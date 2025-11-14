/*
plotP2d.c

plot field on planes (2D + 3D)
*/

#include "ost.h"
#include "ev.h"
#include "ost_prototype.h"

void plotP2d(void)
{
	const int    ncompo = 10;
	const double dbspan = 40;
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
	const int p2d = P2dFigure[0];
	const int p3d = P2dFigure[1];
	char str[BUFSIZ], fmt[BUFSIZ], title[BUFSIZ];

	// open
	FILE *fp;
	if ((fp = fopen(FN_2d, "w")) == NULL) {
		fprintf(stderr, "*** file %s open error.\n", FN_2d);
		return;
	}

	// loop on planes
	for (int n = 0; n < NP2d; n++) {

		// dB (V : linear only)
		int db = P2dScale.db && strcmp(P2d[n].component, "V");

		// component
		int icomponent = 0;
		for (int ic = 0; ic < ncompo; ic++) {
			if (!strcmp(P2d[n].component, component[ic][0])) {
				icomponent = ic;
				break;
			}
		}
		//printf("%d\n", icomponent);

		// node position
		int i1 = 0, i2 = 0, j1 = 0, j2 = 0;
		double *inode = NULL, *jnode = NULL;
		double pos0 = 0;
		char ichar = ' ', jchar = ' ';
		if      (P2d[n].direction == 'X') {
			// Y-Z
			pos0 = Xn[P2d[n].posid];
			i2 = Ny;
			j2 = Nz;
			inode = Yn;
			jnode = Zn;
			ichar = 'Y';
			jchar = 'Z';
		}
		else if (P2d[n].direction == 'Y') {
			// X-Z
			pos0 = Yn[P2d[n].posid];
			i2 = Nx;
			j2 = Nz;
			inode = Xn;
			jnode = Zn;
			ichar = 'X';
			jchar = 'Z';
		}
		else if (P2d[n].direction == 'Z') {
			// X-Y
			pos0 = Zn[P2d[n].posid];
			i2 = Nx;
			j2 = Ny;
			inode = Xn;
			jnode = Yn;
			ichar = 'X';
			jchar = 'Y';
		}
		if (P2dZoomin) {
			i1 = nearest(P2dZoom[0][0], 0, i2, inode);
			i2 = nearest(P2dZoom[0][1], 0, i2, inode);
			j1 = nearest(P2dZoom[1][0], 0, j2, jnode);
			j2 = nearest(P2dZoom[1][1], 0, j2, jnode);
		}
		//printf("%d %d %d %d\n", i1, i2, j1, j2);

		// alloc
		double ***f2d = (double ***)malloc(ncompo * sizeof(double **));
		for (int ic = 0; ic < ncompo; ic++) {
			f2d[ic] = (double **)malloc((i2 - i1 + 1) * sizeof(double *));
			for (int i = 0; i <= i2 - i1; i++) {
				f2d[ic][i] = (double *)malloc((j2 - j1 + 1) * sizeof(double));
			}
		}

		// set array
		for (int ic = 0; ic < ncompo; ic++) {
			for (int i = 0; i <= i2 - i1; i++) {
			for (int j = 0; j <= j2 - j1; j++) {
				if (ic == 0) {
					f2d[ic][i][j] = F2d[n][ic][i1 + i][j1 + j];
				}
				else {
					f2d[ic][i][j] = fabs(F2d[n][ic][i1 + i][j1 + j]);
					if (db) {
						f2d[ic][i][j] = 20 * log10(MAX(f2d[ic][i][j], eps));
					}
				}
			}
			}
		}

		// dara : min, max
		double fmin = f2d[icomponent][0][0];
		double fmax = fmin;
		for (int i = 0; i <= i2 - i1; i++) {
		for (int j = 0; j <= j2 - j1; j++) {
			fmax = MAX(fmax, f2d[icomponent][i][j]);
			fmin = MIN(fmin, f2d[icomponent][i][j]);
		}
		}
		//printf("%f %f\n", fmin, fmax);

		// scale : min, max
		double dmin = 0, dmax = 0;
		if (!P2dScale.user) {
			dmax = fmax;
			if (db) {
				dmin = fmax - dbspan;
			}
			else {
				dmin = ((icomponent == 1) || (icomponent == 5)) ? 0 : fmin;  // E or D -> min = 0
			}
		}
		else {
			dmax = P2dScale.max;
			dmin = P2dScale.min;
		}
		//printf("%f %f\n", dmin, dmax);

		// layout
		const double w0 = Width2d / 2.0;
		const double h0 = Height2d / 2.0;
		const double h = Fontsize2d;

		const double sx1 = inode[i1];
		const double sx2 = inode[i2];
		const double sy1 = jnode[j1];
		const double sy2 = jnode[j2];

		const double sx0 = (sx1 + sx2) / 2;
		const double sy0 = (sy1 + sy2) / 2;

		const double xfctr = 0.75 * Width2d  / fabs(sx2 - sx1);
		const double yfctr = 0.85 * Height2d / fabs(sy2 - sy1);
		const double fctr = (xfctr < yfctr) ? xfctr : yfctr;

		// contour
		if (p2d) {
			ev2d_newPage();

			double *si = (double *)malloc((i2 - i1 + 1) * sizeof(double));
			double *sj = (double *)malloc((j2 - j1 + 1) * sizeof(double));
			for (int i = 0; i <= i2 - i1; i++) {
				si[i] = w0 + fctr * (inode[i + i1] - sx0);
			}
			for (int j = 0; j <= j2 - j1; j++) {
				sj[j] = h0 + fctr * (jnode[j + j1] - sy0);
			}

			const int mode = (P2dContour == 0) ? 0 : (P2dContour == 1) ? 2 : (P2dContour == 2) ? 1 : 3;
			ev2dlib_contour(i2 - i1, j2 - j1, si, sj, f2d[icomponent], dmin, dmax, mode);

			ev2d_setColor(0, 0, 0);
			free(si);
			free(sj);
		}
		if (p3d) {
			ev3d_newPage();

			ev3d_index(0);
			for (int i = 0; i < i2 - i1; i++) {
			for (int j = 0; j < j2 - j1; j++) {
				const double rx1 = inode[i1 + i + 0];
				const double rx2 = inode[i1 + i + 1];
				const double ry1 = jnode[j1 + j + 0];
				const double ry2 = jnode[j1 + j + 1];
				double v = (f2d[icomponent][i + 0][j + 0]
				          + f2d[icomponent][i + 1][j + 0]
				          + f2d[icomponent][i + 1][j + 1]
				          + f2d[icomponent][i + 0][j + 1]) / 4;
				v = (v - dmin) / (dmax - dmin);
				ev3d_setColorV(v, ((P2dContour == 0) || (P2dContour == 1)));
				if ((P2d[n].direction == 'X') || (P2d[n].direction == 'Z')) {
					ev3d_fillRectangle(P2d[n].direction, pos0, rx1, ry1, rx2, ry2);
				}
				else if (P2d[n].direction == 'Y') {
					ev3d_fillRectangle(P2d[n].direction, pos0, ry1, rx1, ry2, rx2);
				}
			}
			}

			ev3d_setColor(0, 0, 0);
			ev3d_index(2);
			ev3d_drawBox(Xn[0], Yn[0], Zn[0], Xn[Nx], Yn[Ny], Zn[Nz]);
		}

		// objects
		for (int ig = 0; ig < NGline; ig++) {
			if (((P2dObject[0] == 0) && (MGline[ig] == 1)) ||
			    ((P2dObject[1] == 0) && (MGline[ig] == 2))) continue;
			if (p2d) {
				int n1 = 0, n2 = 0;
				if      (P2d[n].direction == 'X') {n1 = 1; n2 = 2;}
				else if (P2d[n].direction == 'Y') {n1 = 0; n2 = 2;}
				else if (P2d[n].direction == 'Z') {n1 = 0; n2 = 1;}
				const double gx1 = w0 + fctr * (Gline[ig][0][n1] - sx0);
				const double gx2 = w0 + fctr * (Gline[ig][1][n1] - sx0);
				const double gy1 = h0 + fctr * (Gline[ig][0][n2] - sy0);
				const double gy2 = h0 + fctr * (Gline[ig][1][n2] - sy0);
				ev2d_drawLine(gx1, gy1, gx2, gy2);
			}
			if (p3d) {
				ev3d_index(1);
				ev3dlib_drawLineA(Gline[ig]);
			}
		}

		// position, max, min
		sprintf(fmt, "%s max=%s%s min=%s%s", "%c[m]=%g", (db ? "%.3f" : "%.3e"), "%s", (db ? "%.3f" : "%.3e"), "%s");
		sprintf(title, fmt, P2d[n].direction, pos0, fmax, component[icomponent][1 + db], fmin, component[icomponent][1 + db]);

		if (p2d) {
			const double x1 = w0 + fctr * (sx1 - sx0);
			const double x2 = w0 + fctr * (sx2 - sx0);
			const double y1 = h0 + fctr * (sy1 - sy0);
			const double y2 = h0 + fctr * (sy2 - sy0);

			// color sample
			ev2dlib_sample(x2 + 0.5 * h, y1, x2 + 1.5 * h, y1 + 8.0 * h, (P2dContour == 0) || (P2dContour == 1));
			strcpy(fmt, (db ? "%.3f" : "%.3e"));
			sprintf(str, "%s%s", component[icomponent][0], component[icomponent][1 + db]);
			ev2d_drawString(x2 + 1.0 * h, y1 + 9.0 * h, h, str);
			sprintf(str, fmt, dmax);
			ev2d_drawString(x2 + 1.6 * h, y1 + 7.7 * h, (int)(0.8 * h), str);
			sprintf(str, fmt, dmin);
			ev2d_drawString(x2 + 1.6 * h, y1 - 0.3 * h, (int)(0.8 * h), str);

			// x-span
			sprintf(str, "%c[m]", ichar);
			ev2d_drawString((x1 + x2) / 2 - 2.0 * h, y1 - 1.2 * h, h, str);
			sprintf(str, "%.5g", inode[i1]);
			ev2d_drawString(x1,                                   y1 - 1.2 * h, h, str);
			sprintf(str, "%.5g", inode[i2]);
			ev2d_drawString(x2 - 0.8 * strlen(str) * h,           y1 - 1.2 * h, h, str);

			// y-span
			sprintf(str, "%c[m]", jchar);
			ev2d_drawString(x1 - 3.5 * h, (y1 + y2) / 2 - 0.4 * h, h, str);
			sprintf(str, "%.5g", jnode[j1]);
			ev2d_drawString(x1 - 0.8 * strlen(str) * h - 0.3 * h, y1 - 0.3 * h, h, str);
			sprintf(str, "%.5g", jnode[j2]);
			ev2d_drawString(x1 - 0.8 * strlen(str) * h - 0.3 * h, y2 - 0.3 * h, h, str);

			// title
			ev2d_drawString(x1, y2 + 1.7 * h, h, Title);
			ev2d_drawString(x1, y2 + 0.5 * h, h, title);
		}
		if (p3d) {
			ev3d_drawTitle(Title);
			ev3d_drawTitle(title);
		}

		// log (all components)
		if (P2dLog) {
			fprintf(fp, "   No.   No.          %c[m]          %c[m]          V[V]", ichar, jchar);
			for (int ic = 1; ic < ncompo; ic++) {
				strcpy(str, component[ic][0]);
				strcat(str, component[ic][1 + db]);
				fprintf(fp, "%14s", str);
			}
			fprintf(fp, "\n");
			strcpy(fmt, (db ? "%14.5f" : "%14.5e"));
			for (int i = 0; i <= i2 - i1; i++) {
			for (int j = 0; j <= j2 - j1; j++) {
				fprintf(fp, "%6d%6d%14.5e%14.5e", i1 + i, j1 + j, inode[i1 + i], jnode[j1 + j]);
				fprintf(fp, "%14.5e", f2d[0][i][j]);
				for (int ic = 1; ic < ncompo; ic++) {
					fprintf(fp, fmt, f2d[ic][i][j]);
				}
				fprintf(fp, "\n");
			}
			}
		}

		// free
		for (int ic = 0; ic < ncompo; ic++) {
			for (int i = 0; i <= i2 - i1; i++) {
				free(f2d[ic][i]);
			}
			free(f2d[ic]);
		}
		free(f2d);
	}

	// close
	fclose(fp);
}
