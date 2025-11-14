/*
makeL1d.c

make 1d data
*/

#include "ost.h"
#include "ost_prototype.h"
#include "vedq.h"

static void setup_1d(void);

void makeL1d(void)
{
	if (NL1d < 1) return;
	const int ncompo = 10;
	const int length = MAX(Nx + 1, MAX(Ny + 1, Nz + 1));

	// setup
	setup_1d();

	// alloc
	F1d = (double ***)malloc(NL1d * sizeof(double **));
	for (int n = 0; n < NL1d; n++) {
		F1d[n] = (double **)malloc(ncompo * sizeof(double *));
		for (int ic = 0; ic < ncompo; ic++) {
			F1d[n][ic] = (double *)malloc(length * sizeof(double));
			memset(F1d[n][ic], 0, length * sizeof(double));
		}
	}

	// make data
	double *f = (double *)malloc(ncompo * sizeof(double));
	for (int n = 0; n < NL1d; n++) {
		char dir = L1d[n].direction;
		//int idata1 = (dir == 'X') ? imin : (dir == 'Y') ? jmin : kmin;
		//int idata2 = (dir == 'X') ? imax : (dir == 'Y') ? jmax : kmax;
		//for (int idata = idata1; idata <= idata2; idata++) {
		int ndata = (dir == 'X') ? Nx : (dir == 'Y') ? Ny : Nz;
		for (int idata = 0; idata <= ndata; idata++) {
			int i = (dir == 'X') ? idata : (dir == 'Y') ? L1d[n].posid[1] : L1d[n].posid[0];
			int j = (dir == 'Y') ? idata : (dir == 'Z') ? L1d[n].posid[1] : L1d[n].posid[0];
			int k = (dir == 'Z') ? idata : (dir == 'X') ? L1d[n].posid[1] : L1d[n].posid[0];
			// V/E/D/Q
			vedq(i, j, k, f);
			for (int ic = 0; ic < ncompo; ic++) {
				F1d[n][ic][idata] = f[ic];
			}
		}
	}
	free(f);
}


// 1d index
static void setup_1d(void)
{
	for (int n = 0; n < NL1d; n++) {
		const double p0 = L1d[n].position[0];
		const double p1 = L1d[n].position[1];
		if      (L1d[n].direction == 'X') {
			L1d[n].posid[0] = nearest(p0, 0, Ny, Yn);
			L1d[n].posid[1] = nearest(p1, 0, Nz, Zn);
		}
		else if (L1d[n].direction == 'Y') {
			L1d[n].posid[0] = nearest(p0, 0, Nz, Zn);
			L1d[n].posid[1] = nearest(p1, 0, Nx, Xn);
		}
		else if (L1d[n].direction == 'Z') {
			L1d[n].posid[0] = nearest(p0, 0, Nx, Xn);
			L1d[n].posid[1] = nearest(p1, 0, Ny, Yn);
		}
		//printf("%d %c %c %f %d %f %d\n", n, L1d[n].component, L1d[n].direction, L1d[n].position[0], L1d[n].posid[0], L1d[n].position[1], L1d[n].posid[1]);
	}
}
