/*
comm_cuda_X.cu (CUDA + MPI)
*/

#ifdef _MPI
#include <mpi.h>
#endif

#include "ost.h"
#include "ost_cuda.h"
#include "ost_prototype.h"

// device to host
__host__ __device__
static void _d2h(int i, int j, int k, real_t *v, real_t *buf, param_t *p)
{
	const int krange = p->kMax - p->kMin + 1;
	const int64_t m = (j - p->jMin) * krange + (k - p->kMin);
	const int64_t n = (p->Ni * i) + (p->Nj * j) + (p->Nk * k) + p->N0;
	buf[m] = v[n];
}
__global__
static void d2h_gpu(int i, real_t *v, real_t *buf, int j0, int j1, int k0, int k1)
{
	const int j = j0 + threadIdx.x + (blockIdx.x * blockDim.x);
	const int k = k0 + threadIdx.y + (blockIdx.y * blockDim.y);
	if ((j <= j1) &&
	    (k <= k1)) {
		_d2h(i, j, k, v, buf, &d_Param);
	}
}
static void d2h_cpu(int i, real_t *v, real_t *buf, int j0, int j1, int k0, int k1)
{
	for (int j = j0; j <= j1; j++) {
	for (int k = k0; k <= k1; k++) {
		_d2h(i, j, k, v, buf, &h_Param);
	}
	}
}
static void d2h(int i, int j0, int j1, int k0, int k1)
{
	if (GPU) {
		// parameter
		cudaMemcpyToSymbol(d_Param, &h_Param, sizeof(param_t));

		// grid
		dim3 grid(CEIL(j1 - j0 + 1, bufBlock.x),
		          CEIL(k1 - k0 + 1, bufBlock.y));

		// device
		d2h_gpu<<<grid, bufBlock>>>(i, d_V, d_SendBuf_x, j0, j1, k0, k1);

		// device to host
		const size_t size = (j1 - j0 + 1) * (k1 - k0 + 1) * sizeof(real_t);
		cuda_memcpy(GPU, SendBuf_x, d_SendBuf_x, size, cudaMemcpyDeviceToHost);

		if (UM) cudaDeviceSynchronize();
	}
	else {
		d2h_cpu(i, V, SendBuf_x, j0, j1, k0, k1);
	}
}


// host to device
__host__ __device__
static void _h2d(int i, int j, int k, real_t *v, real_t *buf, param_t *p)
{
	const int krange = p->kMax - p->kMin + 1;
	const int64_t m = (j - p->jMin) * krange + (k - p->kMin);
	const int64_t n = (p->Ni * i) + (p->Nj * j) + (p->Nk * k) + p->N0;
	v[n] = buf[m];
}
__global__
static void h2d_gpu(int i, real_t *v, real_t *buf, int j0, int j1, int k0, int k1)
{
	const int j = j0 + threadIdx.x + (blockIdx.x * blockDim.x);
	const int k = k0 + threadIdx.y + (blockIdx.y * blockDim.y);
	if ((j <= j1) &&
	    (k <= k1)) {
		_h2d(i, j, k, v, buf, &d_Param);
	}
}
static void h2d_cpu(int i, real_t *v, real_t *buf, int j0, int j1, int k0, int k1)
{
	for (int j = j0; j <= j1; j++) {
	for (int k = k0; k <= k1; k++) {
		_h2d(i, j, k, v, buf, &h_Param);
	}
	}
}
static void h2d(int i, int j0, int j1, int k0, int k1)
{
	if (GPU) {
		// parameter
		cudaMemcpyToSymbol(d_Param, &h_Param, sizeof(param_t));

		// grid
		dim3 grid(CEIL(j1 - j0 + 1, bufBlock.x),
		          CEIL(k1 - k0 + 1, bufBlock.y));

		// host to device
		const size_t size = (j1 - j0 + 1) * (k1 - k0 + 1) * sizeof(real_t);
		cuda_memcpy(GPU, d_RecvBuf_x, RecvBuf_x, size, cudaMemcpyHostToDevice);

		// device
		h2d_gpu<<<grid, bufBlock>>>(i, d_V, d_RecvBuf_x, j0, j1, k0, k1);

		if (UM) cudaDeviceSynchronize();
	}
	else {
		h2d_cpu(i, V, RecvBuf_x, j0, j1, k0, k1);
	}
}


void comm_cuda_X(void)
{
#ifdef _MPI
	MPI_Status status;
	const int tag = 0;
	int bx[] = {Ipx > 0, Ipx < Npx - 1};
	int px[] = {Ipx - 1, Ipx + 1};
	int isend[] = {iMin + 1, iMax - 1};
	int irecv[] = {iMin - 1, iMax + 1};
	int i;

	for (int side = 0; side < 2; side++) {
		if (bx[side]) {
			// device to host
			i = isend[side];
			d2h(i, jMin, jMax, kMin, kMax);

			// MPI
			const int ipx = px[side];
			const int dst = (ipx * Npy * Npz) + (Ipy * Npz) + Ipz;
			const int count = (jMax - jMin + 1) * (kMax - kMin + 1);
			MPI_Sendrecv(SendBuf_x, count, MPI_REAL_T, dst, tag,
			             RecvBuf_x, count, MPI_REAL_T, dst, tag, MPI_COMM_WORLD, &status);

			// host to device
			i = irecv[side];
			h2d(i, jMin, jMax, kMin, kMax);
		}
	}
#endif
}
