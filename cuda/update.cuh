/*
update.cuh (CUDA)
*/

#include "reduction_sum.cuh"

// GPU/CPU (vector)
__host__ __device__
static real_t update_vector(param_t *p,
	int i, int j, int k, int64_t n,
	real_t *rxp, real_t *ryp, real_t *rzp, real_t *rxm, real_t *rym, real_t *rzm,
	real_t *v, real_t *epsr_v, real_t omega)
{
	const int64_t ni = p->Ni;
	const int64_t nj = p->Nj;
	const int64_t nk = p->Nk;
	//const int64_t n0 = p->N0;
	//const int64_t n = (ni * i) + (nj * j) + (nk * k) + n0;

	const real_t e = epsr_v[n];

	const real_t axp = (e + epsr_v[n + ni]) * rxp[i];
	const real_t axm = (e + epsr_v[n - ni]) * rxm[i];
	const real_t ayp = (e + epsr_v[n + nj]) * ryp[j];
	const real_t aym = (e + epsr_v[n - nj]) * rym[j];
	const real_t azp = (e + epsr_v[n + nk]) * rzp[k];
	const real_t azm = (e + epsr_v[n - nk]) * rzm[k];
	const real_t asum = axp + axm + ayp + aym + azp + azm;

	const real_t res = omega * (
		((axp * v[n + ni]) + (axm * v[n - ni]) +
		 (ayp * v[n + nj]) + (aym * v[n - nj]) +
		 (azp * v[n + nk]) + (azm * v[n - nk])) / asum - v[n]);

	v[n] += res;

	return (res * res);
}


// GPU/CPU (no vector)
__host__ __device__
static real_t update_no_vector(param_t *p,
	int i, int j, int k, int64_t n,
	real_t *rxp, real_t *ryp, real_t *rzp, real_t *rxm, real_t *rym, real_t *rzm,
	real_t *v, id_t *idepsr, real_t *epsr, real_t omega)
{
	const int64_t ni = p->Ni;
	const int64_t nj = p->Nj;
	const int64_t nk = p->Nk;
	//const int64_t n0 = p->N0;
	//const int64_t n = (ni * i) + (nj * j) + (nk * k) + n0;

	const real_t e = epsr[idepsr[n]];

	const real_t axp = (e + epsr[idepsr[n + ni]]) * rxp[i];
	const real_t axm = (e + epsr[idepsr[n - ni]]) * rxm[i];
	const real_t ayp = (e + epsr[idepsr[n + nj]]) * ryp[j];
	const real_t aym = (e + epsr[idepsr[n - nj]]) * rym[j];
	const real_t azp = (e + epsr[idepsr[n + nk]]) * rzp[k];
	const real_t azm = (e + epsr[idepsr[n - nk]]) * rzm[k];
	const real_t asum = axp + axm + ayp + aym + azp + azm;

	const real_t res = omega * (
		((axp * v[n + ni]) + (axm * v[n - ni]) +
		 (ayp * v[n + nj]) + (aym * v[n - nj]) +
		 (azp * v[n + nk]) + (azm * v[n - nk])) / asum - v[n]);

	v[n] += res;

	return (res * res);
}


// GPU (vector)
__global__
static void update_vector_gpu(int oe,
	//int imin, int imax, int jmin, int jmax, int kmin, int kmax,
	//int64_t ni, int64_t nj, int64_t nk, int64_t n0,
	real_t *rxp, real_t *ryp, real_t *rzp, real_t *rxm, real_t *rym, real_t *rzm,
	real_t *v, id_t *idvolt, real_t *epsr_v, real_t omega, real_t *d_res2)
{
	extern __shared__ real_t sm[];

	const int i = d_Param.iMin + blockIdx.z;
	const int j = d_Param.jMin + threadIdx.y + (blockIdx.y * blockDim.y);
	const int k = d_Param.kMin + threadIdx.x + (blockIdx.x * blockDim.x);

	const int nthread = blockDim.x * blockDim.y;
	const int tid = threadIdx.x + (threadIdx.y * blockDim.x);
	const int bid = blockIdx.x + (blockIdx.y * gridDim.x) + (blockIdx.z * gridDim.x * gridDim.y);

	real_t res2 = 0;

	if (i <= d_Param.iMax) {
	if (j <= d_Param.jMax) {
	if (k <= d_Param.kMax) {
		const int64_t n = (d_Param.Ni * i) + (d_Param.Nj * j) + (d_Param.Nk * k) + d_Param.N0;
		if (((i + j + k) % 2 == oe) && (idvolt[n] == 0)) {
			res2 = update_vector(&d_Param,
				i, j, k, n,
				rxp, ryp, rzp, rxm, rym, rzm,
				v, epsr_v, omega);
		}
	}
	}
	}
	sm[tid] = res2;

	reduction_sum(tid, nthread, sm, &d_res2[bid]);
}


