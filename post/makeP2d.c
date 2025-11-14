/*
makeP2d.c

make 2d data
*/

#include "ost.h"
#include "ost_prototype.h"
#include "vedq.h"

static void setup_2d(void);

void makeP2d(void)
{
	if (NP2d < 1) return;
	const int ncompo = 10;
	const int length = MAX(Nx + 1, MAX(Ny + 1, Nz + 1));

	// setup
	setup_2d();

	// alloc
	F2d = (double ****)malloc(NP2d * sizeof(double ***));
	for (int n = 0; n < NP2d; n++) {
		F2d[n] = (double ***)malloc(ncompo * sizeof(double **));
		for (int ic = 0; ic < ncompo; ic++) {
			F2d[n][ic] = (double **)malloc(length * sizeof(double *));
			for (int l = 0; l < length; l++) {
				F2d[n][ic][l] = (double *)malloc(length * sizeof(double));
				memset(F2d[n][ic][l], 0, length * sizeof(double));
			}
		}
	}

	// make data
	double *f = (double *)malloc(ncompo * sizeof(double));
	for (int n = 0; n < NP2d; n++) {
		char dir = P2d[n].direction;
		//int idata1 = (dir == 'X') ? jmin : (dir == 'Y') ? imin : imin;
		//int idata2 = (dir == 'X') ? jmax : (dir == 'Y') ? imax : imax;
		//int jdata1 = (dir == 'X') ? kmin : (dir == 'Y') ? kmin : jmin;
		//int jdata2 = (dir == 'X') ? kmax : (dir == 'Y') ? kmax : jmax;
		//for (int idata = idata1; idata <= idata2; idata++) {
		//for (int jdata = jdata1; jdata <= jdata2; jdata++) {
		int nidata = (dir == 'X') ? Ny : (dir == 'Y') ? Nx : Nx;
		int njdata = (dir == 'X') ? Nz : (dir == 'Y') ? Nz : Ny;
		for (int idata = 0; idata <= nidata; idata++) {
		for (int jdata = 0; jdata <= njdata; jdata++) {
			int i = (dir == 'X') ? P2d[n].posid : (dir == 'Y') ? idata        : idata;
			int j = (dir == 'X') ? idata :        (dir == 'Y') ? P2d[n].posid : jdata;
			int k = (dir == 'X') ? jdata :        (dir == 'Y') ? jdata        : P2d[n].posid;
			// V/E/D/Q
			vedq(i, j, k, f);
			for (int ic = 0; ic < ncompo; ic++) {
				F2d[n][ic][idata][jdata] = f[ic];
			}
		}
		}
	}
	free(f);
}


// near2d index
static void setup_2d(void)
{
	for (int n = 0; n < NP2d; n++) {
		const double p = P2d[n].position;
		if      (P2d[n].direction == 'X') {
			P2d[n].posid = nearest(p, 0, Nx, Xn);
		}
		else if (P2d[n].direction == 'Y') {
			P2d[n].posid = nearest(p, 0, Ny, Yn);
		}
		else if (P2d[n].direction == 'Z') {
			P2d[n].posid = nearest(p, 0, Nz, Zn);
		}
		//printf("%d %s %c %f %d\n", n, P2d[n].component, P2d[n].direction, P2d[n].position, P2d[n].posid);
	}
}
