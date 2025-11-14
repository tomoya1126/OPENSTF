/*
OpenSTF Version 4.2.2

post process
*/

#define MAIN
#include "ost.h"
#undef MAIN

#include "ost_prototype.h"

static void args(int, char *[], int *, char []);

int main(int argc, char *argv[])
{
	const char errfmt[] = "*** file %s open error.\n";
	FILE *fp_in = NULL, *fp_out = NULL;

	// arguments
	HTML = 0;
	int prompt = 0;
	char fn_in[BUFSIZ] = "";
	args(argc, argv, &prompt, fn_in);

	// input data
	if ((fp_in = fopen(fn_in, "r")) == NULL) {
		printf(errfmt, fn_in);
		if (prompt) getchar();
		exit(1);
	}
	if (post_data(fp_in)) {
		fclose(fp_in);
		if (prompt) getchar();
		exit(1);
	}

	// read ost.out
	if ((fp_out = fopen(FN_out, "rb")) == NULL) {
		printf(errfmt, FN_out);
		if (prompt) getchar();
		exit(1);
	}
	readout(fp_out);
	fclose(fp_out);

	// make data
	if (NL1d > 0) {
		makeL1d();
	}
	if (NP2d > 0) {
		makeP2d();
	}

	// post process
	post();

	// prompt
	if (prompt) getchar();

	return 0;
}

static void args(int argc, char *argv[],
	int *prompt, char fn_in[])
{
	const char usage[] = "Usage : ost_post [-html] <datafile>";

	if (argc < 2) {
		printf("%s\n", usage);
		exit(0);
	}

	while (--argc) {
		++argv;
		if (!strcmp(*argv, "-html")) {
			HTML = 1;
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
