/*
echar.c

Echar[0] : total electro-static energy [W]
Echar[n] : charge of n-th voltage electrodes [C]
*/

#include "ost.h"
#include "ost_prototype.h"
#include "vedq.h"

void echar(void)
{
	// alloc
	size_t size = NVolt * sizeof(double);
	Echar = (double *)malloc(size);
	memset(Echar, 0, size);

	// number of thread
	int nthread = 1;
#ifdef _OPENMP
#pragma omp parallel
	{
		nthread = omp_get_num_threads();
	}
#endif

	// thread variables
	double **echar = (double **)malloc(nthread * sizeof(double *));
	for (int tid = 0; tid < nthread; tid++) {
		echar[tid] = (double *)malloc(size);
		memset(echar[tid], 0, size);
	}

	// calculation
	double wsum = 0;
#ifdef _OPENMP
#pragma omp parallel
#endif
	{
		int i;
		int tid = 0;
#ifdef _OPENMP
		tid = omp_get_thread_num();
#pragma omp for reduction (+: wsum)
#endif
		for (    i = iMin; i <= iMax; i++) {
		for (int j = jMin; j <= jMax; j++) {
		for (int k = kMin; k <= kMax; k++) {
			if (((i == 0) || (i > iMin)) &&
			    ((j == 0) || (j > jMin)) &&
			    ((k == 0) || (k > kMin))) {  // MPI
				//const double dx = (i == 0) ? (Xn[1] - Xn[0]) / 2 : (i == Nx) ? (Xn[Nx] - Xn[Nx - 1]) / 2 : (Xn[i + 1] - Xn[i - 1]) / 2;
				//const double dy = (j == 0) ? (Yn[1] - Yn[0]) / 2 : (j == Ny) ? (Yn[Ny] - Yn[Ny - 1]) / 2 : (Yn[j + 1] - Yn[j - 1]) / 2;
				//const double dz = (k == 0) ? (Zn[1] - Zn[0]) / 2 : (k == Nz) ? (Zn[Nz] - Zn[Nz - 1]) / 2 : (Zn[k + 1] - Zn[k - 1]) / 2;
				const double dx = (i == 0) ? (Xn[1] - Xn[0]) : (i == Nx) ? (Xn[Nx] - Xn[Nx - 1]) : (Xn[i + 1] - Xn[i - 1]) / 2;
				const double dy = (j == 0) ? (Yn[1] - Yn[0]) : (j == Ny) ? (Yn[Ny] - Yn[Ny - 1]) : (Yn[j + 1] - Yn[j - 1]) / 2;
				const double dz = (k == 0) ? (Zn[1] - Zn[0]) : (k == Nz) ? (Zn[Nz] - Zn[Nz - 1]) : (Zn[k + 1] - Zn[k - 1]) / 2;
				const double v = dx * dy * dz;
				double f[10];
				f[0] = f[1] = f[2] = f[3] = f[4] = f[5] = f[6] = f[7] = f[8] = f[9] = 0;
				vedq(i, j, k, f);
				const int64_t n = D(i, j, k);
				echar[tid][idVolt[n]] += f[9] * v;
				wsum += (f[1] * f[1]) * Epsr[idEpsr[n]] * v;
			}
		}
		}
		}
	}

	// sum over threads
	Echar[0] = 0.5 * EPS0 * wsum;
	for (int n = 1; n < NVolt; n++) {
		for (int tid = 0; tid < nthread; tid++) {
			Echar[n] += echar[tid][n];
		}
	}
}
