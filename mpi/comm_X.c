/*
comm_X.c
*/

#ifdef _MPI
#include <mpi.h>
#endif

#include "ost.h"

// V to buffer
static void v_to_buffer(int i, real_t v[], real_t buf[], int j0, int j1, int k0, int k1)
{
	for (int j = j0; j <= j1; j++) {
	for (int k = k0; k <= k1; k++) {
		const int64_t m = (j - j0) * (k1 - k0 + 1) + (k - k0);
		buf[m] = v[D(i, j, k)];
	}
	}
}


// buffer to V
static void buffer_to_v(int i, real_t v[], real_t buf[], int j0, int j1, int k0, int k1)
{
	for (int j = j0; j <= j1; j++) {
	for (int k = k0; k <= k1; k++) {
		const int64_t m = (j - j0) * (k1 - k0 + 1) + (k - k0);
		v[D(i, j, k)] = buf[m];
	}
	}
}


void comm_X(void)
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
			// V to buffer
			i = isend[side];
			v_to_buffer(i, V, SendBuf_x, jMin, jMax, kMin, kMax);

			// MPI
			const int ipx = px[side];
			const int dst = (ipx * Npy * Npz) + (Ipy * Npz) + Ipz;
			const int count = (jMax - jMin + 1) * (kMax - kMin + 1);
			MPI_Sendrecv(SendBuf_x, count, MPI_REAL_T, dst, tag,
			             RecvBuf_x, count, MPI_REAL_T, dst, tag, MPI_COMM_WORLD, &status);

			// buffer to V
			i = irecv[side];
			buffer_to_v(i, V, RecvBuf_x, jMin, jMax, kMin, kMax);
		}
	}
#endif
}
