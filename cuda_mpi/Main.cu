/*
OpenSTF Version 4.2.2 (CUDA + MPI)

solver
*/

#define MAIN
#include "ost.h"
#include "ost_cuda.h"
#undef MAIN

#include "ost_prototype.h"

static void args(int, char *[], int *, int [], int *, int *, char []);

int main(int argc, char *argv[])
{
	const char prog[] = "(GPU+MPI)";
	const char errfmt[] = "*** file %s open error.\n";
	char str[BUFSIZ];
	int ierr = 0;
	double cpu[] = {0, 0, 0, 0};
	FILE *fp_in = NULL, *fp_out = NULL, *fp_log = NULL;

	// initialize MPI
	mpi_init(argc, argv);
	const int io = !commRank;

	// arguments
	GPU = 1;
	UM = 0;
	Npx = Npy = Npz = 1;
	int vector = 0;
	int prompt = 0;
	int nhost = 0;
	int ndevice[256];
	char fn_in[BUFSIZ] = "";
	args(argc, argv, &nhost, ndevice, &vector, &prompt, fn_in);

	// cpu time
	if (GPU) cudaDeviceSynchronize();
	cpu[0] = comm_cputime();

	// input data
	if (io) {
		if ((fp_in = fopen(fn_in, "r")) == NULL) {
			printf(errfmt, fn_in);
			ierr = 1;
		}
		if (!ierr) {
			ierr = input_data(fp_in);
			fclose(fp_in);
		}
	}
	comm_check(ierr, 0, prompt);

	// open log file
	if (io) {
		if ((fp_log = fopen(FN_log, "w")) == NULL) {
			printf(errfmt, FN_log);
			ierr = 1;
		}
	}
	comm_check(ierr, 0, prompt);

	// monitor
	if (io) {
		// logo
		sprintf(str, "<<< %s %s Ver.%d.%d.%d >>>", PROGRAM, prog, VERSION_MAJOR, VERSION_MINOR, VERSION_BUILD);
		monitor1(fp_log, str);
		// mode
		sprintf(str, "%s, process=%dx%dx%d=%d, vector=%s", (GPU ? "GPU" : "CPU"), Npx, Npy, Npz, commSize, (vector ? "on" : "off"));
		monitor1(fp_log, str);
	}
	// check GPU and show info
	info_gpu_mpi(fp_log, nhost, ndevice, GPU, UM, commSize, commRank, prompt);

	// plot geometry 3d and exit
	if (io && Plot3dGeom) {
		plot3dGeom();
		ierr = 1;
	}
	comm_check(ierr, 0, prompt);

	// broadcast (MPI)
	if (commSize > 1) {
		comm_broadcast();
	}

	// setup
	setupsize(Npx, Npy, Npz, commRank);
	//printf("%d %d %d %d %d %d %d %d\n", commSize, commRank, Npx, Npy, Npz, Ipx, Ipy, Ipz); fflush(stdout);
	setupfactor();
	setupid();

	// monitor
	if (io) {
		monitor2(fp_log, vector, GPU);
	}

	// cpu time
	if (GPU) cudaDeviceSynchronize();
	cpu[1] = comm_cputime();

	// solve
	solve(vector, fp_log);

	// cpu time
	if (GPU) cudaDeviceSynchronize();
	cpu[2] = comm_cputime();

	// energy and charge
	echar();
	if (commSize > 1) {
		comm_reduction();
	}

	// gather
	if (commSize > 1) {
		comm_gather();
	}

	// output
	if (io) {
		// monitor
		monitor3(fp_log);

		// output files
		monitor4(fp_log);

		// write ost.out
		if ((fp_out = fopen(FN_out, "wb")) == NULL) {
			printf(errfmt, FN_out);
			ierr = 1;
		}
		if (!ierr) {
			writeout(fp_out);
			fclose(fp_out);
		}
	}
	comm_check(ierr, 0, prompt);

	// cpu time
	if (GPU) cudaDeviceSynchronize();
	cpu[3] = comm_cputime();

	if (io) {
		// cpu time
		monitor5(fp_log, cpu);

		// close log file
		fclose(fp_log);
	}

	// finalize MPI
	mpi_close();

	// prompt
	if (io && prompt) getchar();

	return 0;
}


// arguments
static void args(int argc, char *argv[],
	int *nhost, int ndevice[], int *vector, int *prompt, char fn_in[])
{
	const char usage[] = "Usage : mpiexec -n <process> ost_cuda_mpi [-gpu|-cpu] [-hdm|-um] [-p <x> <y> <z>] [-no-vector|-vector] <datafile>";

	if (argc < 2) {
		if (commRank == 0) {
			printf("%s\n", usage);
		}
		mpi_close();
		exit(0);
	}

	while (--argc) {
		++argv;
		if (!strcmp(*argv, "-gpu")) {
			GPU = 1;
		}
		else if (!strcmp(*argv, "-cpu")) {
			GPU = 0;
		}
		else if (!strcmp(*argv, "-hdm")) {
			UM = 0;
		}
		else if (!strcmp(*argv, "-um")) {
			UM = 1;
		}
		else if (!strcmp(*argv, "-hosts")) {
			if (--argc) {
				*nhost = atoi(*++argv);
				if (*nhost < 1) *nhost = 1;
				//ndevice = (int *)malloc(*nhost * sizeof(int));
				for (int ihost = 0; ihost < *nhost; ihost++) {
					if (argc > 1) {
						ndevice[ihost] = atoi(*++argv);
						argc--;
					}
					else {
						ndevice[ihost] = 1;
					}
				}
			}
		}
		else if (!strcmp(*argv, "-p")) {
			if (--argc) Npx = atoi(*++argv);
			if (--argc) Npy = atoi(*++argv);
			if (--argc) Npz = atoi(*++argv);
		}
		else if (!strcmp(*argv, "-vector")) {
			*vector = 1;
		}
		else if (!strcmp(*argv, "-no-vector")) {
			*vector = 0;
		}
		else if (!strcmp(*argv, "-prompt")) {
			*prompt = 1;
		}
		else if (!strcmp(*argv, "--help")) {
			if (commRank == 0) {
				printf("%s\n", usage);
			}
			mpi_close();
			exit(0);
		}
		else if (!strcmp(*argv, "--version")) {
			if (commRank == 0) {
				printf("%s Ver.%d.%d.%d\n", PROGRAM, VERSION_MAJOR, VERSION_MINOR, VERSION_BUILD);
			}
			mpi_close();
			exit(0);
		}
		else {
			strcpy(fn_in, *argv);
		}
	}

	// check region
	if (commSize != Npx * Npy * Npz) {
		Npx = commSize;
		Npy = 1;
		Npz = 1;
	}
}
