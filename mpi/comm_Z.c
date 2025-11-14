/*
comm_Z.c
*/

#ifdef _MPI
#include <mpi.h>
#endif

#include "ost.h"

// V to buffer
static void v_to_buffer(int k, real_t v[], real_t buf[], int i0, int i1, int j0, int j1)
{
	for (int i = i0; i <= i1; i++) {
	for (int j = j0; j <= j1; j++) {
		const int64_t m = (i - i0) * (j1 - j0 + 1) + (j - j0);
		buf[m] = v[D(i, j, k)];
	}
	}
}


// buffer to V
static void buffer_to_v(int k, real_t v[], real_t buf[], int i0, int i1, int j0, int j1)
{
	for (int i = i0; i <= i1; i++) {
	for (int j = j0; j <= j1; j++) {
		const int64_t m = (i - i0) * (j1 - j0 + 1) + (j - j0);
		v[D(i, j, k)] = buf[m];
	}
	}
}


void comm_Z(void)
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
			// V to buffer
			k = ksend[side];
			v_to_buffer(k, V, SendBuf_z, iMin, iMax, jMin, jMax);

			// MPI
			const int ipz = pz[side];
			const int dst = (Ipx * Npy * Npz) + (Ipy * Npz) + ipz;
			const int count = (iMax - iMin + 1) * (jMax - jMin + 1);
			MPI_Sendrecv(SendBuf_z, count, MPI_REAL_T, dst, tag,
			             RecvBuf_z, count, MPI_REAL_T, dst, tag, MPI_COMM_WORLD, &status);

			// buffer to V
			k = krecv[side];
			buffer_to_v(k, V, RecvBuf_z, iMin, iMax, jMin, jMax);
		}
	}
#endif
}