// GPU (no vector)
__global__
static void update_no_vector_gpu(int oe,
	//int imin, int imax, int jmin, int jmax, int kmin, int kmax,
	//int64_t ni, int64_t nj, int64_t nk, int64_t n0,
	real_t *rxp, real_t *ryp, real_t *rzp, real_t *rxm, real_t *rym, real_t *rzm,
	real_t *v, id_t *idvolt, id_t *idepsr, real_t *epsr, real_t omega, real_t *d_res2)
{
	extern __shared__ real_t sm[];

	const int i = d_Param.iMin + blockIdx.z;
	const int j = d_Param.jMin + threadIdx.y + (blockIdx.y * blockDim.y);
	const int k = d_Param.kMin + threadIdx.x + (blockIdx.x * blockDim.x);

	const int nthread = blockDim.x * blockDim.y;
	const int tid = threadIdx.x + (threadIdx.y * blockDim.x);
	const int bid = blockIdx.x + (blockIdx.y * gridDim.x) + (blockIdx.z * gridDim.x * gridDim.y);

	real_t res2 = 0;

	if (i <= d_Param.iMax) {
	if (j <= d_Param.jMax) {
	if (k <= d_Param.kMax) {
		const int64_t n = (d_Param.Ni * i) + (d_Param.Nj * j) + (d_Param.Nk * k) + d_Param.N0;
		if (((i + j + k) % 2 == oe) && (idvolt[n] == 0)) {
			res2 = update_no_vector(&d_Param,
				i, j, k, n,
				rxp, ryp, rzp, rxm, rym, rzm,
				v, idepsr, epsr, omega);
		}
	}
	}
	}
	sm[tid] = res2;

	reduction_sum(tid, nthread, sm, &d_res2[bid]);
}


// CPU (vector)
static real_t update_vector_cpu(int oe,
	//int imin, int imax, int jmin, int jmax, int kmin, int kmax,
	//int64_t ni, int64_t nj, int64_t nk, int64_t n0,
	real_t *rxp, real_t *ryp, real_t *rzp, real_t *rxm, real_t *rym, real_t *rzm,
	real_t *v, id_t *idvolt, real_t *epsr_v, real_t omega)
{
	real_t res2 = 0;

	for (int i = h_Param.iMin; i <= h_Param.iMax; i++) {
	for (int j = h_Param.jMin; j <= h_Param.jMax; j++) {
	for (int k = h_Param.kMin; k <= h_Param.kMax; k++) {
		const int64_t n = (h_Param.Ni * i) + (h_Param.Nj * j) + (h_Param.Nk * k) + h_Param.N0;
		if (((i + j + k) % 2 == oe) && (idvolt[n] == 0)) {
			res2 += update_vector(&h_Param,
				i, j, k, n,
				rxp, ryp, rzp, rxm, rym, rzm,
				v, epsr_v, omega);
		}
	}
	}
	}

	return res2;
}


// CPU (no vector)
static real_t update_no_vector_cpu(int oe,
	//int imin, int imax, int jmin, int jmax, int kmin, int kmax,
	//int64_t ni, int64_t nj, int64_t nk, int64_t n0,
	real_t *rxp, real_t *ryp, real_t *rzp, real_t *rxm, real_t *rym, real_t *rzm,
	real_t *v, id_t *idvolt, id_t *idepsr, real_t *epsr, real_t omega)
{
	real_t res2 = 0;

	for (int i = h_Param.iMin; i <= h_Param.iMax; i++) {
	for (int j = h_Param.jMin; j <= h_Param.jMax; j++) {
	for (int k = h_Param.kMin; k <= h_Param.kMax; k++) {
		const int64_t n = (h_Param.Ni * i) + (h_Param.Nj * j) + (h_Param.Nk * k) + h_Param.N0;
		if (((i + j + k) % 2 == oe) && (idvolt[n] == 0)) {
			res2 += update_no_vector(&h_Param,
				i, j, k, n,
				rxp, ryp, rzp, rxm, rym, rzm,
				v, idepsr, epsr, omega);
		}
	}
	}
	}

	return res2;
}
