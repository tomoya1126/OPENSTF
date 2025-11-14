/*
OpenSTF Version 4.2.2 (CPU + MPI)

solver
*/

#define MAIN
#include "ost.h"
#undef MAIN
#include "ost_prototype.h"

static void args(int, char *[], int *, int *, int *, char []);

int main(int argc, char *argv[])
{
	const char prog[] = "(CPU+MPI)";
	const char errfmt[] = "*** file %s open error.\n";
	char str[BUFSIZ];
	int ierr = 0;
	double cpu[] = {0, 0, 0, 0};
	FILE *fp_in = NULL, *fp_out = NULL, *fp_log = NULL;

	// initialize MPI
	mpi_init(argc, argv);
	const int io = !commRank;

	// arguments
	Npx = Npy = Npz = 1;
	int nthread = 1;
	int vector = 0;
	int prompt = 0;
	char fn_in[BUFSIZ] = "";
	args(argc, argv, &nthread, &vector, &prompt, fn_in);

	// set number of threads
#ifdef _OPENMP
	omp_set_num_threads(nthread);
#endif

	// cpu time
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
		sprintf(str, "CPU, process=%dx%dx%d=%d, thread=%d, vector=%s", Npx, Npy, Npz, commSize, nthread, (vector ? "on" : "off"));
		monitor1(fp_log, str);
	}

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
	setupfactor();
	setupid();

	// monitor
	if (io) {
		monitor2(fp_log, vector, 0);
	}

	// cpu time
	cpu[1] = comm_cputime();

	// solve
	solve(vector, fp_log);

	// cpu time
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


static void args(int argc, char *argv[],
	int *nthread, int *vector, int *prompt, char fn_in[])
{
	const char usage[] = "Usage : mpiexec -n <process> ost_mpi [-p <x> <y> <z>] [-n <thread>] [-no-vector|-vector] <datafile>";

	if (argc < 2) {
		if (commRank == 0) {
			printf("%s\n", usage);
		}
		mpi_close();
		exit(0);
	}

	while (--argc) {
		++argv;
		if (!strcmp(*argv, "-n")) {
			if (--argc) {
				*nthread = atoi(*++argv);
				if (*nthread <= 0) *nthread = 1;
			}
			else {
				break;
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
