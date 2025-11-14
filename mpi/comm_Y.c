/*
comm_Y.c
*/

#ifdef _MPI
#include <mpi.h>
#endif

#include "ost.h"

// V to buffer
static void v_to_buffer(int j, real_t v[], real_t buf[], int k0, int k1, int i0, int i1)
{
	for (int k = k0; k <= k1; k++) {
	for (int i = i0; i <= i1; i++) {
		const int64_t m = (k - k0) * (i1 - i0 + 1) + (i - i0);
		buf[m] = v[D(i, j, k)];
	}
	}
}


// buffer to V
static void buffer_to_v(int j, real_t v[], real_t buf[], int k0, int k1, int i0, int i1)
{
	for (int k = k0; k <= k1; k++) {
	for (int i = i0; i <= i1; i++) {
		const int64_t m = (k - k0) * (i1 - i0 + 1) + (i - i0);
		v[D(i, j, k)] = buf[m];
	}
	}
}


void comm_Y(void)
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
			// V to buffer
			j = jsend[side];
			v_to_buffer(j, V, SendBuf_y, kMin, kMax, iMin, iMax);

			// MPI
			const int ipy = py[side];
			const int dst = (Ipx * Npy * Npz) + (ipy * Npz) + Ipz;
			const int count = (kMax - kMin + 1) * (iMax - iMin + 1);
			MPI_Sendrecv(SendBuf_y, count, MPI_REAL_T, dst, tag,
			             RecvBuf_y, count, MPI_REAL_T, dst, tag, MPI_COMM_WORLD, &status);

			// buffer to V
			j = jrecv[side];
			buffer_to_v(j, V, RecvBuf_y, kMin, kMax, iMin, iMax);
		}
	}
#endif
}
