/*
plotL1d.c

plot field along lines (2D)
*/

#include "ost.h"
#include "ev.h"

void plotL1d(void)
{
	const int    ncompo = 10;
	const int    ndbdiv = 4;
	const double dbdiv = 10.0;
	const double eps = 1e-20;
	const char   *component[][3] = {
		{"V",  "[V]",     ""         },
		{"E",  "[V/m]",   "[dBV/m]"  },
		{"Ex", "[V/m]",   "[dBV/m]"  },
		{"Ey", "[V/m]",   "[dBV/m]"  },
		{"Ez", "[V/m]",   "[dBV/m]"  },
		{"D",  "[C/m^2]", "[dBC/m^2]"},
		{"Dx", "[C/m^2]", "[dBC/m^2]"},
		{"Dy", "[C/m^2]", "[dBC/m^2]"},
		{"Dz", "[C/m^2]", "[dBC/m^2]"},
		{"Q",  "[C/m^3]", "[dBC/m^3]"}
	};
	const unsigned char rgb[][3] = {
		{0, 0, 0}, {0, 0, 0}, {255, 0, 0}, {0, 255, 0}, {0, 0, 255},
		           {0, 0, 0}, {255, 0, 0}, {0, 255, 0}, {0, 0, 255}, {0, 0, 0}};
	char   str[BUFSIZ], str2[BUFSIZ], fmt[BUFSIZ];

	// open
	FILE *fp;
	if ((fp = fopen(FN_1d, "w")) == NULL) {
		fprintf(stderr, "*** file %s open error.\n", FN_1d);
		return;
	}

	// layout
	const double x1 = 0.14 * Width2d;
	const double x2 = 0.95 * Width2d;
	const double y1 = 0.10 * Height2d;
	const double y2 = 0.88 * Height2d;
	const double h = Fontsize2d;

	// loop on lines
	for (int n = 0; n < NL1d; n++) {

		// dB (V : linear only)
		const int db = L1dScale.db && (L1d[n].component != 'V');

		// component
		int ic1 = 0, ic2 = 0;
		if      (L1d[n].component == 'V') {
			ic1 = 0;
			ic2 = 0;
		}
		else if (L1d[n].component == 'E') {
			ic1 = 1;
			ic2 = 4;
		}
		else if (L1d[n].component == 'D') {
			ic1 = 5;
			ic2 = 8;
		}
		else if (L1d[n].component == 'Q') {
			ic1 = 9;
			ic2 = 9;
		}
		//printf("%d %d\n", ic1, ic2);

		double *pos = NULL;
		int ndata = 0;
		if      (L1d[n].direction == 'X') {
			pos = Xn;
			ndata = Nx + 1;
			sprintf(str2, "Y[m]=%g Z[m]=%g", Yn[L1d[n].posid[0]], Zn[L1d[n].posid[1]]);
		}
		else if (L1d[n].direction == 'Y') {
			pos = Yn;
			ndata = Ny + 1;
			sprintf(str2, "Z[m]=%g X[m]=%g", Zn[L1d[n].posid[0]], Xn[L1d[n].posid[1]]);
		}
		else if (L1d[n].direction == 'Z') {
			pos = Zn;
			ndata = Nz + 1;
			sprintf(str2, "X[m]=%g Y[m]=%g", Xn[L1d[n].posid[0]], Yn[L1d[n].posid[1]]);
		}

		// to dB
		if (db) {
			for (int ic = 0; ic < ncompo; ic++) {
				if (ic == 0) continue;
				for (int idata = 0; idata < ndata; idata++) {
					F1d[n][ic][idata] = 20 * log10(MAX(fabs(F1d[n][ic][idata]), eps));
				}
			}
		}

		// max and min
		double fmin = F1d[n][ic1][0];
		double fmax = fmin;
		for (int ic = ic1; ic <= ic2; ic++) {
			for (int idata = 0; idata < ndata; idata++) {
				fmax = MAX(fmax, F1d[n][ic][idata]);
				fmin = MIN(fmin, F1d[n][ic][idata]);
			}
		}
		//printf("%f %f\n", fmin, fmax);

		// scale
		double ymin = 0;
		double ymax = 0;
		int    ydiv = 0;
		if (!L1dScale.user) {
			// linear
			if (!db) {
				ymax = fmax;
				ymin = fmin;
				ydiv = 10;
			}
			// dB
			else {
				ymax = ceil(fmax / dbdiv) * dbdiv;
				ymin = ymax - (dbdiv * ndbdiv);
				ydiv = ndbdiv;
			}
		}
		else {
			ymax = L1dScale.max;
			ymin = L1dScale.min;
			ydiv = L1dScale.div;
		}
		//printf("%f %f %d\n", ymin, ymax, ydiv);

		// plot

		ev2d_newPage();

		ev2dlib_grid(x1, y1, x2, y2, 10, ydiv);

		double y = y2 + (ic2 - ic1 + 0.8) * h;
		for (int ic = ic1; ic <= ic2; ic++) {
			ev2d_setColorA(rgb[ic]);

			ev2dlib_func2(ndata - 1, pos, F1d[n][ic], ymin, ymax, x1, y1, x2, y2);

			ev2d_drawLine(x2 - 5.0 * h, y, x2 - 2.0 * h, y);
			ev2d_drawString(x2 - 1.5 * h, y - 0.4 * h, h, component[ic][0]);
			y -= h;
		}
		ev2d_setColor(0, 0, 0);

		// comment

		// y-axis
		strcpy(fmt, (db ? "%.1f" : "%.2e"));
		sprintf(str, fmt, ymax);
		ev2d_drawString(x1 - 0.8 * strlen(str) * h, y2 - 0.3 * h, h, str);
		sprintf(str, fmt, ymin);
		ev2d_drawString(x1 - 0.8 * strlen(str) * h, y1 - 0.3 * h, h, str);
		//if (!db) ev2d_drawString(x1 - 1.0 * h, (y1 + y2) / 2 - 0.4 * h, h, "0");
		strcpy(str, component[ic1][1 + db]);
		ev2d_drawString(x1 - 0.8 * strlen(str) * h, y2 - 1.5 * h, h, str);

		// x-axis
		y = y1 - 1.0 * h;
		sprintf(str, "%c[m]", L1d[n].direction);
		ev2d_drawString((x1 + x2) / 2 - 1.5 * h, y, h, str);
		sprintf(str, "%g", pos[0]);
		ev2d_drawString(x1, y, h, str);
		sprintf(str, "%g", pos[ndata - 1]);
		ev2d_drawString(x2 - (0.8 * strlen(str) - 1.0) * h, y, h, str);

		// title
		ev2d_drawString(x1, y2 + 1.7 * h, h, Title);

		// position, max, min
		sprintf(fmt, "%s max=%s%s min=%s%s", "%s", (db ? "%.3f" : "%.3e"), "%s", (db ? "%.3f" : "%.3e"), "%s");
		sprintf(str, fmt, str2, fmax, component[ic1][1 + db], fmin, component[ic1][1 + db]);
		ev2d_drawString(x1, y2 + 0.5 * h, h, str);

		// log
		if (L1dLog) {
			fprintf(fp, "   No.          %c[m]          V[V]", L1d[n].direction);
			for (int ic = 1; ic < ncompo; ic++) {
				strcpy(str, component[ic][0]);
				strcat(str, component[ic][1 + db]);
				fprintf(fp, "%14s", str);
			}
			fprintf(fp, "\n");
			strcpy(fmt, (db ? "%14.5f" : "%14.5e"));
			for (int idata = 0; idata < ndata; idata++) {
				fprintf(fp, "%6d%14.5e%14.5e", idata, pos[idata], F1d[n][0][idata]);
				for (int ic = 1; ic < ncompo; ic++) {
					fprintf(fp, fmt, F1d[n][ic][idata]);
				}
				fprintf(fp, "\n");
			}
		}
	}

	// close
	fclose(fp);
}
