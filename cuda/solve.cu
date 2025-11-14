/*
solve.cu (CUDA)

SOR method (red-black)
*/

#include "ost.h"
#include "ost_cuda.h"
#include "ost_prototype.h"
#include "update.cuh"

void solve(int vector, FILE *fp)
{
	char str[BUFSIZ];
	int converged = 0;
	real_t omega = (real_t)Solver.omega;

	// setup GPU
	setup_gpu();

	// alloc V
	const size_t size = NN * sizeof(real_t);
	V = (real_t *)malloc(size);
	memset(V, 0, size);

	// alloc (vector)
	if (vector) {
		Epsr_v = (real_t *)malloc(size);
		for (int n = 0; n < NN; n++) {
			Epsr_v[n] = Epsr[idEpsr[n]];
		}
		if (GPU) {
			cuda_malloc(GPU, UM, (void **)&d_Epsr_v, size);
			cuda_memcpy(GPU, d_Epsr_v, Epsr_v, size, cudaMemcpyHostToDevice);
		}
	}

	// alloc residual
	const size_t r_size = (Solver.maxiter + 1) * sizeof(double);
	Residual = (double *)malloc(r_size);
	memset(Residual, 0, r_size);

	// electrode
	electrode();

	// get scale
	real_t vmin, vmax;
	getscale(&vmin, &vmax);

	// scaling
	scaling(vmin, vmax);

	// alloc device memory
	if (GPU) {
		memory_alloc_gpu();
	}

	// grid
	dim3 grid = dim3(CEIL(Nz + 1, updateBlock.x),
	                 CEIL(Ny + 1, updateBlock.y),
	                 CEIL(Nx + 1, updateBlock.z));

	// residual array
	size_t r2_size = 0;
	real_t *d_res2 = NULL, *h_res2 = NULL;
	if (GPU) {
		r2_size = grid.x * grid.y * grid.z * sizeof(real_t);
		cuda_malloc(GPU, UM, (void **)&d_res2, r2_size);
		h_res2 = (real_t *)malloc(r2_size);
		memset(h_res2, 0, r2_size);
	}

	// iteration
	int iter;
	for (iter = 0; iter <= Solver.maxiter; iter++) {
		// update
		real_t res2 = 0;
		for (int oe = 0; oe < 2; oe++) {
			if (GPU) {
				// GPU
				cudaMemcpyToSymbol(d_Param, &h_Param, sizeof(param_t));
				const int sm_size = updateBlock.x * updateBlock.y * sizeof(real_t);
				if (vector) {
					update_vector_gpu<<<grid, updateBlock, sm_size>>>(oe,
						d_RXp, d_RYp, d_RZp, d_RXm, d_RYm, d_RZm,
						d_V, d_idVolt, d_Epsr_v, omega, d_res2);
				}
				else {
					update_no_vector_gpu<<<grid, updateBlock, sm_size>>>(oe,
						d_RXp, d_RYp, d_RZp, d_RXm, d_RYm, d_RZm,
						d_V, d_idVolt, d_idEpsr, d_Epsr, omega, d_res2);
				}
				cudaMemcpy(h_res2, d_res2, r2_size, cudaMemcpyDeviceToHost);
				for (int n = 0; n < r2_size / sizeof(real_t); n++) {
					res2 += h_res2[n];
				}
			}
			else {
				// CPU
				if (vector) {
					res2 += update_vector_cpu(oe,
						RXp, RYp, RZp, RXm, RYm, RZm,
						V, idVolt, Epsr_v, omega);
				}
				else {
					res2 += update_no_vector_cpu(oe,
						RXp, RYp, RZp, RXm, RYm, RZm,
						V, idVolt, idEpsr, Epsr, omega);
				}
			}
		}

		// residual
		Residual[iter] = sqrt(res2 / ((double)(Nx + 1) * (Ny + 1) * (Nz + 1)));

		// monitor and check
		if ((iter % Solver.nout == 0) || (iter == Solver.maxiter)
			|| (Residual[iter] < Solver.converg)) {
			// monitor
			if (fp != NULL) {
				sprintf(str, "   %7d    %.7f", iter, Residual[iter]);
				monitor1(fp, str);
			}

			// check convergence
			if (Residual[iter] < Solver.converg) {
				converged = 1;
				break;
			}
		}
	}

	// monitor result
	if (fp != NULL) {
		sprintf(str, "    --- %s ---",  (converged ? "converged" : "max steps"));
		monitor1(fp, str);
	}

	// iterations
	NumIter = iter + 1;

	// copy and free
	if (GPU) {
		// copy device memory
		memory_copy_gpu();

		// free device memory
		memory_free_gpu();

		// free residual
		cuda_free(GPU, d_res2);
		free(h_res2);

		// free vector array
		if (vector) {
			cuda_free(GPU, d_Epsr_v);
			free(Epsr_v);
		}
	}

	// rescaling
	rescaling(vmin, vmax);

	// edge
	edge();
}
