/*
comm_cuda_Z.cu (CUDA + MPI)
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
	const int jrange = p->jMax - p->jMin + 1;
	const int64_t m = (i - p->iMin) * jrange + (j - p->jMin);
	const int64_t n = (p->Ni * i) + (p->Nj * j) + (p->Nk * k) + p->N0;
	buf[m] = v[n];
}
__global__
static void d2h_gpu(int k, real_t *v, real_t *buf, int i0, int i1, int j0, int j1)
{
	const int i = i0 + threadIdx.x + (blockIdx.x * blockDim.x);
	const int j = j0 + threadIdx.y + (blockIdx.y * blockDim.y);
	if ((i <= i1) &&
	    (j <= j1)) {
		_d2h(i, j, k, v, buf, &d_Param);
	}
}
static void d2h_cpu(int k, real_t *v, real_t *buf, int i0, int i1, int j0, int j1)
{
	for (int i = i0; i <= i1; i++) {
	for (int j = j0; j <= j1; j++) {
		_d2h(i, j, k, v, buf, &h_Param);
	}
	}
}
static void d2h(int k, int i0, int i1, int j0, int j1)
{
	if (GPU) {
		// parameter
		cudaMemcpyToSymbol(d_Param, &h_Param, sizeof(param_t));

		// grid
		dim3 grid(CEIL(i1 - i0 + 1, bufBlock.x),
		          CEIL(j1 - j0 + 1, bufBlock.y));

		// device
		d2h_gpu<<<grid, bufBlock>>>(k, d_V, d_SendBuf_z, i0, i1, j0, j1);

		// device to host
		const size_t size = (i1 - i0 + 1) * (j1 - j0 + 1) * sizeof(real_t);
		cuda_memcpy(GPU, SendBuf_z, d_SendBuf_z, size, cudaMemcpyDeviceToHost);

		if (UM) cudaDeviceSynchronize();
	}
	else {
		d2h_cpu(k, V, SendBuf_z, i0, i1, j0, j1);
	}
}


// host to device
__host__ __device__
static void _h2d(int i, int j, int k, real_t *v, real_t *buf, param_t *p)
{
	const int jrange = p->jMax - p->jMin + 1;
	const int64_t m = (i - p->iMin) * jrange + (j - p->jMin);
	const int64_t n = (p->Ni * i) + (p->Nj * j) + (p->Nk * k) + p->N0;
	v[n] = buf[m];
}
__global__
static void h2d_gpu(int k, real_t *v, real_t *buf, int i0, int i1, int j0, int j1)
{
	const int i = i0 + threadIdx.x + (blockIdx.x * blockDim.x);
	const int j = j0 + threadIdx.y + (blockIdx.y * blockDim.y);
	if ((i <= i1) &&
	    (j <= j1)) {
		_h2d(i, j, k, v, buf, &d_Param);
	}
}
static void h2d_cpu(int k, real_t *v, real_t *buf, int i0, int i1, int j0, int j1)
{
	for (int i = i0; i <= i1; i++) {
	for (int j = j0; j <= j1; j++) {
		_h2d(i, j, k, v, buf, &h_Param);
	}
	}
}
static void h2d(int k, int i0, int i1, int j0, int j1)
{
	if (GPU) {
		// parameter
		cudaMemcpyToSymbol(d_Param, &h_Param, sizeof(param_t));

		// grid
		dim3 grid(CEIL(i1 - i0 + 1, bufBlock.x),
		          CEIL(j1 - j0 + 1, bufBlock.y));

		// host to device
		const size_t size = (i1 - i0 + 1) * (j1 - j0 + 1) * sizeof(real_t);
		cuda_memcpy(GPU, d_RecvBuf_z, RecvBuf_z, size, cudaMemcpyHostToDevice);

		// device
		h2d_gpu<<<grid, bufBlock>>>(k, d_V, d_RecvBuf_z, i0, i1, j0, j1);

		if (UM) cudaDeviceSynchronize();
	}
	else {
		h2d_cpu(k, V, RecvBuf_z, i0, i1, j0, j1);
	}
}


void comm_cuda_Z(void)
{
#ifdef _MPI
	MPI_Status status;
	const int tag = 0;
	int bz[] = {Ipz > 0, Ipz < Npz - 1};
	int pz[] = {Ipz - 1, Ipz + 1};
	int ksend[] = {kMin + 1, kMax - 1};
	int krecv[] = {kMin - 1, kMax + 1};
	int k;

	for (int side = 0; side < 2; side++) {
		if (bz[side]) {
			// device to host
			k = ksend[side];
			d2h(k, iMin, iMax, jMin, jMax);

			// MPI
			const int ipz = pz[side];
			const int dst = (Ipx * Npy * Npz) + (Ipy * Npz) + ipz;
			const int count = (iMax - iMin + 1) * (jMax - jMin + 1);
			MPI_Sendrecv(SendBuf_z, count, MPI_REAL_T, dst, tag,
			             RecvBuf_z, count, MPI_REAL_T, dst, tag, MPI_COMM_WORLD, &status);

			// host to device
			k = krecv[side];
			h2d(k, iMin, iMax, jMin, jMax);
		}
	}
#endif
}
