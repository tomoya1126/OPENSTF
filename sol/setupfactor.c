/*
setupfactor.c

setup factors
*/

#include "ost.h"

void setupfactor(void)
{
	RXp = (real_t *)malloc((Nx + 1) * sizeof(real_t));
	RXm = (real_t *)malloc((Nx + 1) * sizeof(real_t));

	RYp = (real_t *)malloc((Ny + 1) * sizeof(real_t));
	RYm = (real_t *)malloc((Ny + 1) * sizeof(real_t));

	RZp = (real_t *)malloc((Nz + 1) * sizeof(real_t));
	RZm = (real_t *)malloc((Nz + 1) * sizeof(real_t));

	for (int i = 1; i < Nx; i++) {
		RXp[i] = (real_t)(1 / (Xn[i + 1] - Xn[i + 0]) * 2 / (Xn[i + 1] - Xn[i - 1]));
		RXm[i] = (real_t)(1 / (Xn[i + 0] - Xn[i - 1]) * 2 / (Xn[i + 1] - Xn[i - 1]));
	}
	for (int j = 1; j < Ny; j++) {
		RYp[j] = (real_t)(1 / (Yn[j + 1] - Yn[j + 0]) * 2 / (Yn[j + 1] - Yn[j - 1]));
		RYm[j] = (real_t)(1 / (Yn[j + 0] - Yn[j - 1]) * 2 / (Yn[j + 1] - Yn[j - 1]));
	}
	for (int k = 1; k < Nz; k++) {
		RZp[k] = (real_t)(1 / (Zn[k + 1] - Zn[k + 0]) * 2 / (Zn[k + 1] - Zn[k - 1]));
		RZm[k] = (real_t)(1 / (Zn[k + 0] - Zn[k - 1]) * 2 / (Zn[k + 1] - Zn[k - 1]));
	}

	RXp[ 0] = RXp[     1];
	RYp[ 0] = RYp[     1];
	RZp[ 0] = RZp[     1];

	RXm[Nx] = RXm[Nx - 1];
	RYm[Ny] = RYm[Ny - 1];
	RZm[Nz] = RZm[Nz - 1];

	// cf. Neumann BC
	RXm[ 0] =
	RYm[ 0] =
	RZm[ 0] =
	RXp[Nx] =
	RYp[Ny] =
	RZp[Nz] = 0;

	// 2D
	if (Nx < 3) {
		for (int i = 0; i <= Nx; i++) {
			RXp[i] = RXm[i] = 0;
		}
	}
	if (Ny < 3) {
		for (int j = 0; j <= Ny; j++) {
			RYp[j] = RYm[j] = 0;
		}
	}
	if (Nz < 3) {
		for (int k = 0; k <= Nz; k++) {
			RZp[k] = RZm[k] = 0;
		}
	}
/*
	for (int i = 0; i <= Nx; i++) printf("X %d %f %f\n", i, RXp[i], RXm[i]);
	for (int j = 0; j <= Ny; j++) printf("Y %d %f %f\n", j, RYp[j], RYm[j]);
	for (int k = 0; k <= Nz; k++) printf("Z %d %f %f\n", k, RZp[k], RZm[k]);
*/
}
