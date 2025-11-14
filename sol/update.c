/*
update.c
*/

#include "ost.h"
#include "ost_prototype.h"

// no-vector
real_t update_no_vector(int oe)
{
	const real_t omega = (real_t)Solver.omega;

	real_t res2 = 0;
	int i;
#ifdef _OPENMP
#pragma omp parallel for reduction (+: res2)
#endif
	for (    i = iMin; i <= iMax; i++) {
	for (int j = jMin; j <= jMax; j++) {
	for (int k = kMin; k <= kMax; k++) {
		const int64_t n = D(i, j, k);
		if (((i + j + k) % 2 == oe) && (idVolt[n] == 0)) {
			const real_t e = Epsr[idEpsr[n]];

			const real_t axp = (e + Epsr[idEpsr[n + Ni]]) * RXp[i];
			const real_t axm = (e + Epsr[idEpsr[n - Ni]]) * RXm[i];
			const real_t ayp = (e + Epsr[idEpsr[n + Nj]]) * RYp[j];
			const real_t aym = (e + Epsr[idEpsr[n - Nj]]) * RYm[j];
			const real_t azp = (e + Epsr[idEpsr[n + Nk]]) * RZp[k];
			const real_t azm = (e + Epsr[idEpsr[n - Nk]]) * RZm[k];
			const real_t asum = axp + axm + ayp + aym + azp + azm;

			const real_t res = omega * (
				((axp * V[n + Ni]) + (axm * V[n - Ni]) +
				 (ayp * V[n + Nj]) + (aym * V[n - Nj]) +
				 (azp * V[n + Nk]) + (azm * V[n - Nk])) / asum - V[n]);

			V[n] += res;
			if (((i == 0) || (i > iMin)) &&
			    ((j == 0) || (j > jMin)) &&
			    ((k == 0) || (k > kMin))) {  // MPI
				res2 += res * res;
			}
		}
	}
	}
	}

	return res2;
}


// vector
real_t update_vector(int oe)
{
	const real_t omega = (real_t)Solver.omega;

	real_t res2 = 0;
	int i;
#ifdef _OPENMP
#pragma omp parallel for reduction (+: res2)
#endif
	for (    i = iMin; i <= iMax; i++) {
	for (int j = jMin; j <= jMax; j++) {
	for (int k = kMin; k <= kMax; k++) {
		const int64_t n = D(i, j, k);
		if (((i + j + k) % 2 == oe) && (idVolt[n] == 0)) {
			const real_t e = Epsr_v[n];

			const real_t axp = (e + Epsr_v[n + Ni]) * RXp[i];
			const real_t axm = (e + Epsr_v[n - Ni]) * RXm[i];
			const real_t ayp = (e + Epsr_v[n + Nj]) * RYp[j];
			const real_t aym = (e + Epsr_v[n - Nj]) * RYm[j];
			const real_t azp = (e + Epsr_v[n + Nk]) * RZp[k];
			const real_t azm = (e + Epsr_v[n - Nk]) * RZm[k];
			const real_t asum = axp + axm + ayp + aym + azp + azm;

			const real_t res = omega * (
				((axp * V[n + Ni]) + (axm * V[n - Ni]) +
				 (ayp * V[n + Nj]) + (aym * V[n - Nj]) +
				 (azp * V[n + Nk]) + (azm * V[n - Nk])) / asum - V[n]);

			V[n] += res;
			if (((i == 0) || (i > iMin)) &&
			    ((j == 0) || (j > jMin)) &&
			    ((k == 0) || (k > kMin))) {  // MPI
				res2 += res * res;
			}
		}
	}
	}
	}

	return res2;
}
