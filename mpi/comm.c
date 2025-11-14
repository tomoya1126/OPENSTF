/*
comm.c (MPI)

MPI routines
*/

#ifdef _MPI
#include <mpi.h>
#endif

#include "ost.h"
#include "ost_prototype.h"

// initialize
void mpi_init(int argc, char **argv)
{
#ifdef _MPI
	MPI_Init(&argc, &argv);
	MPI_Comm_size(MPI_COMM_WORLD, &commSize);
	MPI_Comm_rank(MPI_COMM_WORLD, &commRank);
#else
	commSize = 1;
	commRank = 0;
	argc = argc;	// dummy
	argv = argv;	// dummy
#endif
}


// close
void mpi_close(void)
{
#ifdef _MPI
	MPI_Finalize();
#endif
}


// check error code
// mode = 0/1 : Bcast/Allreduce
void comm_check(int ierr, int mode, int prompt)
{
#ifdef _MPI
	if (commSize > 1) {
		if (mode == 0) {
			MPI_Bcast(&ierr, 1, MPI_INT, 0, MPI_COMM_WORLD);
		}
		else {
			int g_ierr;
			MPI_Allreduce(&ierr, &g_ierr, 1, MPI_INT, MPI_LOR, MPI_COMM_WORLD);
			ierr = g_ierr;
		}
	}
	if (ierr) {
		MPI_Finalize();
	}
#endif
	mode = 0;  // dummy
	if (ierr) {
		if (prompt && (commRank == 0)) {
			fflush(stdout);
			getchar();
		}
		exit(0);
	}
}


// get cpu time [sec]
double comm_cputime(void)
{
#ifdef _MPI
	MPI_Barrier(MPI_COMM_WORLD);
	return MPI_Wtime();
#else
#ifdef _WIN32
	return (double)clock() / CLOCKS_PER_SEC;
#else
	struct timespec ts;
	clock_gettime(CLOCK_REALTIME, &ts);
	return (ts.tv_sec + (ts.tv_nsec * 1e-9));
#endif  // _WIN32
#endif  // MPI
}


// gather string
void comm_string(const char *lstr, char *gstr)
{
#ifdef _MPI
	char buff[BUFSIZ];
	if (commRank == 0) {
		MPI_Status status;
		strcpy(gstr, lstr);
		for (int i = 1; i < commSize; i++) {
			MPI_Recv(buff, BUFSIZ, MPI_CHAR, i, 0, MPI_COMM_WORLD, &status);
			strcat(gstr, "\n");
			strcat(gstr, buff);
		}
	}
	else {
		strcpy(buff, lstr);
		MPI_Send(buff, BUFSIZ, MPI_CHAR, 0, 0, MPI_COMM_WORLD);
	}
#else
	strcpy(gstr, lstr);
#endif
}


