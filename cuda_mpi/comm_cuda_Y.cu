/*
comm_cuda_Y.cu (CUDA + MPI)
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
	const int irange = p->iMax - p->iMin + 1;
	const int64_t m = (k - p->kMin) * irange + (i - p->iMin);
	const int64_t n = (p->Ni * i) + (p->Nj * j) + (p->Nk * k) + p->N0;
	buf[m] = v[n];
}
__global__
static void d2h_gpu(int j, real_t *v, real_t *buf, int k0, int k1, int i0, int i1)
{
	const int k = k0 + threadIdx.x + (blockIdx.x * blockDim.x);
	const int i = i0 + threadIdx.y + (blockIdx.y * blockDim.y);
	if ((k <= k1) &&
	    (i <= i1)) {
		_d2h(i, j, k, v, buf, &d_Param);
	}
}
static void d2h_cpu(int j, real_t *v, real_t *buf, int k0, int k1, int i0, int i1)
{
	for (int k = k0; k <= k1; k++) {
	for (int i = i0; i <= i1; i++) {
		_d2h(i, j, k, v, buf, &h_Param);
	}
	}
}
static void d2h(int j, int k0, int k1, int i0, int i1)
{
	if (GPU) {
		// parameter
		cudaMemcpyToSymbol(d_Param, &h_Param, sizeof(param_t));

		// grid
		dim3 grid(CEIL(k1 - k0 + 1, bufBlock.x),
		          CEIL(i1 - i0 + 1, bufBlock.y));

		// device
		d2h_gpu<<<grid, bufBlock>>>(j, d_V, d_SendBuf_y, k0, k1, i0, i1);

		// device to host
		const size_t size = (k1 - k0 + 1) * (i1 - i0 + 1) * sizeof(real_t);
		cuda_memcpy(GPU, SendBuf_y, d_SendBuf_y, size, cudaMemcpyDeviceToHost);

		if (UM) cudaDeviceSynchronize();
	}
	else {
		d2h_cpu(j, V, SendBuf_y, k0, k1, i0, i1);
	}
}


// host to device
__host__ __device__
static void _h2d(int i, int j, int k, real_t *v, real_t *buf, param_t *p)
{
	const int irange = p->iMax - p->iMin + 1;
	const int64_t m = (k - p->kMin) * irange + (i - p->iMin);
	const int64_t n = (p->Ni * i) + (p->Nj * j) + (p->Nk * k) + p->N0;
	v[n] = buf[m];
}
__global__
static void h2d_gpu(int j, real_t *v, real_t *buf, int k0, int k1, int i0, int i1)
{
	const int k = k0 + threadIdx.x + (blockIdx.x * blockDim.x);
	const int i = i0 + threadIdx.y + (blockIdx.y * blockDim.y);
	if ((k <= k1) &&
	    (i <= i1)) {
		_h2d(i, j, k, v, buf, &d_Param);
	}
}
static void h2d_cpu(int j, real_t *v, real_t *buf, int k0, int k1, int i0, int i1)
{
	for (int k = k0; k <= k1; k++) {
	for (int i = i0; i <= i1; i++) {
		_h2d(i, j, k, v, buf, &h_Param);
	}
	}
}
static void h2d(int j, int k0, int k1, int i0, int i1)
{
	if (GPU) {
		// parameter
		cudaMemcpyToSymbol(d_Param, &h_Param, sizeof(param_t));

		// grid
		dim3 grid(CEIL(k1 - k0 + 1, bufBlock.x),
		          CEIL(i1 - i0 + 1, bufBlock.y));

		// host to device
		const size_t size = (k1 - k0 + 1) * (i1 - i0 + 1) * sizeof(real_t);
		cuda_memcpy(GPU, d_RecvBuf_y, RecvBuf_y, size, cudaMemcpyHostToDevice);

		// device
		h2d_gpu<<<grid, bufBlock>>>(j, d_V, d_RecvBuf_y, k0, k1, i0, i1);

		if (UM) cudaDeviceSynchronize();
	}
	else {
		h2d_cpu(j, V, RecvBuf_y, k0, k1, i0, i1);
	}
}


void comm_cuda_Y(void)
{
#ifdef _MPI
	MPI_Status status;
	const int tag = 0;
	int by[] = {Ipy > 0, Ipy < Npy - 1};
	int py[] = {Ipy - 1, Ipy + 1};
	int jsend[] = {jMin + 1, jMax - 1};
	int jrecv[] = {jMin - 1, jMax + 1};
	int j;

	for (int side = 0; side < 2; side++) {
		if (by[side]) {
			// device to host
			j = jsend[side];
			d2h(j, kMin, kMax, iMin, iMax);

			// MPI
			const int ipy = py[side];
			const int dst = (Ipx * Npy * Npz) + (ipy * Npz) + Ipz;
			const int count = (kMax - kMin + 1) * (iMax - iMin + 1);
			MPI_Sendrecv(SendBuf_y, count, MPI_REAL_T, dst, tag,
			             RecvBuf_y, count, MPI_REAL_T, dst, tag, MPI_COMM_WORLD, &status);

			// host to device
			j = jrecv[side];
			h2d(j, kMin, kMax, iMin, iMax);
		}
	}
#endif
}
