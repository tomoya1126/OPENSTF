/*
setup_mpi.c (MPI)
*/

#include "ost.h"

void setup_mpi(void)
{
	size_t size;

	// alloc MPI buffer
	if (Npx > 1) {
		size = (jMax - jMin + 1) * (kMax - kMin + 1) * sizeof(real_t);
		SendBuf_x = (real_t *)malloc(size);
		RecvBuf_x = (real_t *)malloc(size);
	}
	if (Npy > 1) {
		size = (kMax - kMin + 1) * (iMax - iMin + 1) * sizeof(real_t);
		SendBuf_y = (real_t *)malloc(size);
		RecvBuf_y = (real_t *)malloc(size);
	}
	if (Npz > 1) {
		size = (iMax - iMin + 1) * (jMax - jMin + 1) * sizeof(real_t);
		SendBuf_z = (real_t *)malloc(size);
		RecvBuf_z = (real_t *)malloc(size);
	}
}
