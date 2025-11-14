// ost_cuda.h
#ifndef _OST_CUDA_H_
#define _OST_CUDA_H_

#define CEIL(n,d) (((n) + (d) - 1) / (d))

typedef struct {
	int     iMin, iMax, jMin, jMax, kMin, kMax;
	int64_t Ni, Nj, Nk, N0;
} param_t;

EXTERN param_t h_Param;
__constant__ param_t d_Param;

EXTERN int    GPU;
EXTERN int    UM;

EXTERN dim3   updateBlock;
EXTERN dim3   bufBlock;

EXTERN real_t *d_V;
EXTERN real_t *d_RXp, *d_RYp, *d_RZp, *d_RXm, *d_RYm, *d_RZm;
EXTERN real_t *d_Epsr, *d_Epsr_v;
EXTERN id_t   *d_idVolt, *d_idEpsr;
EXTERN real_t *d_SendBuf_x, *d_SendBuf_y, *d_SendBuf_z;
EXTERN real_t *d_RecvBuf_x, *d_RecvBuf_y, *d_RecvBuf_z;

#endif		// _OST_CUDA_H_
