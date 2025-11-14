/*
setup_gpu.cu (CUDA)
*/

#include "ost.h"
#include "ost_cuda.h"

void setup_gpu()
{
	// block
	updateBlock = dim3(16, 16, 1);

	// constant memory
	h_Param.Ni   = Ni;
	h_Param.Nj   = Nj;
	h_Param.Nk   = Nk;
	h_Param.N0   = N0;
	h_Param.iMin = iMin;
	h_Param.iMax = iMax;
	h_Param.jMin = jMin;
	h_Param.jMax = jMax;
	h_Param.kMin = kMin;
	h_Param.kMax = kMax;
}
