/*
vmisc.c
*/

#include "ost.h"

void electrode(void)
{
	for (int i = iMin - 1; i <= iMax + 1; i++) {
	for (int j = jMin - 1; j <= jMax + 1; j++) {
	for (int k = kMin - 1; k <= kMax + 1; k++) {
		const int64_t n = D(i, j, k);
		if (idVolt[n]) {
			V[n] = (real_t)Volt[idVolt[n]];
		}
	}
	}
	}
}


void getscale(real_t *vmin, real_t *vmax)
{
	*vmin = +1e10;
	*vmax = -1e10;
	for (int n = 0; n < NGeom; n++) {
		if (Geom[n].type == 1) {
			real_t v = (real_t)Volt[Geom[n].pid];
			*vmin = MIN(*vmin, v);
			*vmax = MAX(*vmax, v);
		}
	}
}


void scaling(real_t vmin, real_t vmax)
{
	const real_t v0 = (vmin + vmax) / 2;
	const real_t f = 2 / (vmax - vmin);

	for (int i = iMin - 1; i <= iMax + 1; i++) {
	for (int j = jMin - 1; j <= jMax + 1; j++) {
	for (int k = kMin - 1; k <= kMax + 1; k++) {
		const int64_t n = D(i, j, k);
		if (idVolt[n]) {
			V[n] = f * (V[n] - v0);
		}
		else {
			V[n] = 0;
		}
	}
	}
	}
}


void rescaling(real_t vmin, real_t vmax)
{
	const real_t v0 = (vmin + vmax) / 2;
	const real_t f = (vmax - vmin) / 2;

	for (int i = iMin - 1; i <= iMax + 1; i++) {
	for (int j = jMin - 1; j <= jMax + 1; j++) {
	for (int k = kMin - 1; k <= kMax + 1; k++) {
		const int64_t n = D(i, j, k);
		V[n] = v0 + (f * V[n]);
	}
	}
	}
}


void edge(void)
{
	for (int i = iMin; i <= iMax; i++) {
	for (int j = jMin; j <= jMax; j++) {
	for (int k = kMin; k <= kMax; k++) {
		const int64_t n = D(i, j, k);
		if (!idVolt[n]) {
			if ((j ==  0) && (k ==  0)) V[n] = V[D(i + 0, j + 1, k + 1)];
			if ((j == Ny) && (k ==  0)) V[n] = V[D(i + 0, j - 1, k + 1)];
			if ((j ==  0) && (k == Nz)) V[n] = V[D(i + 0, j + 1, k - 1)];
			if ((j == Ny) && (k == Nz)) V[n] = V[D(i + 0, j - 1, k - 1)];
			if ((k ==  0) && (i ==  0)) V[n] = V[D(i + 1, j + 0, k + 1)];
			if ((k == Nz) && (i ==  0)) V[n] = V[D(i + 1, j + 0, k - 1)];
			if ((k ==  0) && (i == Nx)) V[n] = V[D(i - 1, j + 0, k + 1)];
			if ((k == Nz) && (i == Nx)) V[n] = V[D(i - 1, j + 0, k - 1)];
			if ((i ==  0) && (j ==  0)) V[n] = V[D(i + 1, j + 1, k + 0)];
			if ((i == Nx) && (j ==  0)) V[n] = V[D(i - 1, j + 1, k + 0)];
			if ((i ==  0) && (j == Ny)) V[n] = V[D(i + 1, j - 1, k + 0)];
			if ((i == Nx) && (j == Ny)) V[n] = V[D(i - 1, j - 1, k + 0)];
		}
	}
	}
	}
}