// broadcast input data
void comm_broadcast(void)
{
#ifdef _MPI
	const int maxvolt = sizeof(Volt) / sizeof(double);  // =256
	const int maxepsr = sizeof(Epsr) / sizeof(real_t);  // =256

	int    *i_buf = NULL;
	double *d_buf = NULL;
	int i_num = 0;
	int d_num = 0;

	// variables to buffers (root only)

	if (commRank == 0) {
		// number of data
		i_num = 8 + (3 * NGeom);
		d_num = 2 + (Nx + 1) + (Ny + 1) + (Nz + 1)
		      + (1 * maxvolt) + (1 * maxepsr) + (8 * NGeom);

		// alloc
		i_buf =    (int *)malloc(i_num * sizeof(int));
		d_buf = (double *)malloc(d_num * sizeof(double));

		int i_id = 0;
		int d_id = 0;

		i_buf[i_id++] = Nx;
		i_buf[i_id++] = Ny;
		i_buf[i_id++] = Nz;
		i_buf[i_id++] = NVolt;
		i_buf[i_id++] = NEpsr;
		i_buf[i_id++] = NGeom;

		i_buf[i_id++] = Solver.maxiter;
		i_buf[i_id++] = Solver.nout;
		d_buf[d_id++] = Solver.omega;
		d_buf[d_id++] = Solver.converg;

		for (int i = 0; i <= Nx; i++) {
			d_buf[d_id++] = Xn[i];
		}

		for (int j = 0; j <= Ny; j++) {
			d_buf[d_id++] = Yn[j];
		}

		for (int k = 0; k <= Nz; k++) {
			d_buf[d_id++] = Zn[k];
		}

		for (int n = 0; n < maxvolt; n++) {
			d_buf[d_id++] = Volt[n];
		}

		for (int n = 0; n < maxepsr; n++) {
			d_buf[d_id++] = Epsr[n];
		}

		for (int n = 0; n < NGeom; n++) {
			i_buf[i_id++] = Geom[n].type;
			i_buf[i_id++] = Geom[n].shape;
			i_buf[i_id++] = Geom[n].pid;
			for (int m = 0; m < 8; m++) {
				d_buf[d_id++] = Geom[n].g[m];
			}
		}

		// check
		assert(i_id == i_num);
		assert(d_id == d_num);
	}

	// broadcast (root to non-root)

	MPI_Bcast(&i_num, 1, MPI_INT, 0, MPI_COMM_WORLD);
	MPI_Bcast(&d_num, 1, MPI_INT, 0, MPI_COMM_WORLD);

	// alloc
	if (commRank > 0) {
		i_buf =    (int *)malloc(i_num * sizeof(int));
		d_buf = (double *)malloc(d_num * sizeof(double));
	}

	MPI_Bcast(i_buf, i_num, MPI_INT,    0, MPI_COMM_WORLD);
	MPI_Bcast(d_buf, d_num, MPI_DOUBLE, 0, MPI_COMM_WORLD);

	if (commRank > 0) {
		int i_id = 0;
		int d_id = 0;

		Nx             = i_buf[i_id++];
		Ny             = i_buf[i_id++];
		Nz             = i_buf[i_id++];
		NVolt          = i_buf[i_id++];
		NEpsr          = i_buf[i_id++];
		NGeom          = i_buf[i_id++];

		Solver.maxiter = i_buf[i_id++];
		Solver.nout    = i_buf[i_id++];
		Solver.omega   = d_buf[d_id++];
		Solver.converg = d_buf[d_id++];

		Xn = (double *)malloc((Nx + 1) * sizeof(double));
		for (int i = 0; i <= Nx; i++) {
			Xn[i] = d_buf[d_id++];
		}

		Yn = (double *)malloc((Ny + 1) * sizeof(double));
		for (int j = 0; j <= Ny; j++) {
			Yn[j] = d_buf[d_id++];
		}

		Zn = (double *)malloc((Nz + 1) * sizeof(double));
		for (int k = 0; k <= Nz; k++) {
			Zn[k] = d_buf[d_id++];
		}

		for (int n = 0; n < maxvolt; n++) {
			Volt[n] = d_buf[d_id++];
		}

		for (int n = 0; n < maxepsr; n++) {
			Epsr[n] = (real_t)d_buf[d_id++];
		}

		Geom = (geometry_t *)malloc(NGeom * sizeof(geometry_t));
		for (int n = 0; n < NGeom; n++) {
			Geom[n].type  =       i_buf[i_id++];
			Geom[n].shape =       i_buf[i_id++];
			Geom[n].pid   = (id_t)i_buf[i_id++];
			for (int m = 0; m < 8; m++) {
				Geom[n].g[m] = d_buf[d_id++];
			}
		}

		// check
		assert(i_id == i_num);
		assert(d_id == d_num);
	}

	// free
	free(i_buf);
	free(d_buf);
/*
	// debug
	printf("%d %d\n", commSize, commRank);
	printf("%d %d %d\n", Nx, Ny, Nz);
	//printf("%d %d %g %g\n", Solver.maxiter, Solver.nout, Solver.omega, Solver.converg);
	//for (int i = 0; i <= Nx; i++) printf("%d %f\n", i, Xn[i]);
	//for (int j = 0; j <= Ny; j++) printf("%d %f\n", j, Yn[j]);
	//for (int k = 0; k <= Nz; k++) printf("%d %f\n", k, Zn[k]);
	//printf("%d %d\n", NVolt, NEpsr);
	//for (int n = 0; n < NVolt; n++) printf("%d %f\n", n, Volt[n]);
	//for (int n = 0; n < NEpsr; n++) printf("%d %f\n", n, Epsr[n]);
	//printf("%d\n", NGeom);
	//for (int n = 0; n < NGeom; n++) printf("%d %d %d %d %f %f %f %f %f %f\n", n, Geom[n].type, Geom[n].shape, Geom[n].pid, Geom[n].g[0], Geom[n].g[1], Geom[n].g[2], Geom[n].g[3], Geom[n].g[4], Geom[n].g[5]);
	fflush(stdout);
*/
#endif
}


// sum reduction (scalar)
real_t comm_sum(real_t l_sum)
{
	real_t sum;
#ifdef _MPI
	MPI_Allreduce(&l_sum, &sum, 1, MPI_REAL_T, MPI_SUM, MPI_COMM_WORLD);
#else
	sum = l_sum;
#endif
	return sum;
}


