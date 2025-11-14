/*
setupsize.c
*/

#include "ost.h"

static void idminmax(int n, int _np, int np, int ip, int *min, int *max)
{
	if (_np == 1) {
		*min = 0;
		*max = n;
	}
	else {
		// MPI
		const int nc = MAX(n / np, 1);
		*min = (ip + 0) * nc;
		*max = (ip + 1) * nc;
		if (ip == np - 1) {
			*max = n;
		}
	}
}


void setupsize(int npx, int npy, int npz, int comm_rank)
{
	// too many prosess (MPI)
	if ((npx > Nx) || (npy > Ny) || (npz > Nz)) {
		if (comm_rank == 0) {
			fprintf(stderr, "*** too many processes = %dx%dx%d (limit = %dx%dx%d)\n", npx, npy, npz, Nx, Ny, Nz);
			fflush(stderr);
		}
	}

	// get block numbers : (Ipx, Ipy, Ipz) (MPI)
	int ip = 0;
	for (int i = 0; i < npx; i++) {
	for (int j = 0; j < npy; j++) {
	for (int k = 0; k < npz; k++) {
		if (comm_rank == ip) {
			Ipx = i;
			Ipy = j;
			Ipz = k;
		}
		ip++;
	}
	}
	}
	//printf("%d %d %d %d\n", comm_rank, Ipx, Ipy, Ipz); fflush(stdout);
	//assert(comm_rank == (Ipx * npy * npz) + (Ipy * npz) + Ipz);

	// min, max
	idminmax(Nx, npx, Npx, Ipx, &iMin, &iMax);
	idminmax(Ny, npy, Npy, Ipy, &jMin, &jMax);
	idminmax(Nz, npz, Npz, Ipz, &kMin, &kMax);
/*
	// X region
	if (npx == 1) {
		iMin = 0;
		iMax = Nx;
	}
	else {
		// MPI
		const int nx = MAX(Nx / Npx, 1);
		iMin = (Ipx + 0) * nx;
		iMax = (Ipx + 1) * nx;
		if (Ipx == Npx - 1) {
			iMax = Nx;
		}
	}

	// Y region
	if (npy == 1) {
		jMin = 0;
		jMax = Ny;
	}
	else {
		// MPI
		const int ny = MAX(Ny / Npy, 1);
		jMin = (Ipy + 0) * ny;
		jMax = (Ipy + 1) * ny;
		if (Ipy == Npy - 1) {
			jMax = Ny;
		}
	}

	// Z region
	if (npz == 1) {
		kMin = 0;
		kMax = Nz;
	}
	else {
		// MPI
		const int nz = MAX(Nz / Npz, 1);
		kMin = (Ipz + 0) * nz;
		kMax = (Ipz + 1) * nz;
		if (Ipz == Npz - 1) {
			kMax = Nz;
		}
	}
*/
	//printf("%d %d %d %d %d %d %d\n", comm_rank, iMin, iMax, jMin, jMax, kMin, kMax);

	Nk = 1;
	Nj = (kMax - kMin + 3);
	Ni = (jMax - jMin + 3) * Nj;
	N0 = -((iMin - 1) * Ni + (jMin - 1) * Nj + (kMin - 1) * Nk);
	NN = Ni * (iMax + 1) + Nj * (jMax + 1) + Nk * (kMax + 1) + N0 + 1;
	//printf("%d %d %d %d %d %zd\n", commRank, Ni, Nj, Nk, N0, NN); fflush(stdout);

	//assert((Ni * (iMin - 1)) + (Nj * (jMin - 1)) + (Nk * (kMin - 1)) + N0 == 0);
	//assert((Ni * (iMax + 1)) + (Nj * (jMax + 1)) + (Nk * (kMax + 1)) + N0 == NN - 1);
	assert(D(iMin - 1, jMin - 1, kMin - 1) == 0);
	assert(D(iMax + 1, jMax + 1, kMax + 1) == NN - 1);
}
