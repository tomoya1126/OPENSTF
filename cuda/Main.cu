/*
OpenSTF Version 4.2.2 (CUDA)

solver
*/

#define MAIN
#include "ost.h"
#include "ost_cuda.h"
#undef MAIN

#include "ost_prototype.h"

static void args(int, char *[], int *, int *, int *, char []);
static void error_check(int, int);

int main(int argc, char *argv[])
{
	const char prog[] = "(GPU)";
	const char errfmt[] = "*** file %s open error.\n";
	char str[BUFSIZ];
	int ierr = 0;
	double cpu[] = {0, 0, 0, 0};
	FILE *fp_in = NULL, *fp_out = NULL, *fp_log = NULL;
	const int io = 1;  // cf. MPI

	// arguments
	GPU = 1;
	UM = 0;
	int vector = 0;
	int device = 0;
	int prompt = 0;
	char fn_in[BUFSIZ] = "";
	args(argc, argv, &vector, &device, &prompt, fn_in);

	// cpu time
	if (GPU) cudaDeviceSynchronize();
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
		sprintf(str, "%s, process=1, vector=%s", (GPU ? "GPU" : "CPU"), (vector ? "on" : "off"));
		monitor1(fp_log, str);
		// check GPU and show info
		info_gpu(fp_log, device, GPU, UM);
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
		monitor2(fp_log, vector, GPU);
	}

	// cpu time
	if (GPU) cudaDeviceSynchronize();
	cpu[1] = cputime();

	// solve
	solve(vector, fp_log);

	// cpu time
	if (GPU) cudaDeviceSynchronize();
	cpu[2] = cputime();

	// energy and charge
	echar();

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
	error_check(ierr, prompt);

	// cpu time
	if (GPU) cudaDeviceSynchronize();
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


// arguments
static void args(int argc, char *argv[],
	int *vector, int *device, int *prompt, char fn_in[])
{
	const char usage[] = "Usage : ost_cuda [-gpu|-cpu] [-hdm|-um] [-device <device>] [-vector|-no-vector] <datafile>";

	if (argc < 2) {
		printf("%s\n", usage);
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
		else if (!strcmp(*argv, "-device")) {
			if (--argc) {
				*device = atoi(*++argv);
				if (*device <= 0) *device = 1;
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
