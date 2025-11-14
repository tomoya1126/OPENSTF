/*
solve.c (MPI)

SOR method
*/

#include "ost.h"
#include "ost_prototype.h"

void solve(int vector, FILE *fp)
{
	char str[BUFSIZ];
	size_t size;
	int converged = 0;

	// setup (MPI)
	setup_mpi();

	// alloc V
	size = NN * sizeof(real_t);
	V = (real_t *)malloc(size);
	memset(V, 0, size);

	// alloc (vector)
	if (vector) {
		Epsr_v = (real_t *)malloc(size);
		for (int64_t n = 0; n < NN; n++) {
			Epsr_v[n] = Epsr[idEpsr[n]];
		}
	}

	// alloc residual
	size = (Solver.maxiter + 1) * sizeof(double);
	Residual = (double *)malloc(size);
	memset(Residual, 0, size);

	// electrode
	electrode();

	// get scale
	real_t vmin, vmax;
	getscale(&vmin, &vmax);

	// scaling
	scaling(vmin, vmax);

	// iteration
	int iter;
	for (iter = 0; iter <= Solver.maxiter; iter++) {
		// update
		real_t res2 = 0;
		for (int oe = 0; oe < 2; oe++) {
			if (vector) {
				res2 += update_vector(oe);
			}
			else {
				res2 += update_no_vector(oe);
			}

			// share boundary (MPI)
			if (Npx > 1) {
				comm_X();
			}
			if (Npy > 1) {
				comm_Y();
			}
			if (Npz > 1) {
				comm_Z();
			}
		}

		// residual
		if (commSize > 1) {
			res2 = comm_sum(res2);
		}
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

	// final
	rescaling(vmin, vmax);

	// edge
	edge();

	// free
	if (vector) {
		free(Epsr_v);
	}
}
