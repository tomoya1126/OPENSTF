/*
OpenSTF Version 4.2.2 (CPU + OpenMP)

solver
*/

#define MAIN
#include "ost.h"
#undef MAIN

#include "ost_prototype.h"

static void args(int, char *[], int *, int *, int *, char []);
static void error_check(int, int);

int main(int argc, char *argv[])
{
	const char prog[] = "(CPU+OpenMP)";
	const char errfmt[] = "*** file %s open error.\n";
	char str[BUFSIZ];
	int ierr = 0;
	double cpu[] = {0, 0, 0, 0};
	FILE *fp_in = NULL, *fp_out = NULL, *fp_log = NULL;

	const int io = 1;  // MPI

	// arguments
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
	cpu[0] = cputime();

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
	error_check(ierr, prompt);

	// open log file
	if (io) {
		if ((fp_log = fopen(FN_log, "w")) == NULL) {
			printf(errfmt, FN_log);
			ierr = 1;
		}
	}
	error_check(ierr, prompt);

	// monitor
	if (io) {
		// logo
		sprintf(str, "<<< %s %s Ver.%d.%d.%d >>>", PROGRAM, prog, VERSION_MAJOR, VERSION_MINOR, VERSION_BUILD);
		monitor1(fp_log, str);
		// mode
		sprintf(str, "CPU, thread=%d, process=1, vector=%s", nthread, (vector ? "on" : "off"));
		monitor1(fp_log, str);
	}

	// plot geometry 3d and exit
	if (io && Plot3dGeom) {
		plot3dGeom();
		ierr = 1;
	}
	error_check(ierr, prompt);

	// setup
	setupsize(1, 1, 1, 0);
	setupfactor();
	setupid();

	// monitor
	if (io) {
		monitor2(fp_log, vector, 0);
	}

	// cpu time
	cpu[1] = cputime();

	// solve
	solve(vector, fp_log);

	// cpu time
	cpu[2] = cputime();

	// output
	if (io) {
		// energy and charge
		echar();

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
	error_check(ierr, prompt);

	// cpu time
	cpu[3] = cputime();

	if (io) {
		// cpu time
		monitor5(fp_log, cpu);

		// close log file
		fclose(fp_log);
	}

	// prompt
	if (io && prompt) getchar();

	return 0;
}


static void args(int argc, char *argv[], int *nthread, int *vector, int *prompt, char fn_in[])
{
	const char usage[] = "Usage : ost [-n <thread>] [-no-vector|-vector] <datafile>";

	if (argc < 2) {
		printf("%s\n", usage);
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
			printf("%s\n", usage);
			exit(0);
		}
		else if (!strcmp(*argv, "--version")) {
			printf("%s Ver.%d.%d.%d\n", PROGRAM, VERSION_MAJOR, VERSION_MINOR, VERSION_BUILD);
			exit(0);
		}
		else {
			strcpy(fn_in, *argv);
		}
	}
}


// error check
static void error_check(int ierr, int prompt)
{
	if (ierr) {
		if (prompt) {
			fflush(stdout);
			getchar();
		}
		exit(1);
	}
}
