/*
vedq.h

V/E/D/Q
*/

static inline void vedq(int i, int j, int k, double f[])
{
	if ((i < 0) || (Nx < i) || (j < 0) || (Ny < j) || (k < 0) || (Nz < k)) {
		return;
	}

	const int ip = (i < Nx) ? (i + 1) : i;
	const int im = (i > 0 ) ? (i - 1) : i;
	const int jp = (j < Ny) ? (j + 1) : j;
	const int jm = (j > 0 ) ? (j - 1) : j;
	const int kp = (k < Nz) ? (k + 1) : k;
	const int km = (k > 0 ) ? (k - 1) : k;

	const int64_t n   = D(i,  j,  k );
	const int64_t nxp = D(ip, j,  k );
	const int64_t nxm = D(im, j,  k );
	const int64_t nyp = D(i,  jp, k );
	const int64_t nym = D(i,  jm, k );
	const int64_t nzp = D(i,  j,  kp);
	const int64_t nzm = D(i,  j,  km);

	const double v = V[n];

	// V [V}
	f[0] = v;

	// E [V/m]
	f[2] = (Nx > 2) ? -(V[nxp] - V[nxm]) / (Xn[ip] - Xn[im]) : 0;
	f[3] = (Ny > 2) ? -(V[nyp] - V[nym]) / (Yn[jp] - Yn[jm]) : 0;
	f[4] = (Nz > 2) ? -(V[nzp] - V[nzm]) / (Zn[kp] - Zn[km]) : 0;
	f[1] = sqrt((f[2] * f[2]) + (f[3] * f[3]) + (f[4] * f[4]));

	// D [C/m^2]
	const double epsr = Epsr[idEpsr[n]];
	for (int m = 5; m <= 8; m++) {
		f[m] = epsr * EPS0 * f[m - 4];
	}

	// Q [C/m^3]
	if (idVolt[n]) {
		f[9] = EPS0 * (
			(v - V[nxp]) * (epsr + Epsr[idEpsr[nxp]]) / 2 * RXp[i] +
			(v - V[nxm]) * (epsr + Epsr[idEpsr[nxm]]) / 2 * RXm[i] +
			(v - V[nyp]) * (epsr + Epsr[idEpsr[nyp]]) / 2 * RYp[j] +
			(v - V[nym]) * (epsr + Epsr[idEpsr[nym]]) / 2 * RYm[j] +
			(v - V[nzp]) * (epsr + Epsr[idEpsr[nzp]]) / 2 * RZp[k] +
			(v - V[nzm]) * (epsr + Epsr[idEpsr[nzm]]) / 2 * RZm[k]);
	}
	else {
		f[9] = 0;
	}
}
