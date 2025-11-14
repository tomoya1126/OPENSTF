/*
post_data.c

read post data
*/

#include "ost.h"
#include "ost_prototype.h"

#define MAXTOKEN 1000

int post_data(FILE *fp)
{
	int    ntoken, nline;
	int    version = 0;
	char   strline[BUFSIZ], strkey[BUFSIZ], strsave[BUFSIZ];
	char   *token[MAXTOKEN];
	const char sep[] = " \t";			// separator

	// initialize

	Piter = 0;

	NL1d = 0;
	L1dScale.db = 0;      // linear
	L1dScale.user = 0;    // auto scale
	L1dLog = 1;

	NP2d = 0;
	P2dFigure[0] = P2dFigure[1] = 1;
	P2dScale.db = 0;      // linear
	P2dScale.user = 0;    // auto scale
	P2dObject[0] = P2dObject[1] = 1;
	P2dZoomin = 0;
	P2dLog = 1;

	// window size 2D

	Width2d    = 1.5;
	Height2d   = 1.0;
	Fontsize2d = 0.03;

	// HTML : pixel (for Linux)
	if (HTML) {
		Width2d    = 750;
		Height2d   = 500;
		Fontsize2d = 13;
	}

	// read

	nline = 0;
	while (fgets(strline, sizeof(strline), fp) != NULL) {
		//printf("%s", strline);

		// skip a vacant line
		if (strlen(strline) <= 1) continue;

		// skip a comment line
		if (strline[0] == '#') continue;

		// delete "\n"
		//printf("%ld\n", strlen(strline));
		if (strstr(strline, "\r\n") != NULL) {
			strline[strlen(strline) - 2] = '\0';
		}
		else if ((strstr(strline, "\r") != NULL) || (strstr(strline, "\n") != NULL)) {
			strline[strlen(strline) - 1] = '\0';
		}
		//printf("%ld\n", strlen(strline));

		// "end" -> break
		if (!strncmp(strline, "end", 3)) break;

		// save "strline"
		strcpy(strsave, strline);

		// token ("strline" is destroyed)
		ntoken = tokenize(strline, sep, token, MAXTOKEN);
		//for (int i = 0; i < ntoken; i++) printf("%d %s\n", i, token[i]);

		// check number of data and "=" (excluding header)
		if ((nline > 0) && ((ntoken < 3) || strcmp(token[1], "="))) continue;

		// keyword
		strcpy(strkey, token[0]);

		// input
		if      (nline == 0) {
			if (strcmp(strkey, "OpenSTF")) {
				fprintf(stderr, "*** not OpenSTF data\n");
				return 1;
			}
			else if (ntoken > 2) {
				version = (10 * atoi(token[1])) + atoi(token[2]);
				version = version;  // dummy
			}
			nline++;
		}
		else if (!strcmp(strkey, "plotiter")) {
			Piter = atoi(token[2]);
		}
		else if (!strcmp(strkey, "plot1d")) {
			if (ntoken < 6) {
				fprintf(stderr, "*** invalid %s data #%d\n", strkey, NL1d + 1);
				return 1;
			}
			L1d = (l1d_t *)realloc(L1d, (NL1d + 1) * sizeof(l1d_t));
			L1d[NL1d].component = (char)toupper((int)token[2][0]);
			L1d[NL1d].direction = (char)toupper((int)token[3][0]);
			L1d[NL1d].position[0] = atof(token[4]);
			L1d[NL1d].position[1] = atof(token[5]);
			NL1d++;
		}
		else if (!strcmp(strkey, "1ddb")) {
			L1dScale.db = atoi(token[2]);
		}
		else if (!strcmp(strkey, "1dscale")) {
			if (ntoken > 4) {
				L1dScale.user = 1;
				L1dScale.min = atof(token[2]);
				L1dScale.max = atof(token[3]);
				L1dScale.div = atoi(token[4]);
			}
		}
		else if (!strcmp(strkey, "1dlog")) {
			L1dLog = atoi(token[2]);
		}
		else if (!strcmp(strkey, "plot2d")) {
			if (ntoken < 5) {
				fprintf(stderr, "*** invalid %s data #%d\n", strkey, NP2d + 1);
				return 1;
			}
			P2d = (p2d_t *)realloc(P2d, (NP2d + 1) * sizeof(p2d_t));
			strcpy(P2d[NP2d].component, token[2]);
			P2d[NP2d].direction = (char)toupper((int)token[3][0]);
			P2d[NP2d].position = atof(token[4]);
			NP2d++;
		}
		else if (!strcmp(strkey, "2dfigure")) {
			if (ntoken > 3) {
				P2dFigure[0] = atoi(token[2]);
				P2dFigure[1] = atoi(token[3]);
			}
		}
		else if (!strcmp(strkey, "2ddb")) {
			P2dScale.db = atoi(token[2]);
		}
		else if (!strcmp(strkey, "2dscale")) {
			if (ntoken > 3) {
				P2dScale.user = 1;
				P2dScale.min = atof(token[2]);
				P2dScale.max = atof(token[3]);
				// token[4] : nou used
			}
		}
		else if (!strcmp(strkey, "2dcontour")) {
			P2dContour = atoi(token[2]);
		}
		else if (!strcmp(strkey, "2dobject")) {
			if (ntoken > 3) {
				P2dObject[0] = atoi(token[2]);
				P2dObject[1] = atoi(token[3]);
			}
		}
		else if (!strcmp(strkey, "2dzoom")) {
			if (ntoken > 5) {
				P2dZoomin = 1;
				P2dZoom[0][0] = atof(token[2]);
				P2dZoom[0][1] = atof(token[3]);
				P2dZoom[1][0] = atof(token[4]);
				P2dZoom[1][1] = atof(token[5]);
			}
		}
		else if (!strcmp(strkey, "2dlog")) {
			P2dLog = atoi(token[2]);
		}
	}

	return 0;
}
