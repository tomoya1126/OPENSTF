#ifndef _OST_PROTOTYPE_H_
#define _OST_PROTOTYPE_H_

#ifdef __cplusplus
extern "C" {
#endif

// C
extern double cputime(void);
extern void   echar(void);
extern void   edge(void);
extern void   electrode(void);
extern int    geomlines(int, int, int *, int *, double (*)[8], double (*)[2][3], int *, double);
extern void   getscale(real_t *, real_t *);
extern void   get_span(double *, int, int, double, double, int *, int *, double);
extern int    ingeometry(double, double, double, int, double *, double);
extern void   initial(real_t *, real_t *);
extern int    input_data(FILE *);
extern void   makeL1d(void);
extern void   makeP2d(void);
extern void   monitor1(FILE *, const char []);
extern void   monitor2(FILE *, int, int);
extern void   monitor3(FILE *);
extern void   monitor4(FILE *);
extern void   monitor5(FILE *, const double []);
extern int    nearest(double, int, int, const double []);
extern void   plot3dGeom(void);
extern void   plotIter(void);
extern void   plotL1d(void);
extern void   plotP2d(void);
extern void   post(void);
extern int    post_data(FILE *);
extern void   readout(FILE *);
extern void   rescaling(real_t, real_t);
extern void   scaling(real_t, real_t);
extern void   setupfactor(void);
extern void   setupid(void);
extern void   setupsize(int, int, int, int);
extern int    tokenize(char *, const char *, char *[], int);
extern real_t update_no_vector(int);
extern real_t update_vector(int);
extern void   writeout(FILE *);

// MPI
extern void   comm_broadcast(void);
extern void   comm_check(int, int, int);
extern double comm_cputime(void);
extern void   comm_gather(void);
extern void   comm_reduction(void);
extern void   comm_string(const char *, char *);
extern real_t comm_sum(real_t);
extern void   comm_X(void);
extern void   comm_Y(void);
extern void   comm_Z(void);
extern void   mpi_close(void);
extern void   mpi_init(int, char **);
extern void   setup_mpi(void);

#ifdef __cplusplus
}
#endif

// C + CUDA
extern void   solve(int, FILE *);

// CUDA
#ifdef __CUDACC__
extern int    check_gpu(int, char []);
extern void   comm_cuda_X(void);
extern void   comm_cuda_Y(void);
extern void   comm_cuda_Z(void);
extern void   cuda_free(int, void *);
extern void   cuda_malloc(int, int, void **, size_t);
extern void   cuda_memcpy(int, void *, const void *, size_t, cudaMemcpyKind);
extern void   info_gpu(FILE *, int, int, int);
extern void   info_gpu_mpi(FILE *, int, const int [], int, int, int, int, int);
extern void   memory_alloc_gpu();
extern void   memory_copy_gpu();
extern void   memory_free_gpu();
extern int    rank2device(int, int, const int []);
extern void   setup_gpu(void);
#endif

#endif
