/*
allocfree_gpu.cu (CUDA)
*/

#include "ost.h"
#include "ost_cuda.h"
#include "ost_prototype.h"

void memory_alloc_gpu()
{
	//const int64_t num = (int64_t)(Nx + 3) * (Ny + 3) * (Nz + 3);

	cuda_malloc(GPU, UM, (void **)&d_V,       NN * sizeof(real_t));
	cuda_malloc(GPU, UM, (void **)&d_idVolt,  NN * sizeof(id_t));
	cuda_malloc(GPU, UM, (void **)&d_idEpsr,  NN * sizeof(id_t));
	cuda_malloc(GPU, UM, (void **)&d_RXp, (Nx + 1) * sizeof(real_t));
	cuda_malloc(GPU, UM, (void **)&d_RYp, (Ny + 1) * sizeof(real_t));
	cuda_malloc(GPU, UM, (void **)&d_RZp, (Nz + 1) * sizeof(real_t));
	cuda_malloc(GPU, UM, (void **)&d_RXm, (Nx + 1) * sizeof(real_t));
	cuda_malloc(GPU, UM, (void **)&d_RYm, (Ny + 1) * sizeof(real_t));
	cuda_malloc(GPU, UM, (void **)&d_RZm, (Nz + 1) * sizeof(real_t));
	cuda_malloc(GPU, UM, (void **)&d_Epsr, 256 * sizeof(real_t));

	cuda_memcpy(GPU, d_V,      V,            NN * sizeof(real_t), cudaMemcpyHostToDevice);
	cuda_memcpy(GPU, d_idVolt, idVolt,       NN * sizeof(id_t),   cudaMemcpyHostToDevice);
	cuda_memcpy(GPU, d_idEpsr, idEpsr,       NN * sizeof(id_t),   cudaMemcpyHostToDevice);
	cuda_memcpy(GPU, d_RXp,    RXp,    (Nx + 1) * sizeof(real_t), cudaMemcpyHostToDevice);
	cuda_memcpy(GPU, d_RYp,    RYp,    (Ny + 1) * sizeof(real_t), cudaMemcpyHostToDevice);
	cuda_memcpy(GPU, d_RZp,    RZp,    (Nz + 1) * sizeof(real_t), cudaMemcpyHostToDevice);
	cuda_memcpy(GPU, d_RXm,    RXm,    (Nx + 1) * sizeof(real_t), cudaMemcpyHostToDevice);
	cuda_memcpy(GPU, d_RYm,    RYm,    (Ny + 1) * sizeof(real_t), cudaMemcpyHostToDevice);
	cuda_memcpy(GPU, d_RZm,    RZm,    (Nz + 1) * sizeof(real_t), cudaMemcpyHostToDevice);
	cuda_memcpy(GPU, d_Epsr,   Epsr,        256 * sizeof(real_t), cudaMemcpyHostToDevice);
}


void memory_copy_gpu()
{
	cuda_memcpy(GPU, V, d_V, NN * sizeof(real_t), cudaMemcpyDeviceToHost);
}


void memory_free_gpu()
{
	cuda_free(GPU, d_V);
	cuda_free(GPU, d_idVolt);
	cuda_free(GPU, d_idEpsr);
	cuda_free(GPU, d_RXp);
	cuda_free(GPU, d_RYp);
	cuda_free(GPU, d_RZp);
	cuda_free(GPU, d_RXm);
	cuda_free(GPU, d_RYm);
	cuda_free(GPU, d_RZm);
	cuda_free(GPU, d_Epsr);
}