// sum reduction (vector)
void comm_reduction(void)
{
	for (int n = 0; n < NVolt; n++) {
		Echar[n] = comm_sum((real_t)Echar[n]);
	}
}


// gather
void comm_gather(void)
{
#ifdef _MPI
	int64_t g_n, n;
	MPI_Status status;
	int isend[11], irecv[11];
	const int tag = 0;

	// root : self copy to global array
	if (commRank == 0) {
		// save local index
		const int imin = iMin;
		const int imax = iMax;
		const int jmin = jMin;
		const int jmax = jMax;
		const int kmin = kMin;
		const int kmax = kMax;
		const int64_t ni = Ni;
		const int64_t nj = Nj;
		const int64_t nk = Nk;
		const int64_t n0 = N0;
		//const int64_t nn = NN;

		// new global index
		setupsize(1, 1, 1, 0);

		// alloc global array
		g_V      = (real_t *)malloc(NN * sizeof(real_t));
		g_idVolt =   (id_t *)malloc(NN * sizeof(id_t));
		g_idEpsr =   (id_t *)malloc(NN * sizeof(id_t));

		// self copy
		for (int i = imin; i <= imax; i++) {
		for (int j = jmin; j <= jmax; j++) {
		for (int k = kmin; k <= kmax; k++) {
			g_n = (Ni * i) + (Nj * j) + (Nk * k) + N0;
			n   = (ni * i) + (nj * j) + (nk * k) + n0;
			g_V[g_n]      = V[n];
			g_idVolt[g_n] = idVolt[n];
			g_idEpsr[g_n] = idEpsr[n];
		}
		}
		}
	}

	// root : receive
	if (commRank == 0) {
		for (int irank = 1; irank < commSize; irank++) {
			// receive local index
			MPI_Recv(irecv, 11, MPI_INT, irank, tag, MPI_COMM_WORLD, &status);
			const int imin = irecv[0];
			const int imax = irecv[1];
			const int jmin = irecv[2];
			const int jmax = irecv[3];
			const int kmin = irecv[4];
			const int kmax = irecv[5];
			const int ni   = irecv[6];
			const int nj   = irecv[7];
			const int nk   = irecv[8];
			const int n0   = irecv[9];
			const int nn   = irecv[10];
			//printf("%d %d %d %d %d\n", commRank, imin, imax, n0, nn); fflush(stdout);

			// alloc receive buffer
			real_t *recv_v      = (real_t *)malloc(nn * sizeof(real_t));
			id_t   *recv_idvolt =   (id_t *)malloc(nn * sizeof(id_t));
			id_t   *recv_idepsr =   (id_t *)malloc(nn * sizeof(id_t));

			// receive and set
			MPI_Recv(recv_v,      nn, MPI_REAL_T, irank, tag, MPI_COMM_WORLD, &status);
			MPI_Recv(recv_idvolt, nn, MPI_ID_T,   irank, tag, MPI_COMM_WORLD, &status);
			MPI_Recv(recv_idepsr, nn, MPI_ID_T,   irank, tag, MPI_COMM_WORLD, &status);
			for (int i = imin; i <= imax; i++) {
			for (int j = jmin; j <= jmax; j++) {
			for (int k = kmin; k <= kmax; k++) {
				g_n = (Ni * i) + (Nj * j) + (Nk * k) + N0;
				n   = (ni * i) + (nj * j) + (nk * k) + n0;
				g_V[g_n]      = recv_v[n];
				g_idVolt[g_n] = recv_idvolt[n];
				g_idEpsr[g_n] = recv_idepsr[n];
			}
			}
			}
		}
	}
	else {
		// non-root : send to root
		// index
		isend[0]  = iMin;
		isend[1]  = iMax;
		isend[2]  = jMin;
		isend[3]  = jMax;
		isend[4]  = kMin;
		isend[5]  = kMax;
		isend[6]  = (int)Ni;
		isend[7]  = (int)Nj;
		isend[8]  = (int)Nk;
		isend[9]  = (int)N0;
		isend[10] = (int)NN;
		MPI_Send(isend, 11, MPI_INT, 0, tag, MPI_COMM_WORLD);

		// data
		const int nn = (int)NN;
		MPI_Send(V,      nn, MPI_REAL_T, 0, tag, MPI_COMM_WORLD);
		MPI_Send(idVolt, nn, MPI_ID_T,   0, tag, MPI_COMM_WORLD);
		MPI_Send(idEpsr, nn, MPI_ID_T,   0, tag, MPI_COMM_WORLD);
	}

	// copy pointer : global -> root
	if (commRank == 0) {
		V      = g_V;
		idVolt = g_idVolt;
		idEpsr = g_idEpsr;
	}
#endif
}
