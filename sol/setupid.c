/*
setupid.c

setup ID
*/

#include "ost.h"
#include "ost_prototype.h"

void setupid(void)
{
	const size_t size = NN * sizeof(id_t);
	idVolt = (id_t *)malloc(size);
	idEpsr = (id_t *)malloc(size);
	memset(idVolt, 0, size);
	memset(idEpsr, 0, size);

	const double eps = EPS * (
		fabs(Xn[Nx] - Xn[0]) +
		fabs(Yn[Ny] - Yn[0]) +
		fabs(Zn[Nz] - Zn[0]));

	for (int n = 0; n < NGeom; n++) {
		const int type  = Geom[n].type;
		const id_t pid  = Geom[n].pid;
		const int shape = Geom[n].shape;
		double *g = Geom[n].g;
		if (shape == 1) {
			// rectangle
			int i1, i2, j1, j2, k1, k2;
			// +1 cell
			const int imin = MAX(iMin - 1, 0);
			const int imax = MIN(iMax + 1, Nx);
			const int jmin = MAX(jMin - 1, 0);
			const int jmax = MIN(jMax + 1, Ny);
			const int kmin = MAX(kMin - 1, 0);
			const int kmax = MIN(kMax + 1, Nz);
			get_span(Xn, imin, imax, g[0], g[1], &i1, &i2, eps);
			get_span(Yn, jmin, jmax, g[2], g[3], &j1, &j2, eps);
			get_span(Zn, kmin, kmax, g[4], g[5], &k1, &k2, eps);
			//printf("%d %d %d %d %d %d %d\n", commRank, i1, i2, j1, j2, k1, k2);
			for (int i = i1; i <= i2; i++) {
			for (int j = j1; j <= j2; j++) {
			for (int k = k1; k <= k2; k++) {
				int64_t adr = D(i, j, k);
				idVolt[adr] = (type == 1) ? pid : 0;
				idEpsr[adr] = (type == 1) ? 0 : pid;
			}
			}
			}
		}
		else {
			// not rectangle (+1 cell)
			for (int i = iMin - 1; i <= iMax + 1; i++) {
			for (int j = jMin - 1; j <= jMax + 1; j++) {
			for (int k = kMin - 1; k <= kMax + 1; k++) {
				if (ingeometry(Xn[i], Yn[j], Zn[k], shape, g, eps)) {
					int64_t adr = D(i, j, k);
					idVolt[adr] = (type == 1) ? pid : 0;
					idEpsr[adr] = (type == 1) ? 0 : pid;
				}
			}
			}
			}
		}
	}
/*
	// debug
	for (int i = imin; i <= imax; i++) {
		printf("i=%d\n", i);
		for (int j = jmin; j <= jmax; j++) {
			for (int k = kmin; k <= kmax; k++) {
				int64_t n = D(i - imin, j - jmin, k - kmin);
				int idv = idVolt[n];
				assert((idv >= 0) && (idv < NVolt));
				int ide = idEpsr[n];
				assert((ide >= 0) && (ide < NEpsr));
				printf(" %d", idv);
				//printf(" %d", ide);
				fflush(stdout);
			}
			printf("\n"); fflush(stdout);
		}
		printf("\n"); fflush(stdout);
	}
*/
/*
	// debug (2)
	int isum = 0;
	for (int i = imin; i <= imax; i++) {
		for (int j = jmin; j <= jmax; j++) {
			for (int k = kmin; k <= kmax; k++) {
				int64_t n = D(i - imin, j - jmin, k - kmin);
				if (idVolt[n] > 0) {
					isum++;
				}
			}
		}
	}
	printf("isum = %d\n", isum);
*/
}
