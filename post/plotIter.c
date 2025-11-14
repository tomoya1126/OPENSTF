/*
plotIter.c

plot iteration (2D)
*/

#include "ost.h"
#include "ev.h"

void plotIter(void)
{
	if (NumIter < 1) return;

	char   str[BUFSIZ];
	const int ylog = 8;

	// layout
	const double x1 = 0.14 * Width2d;
	const double x2 = 0.95 * Width2d;
	const double y1 = 0.10 * Height2d;
	const double y2 = 0.90 * Height2d;
	const double h = Fontsize2d;

	// min, max
	double fmax = 0;
	for (int n = 0; n < NumIter; n++) {
		fmax = MAX(fmax, Residual[n]);
	}
	const double ymax = ceil(log10(fmax));
	const double ymin = ymax - ylog;
	//printf("%f %f\n", ymax, ymin);

	// plot
	ev2d_newPage();

	// grid
	ev2dlib_grid(x1, y1, x2, y2, 10, ylog);

	// iteration
	for (int n = 0; n < NumIter - 1; n++) {
		double px1 = x1 + (x2 - x1) * (n + 0) / (NumIter - 1);
		double px2 = x1 + (x2 - x1) * (n + 1) / (NumIter - 1);
		double py1 = MAX(log10(MAX(Residual[n + 0], EPS2)), ymin);
		double py2 = MAX(log10(MAX(Residual[n + 1], EPS2)), ymin);
		py1 = y1 + (y2 - y1) * (py1 - ymin) / (ymax - ymin);
		py2 = y1 + (y2 - y1) * (py2 - ymin) / (ymax - ymin);
		ev2d_drawLine(px1, py1, px2, py2);
	}

	// comment
	ev2d_drawString(x1, y2 + 0.5 * h, h, Title);

	// x-axis
	ev2d_drawString(x1 - 0.0 * h, y1 - 1.0 * h, h, "0");
	sprintf(str, "%d", NumIter - 1);
	ev2d_drawString(x2 - 1.5 * h, y1 - 1.0 * h, h, str);
	ev2d_drawString((x1 + x2) / 2 - 2.0 * h, y1 - 1.0 * h, h, "iteration");

	// y-axis
	ev2d_drawString(x1 - 6.5 * h, y2 - 1.5 * h, h, "Residual");
	sprintf(str, "%.0e", pow(10, ymax));
	ev2d_drawString(x1 - 0.8 * strlen(str) * h, y2 - 0.3 * h, h, str);
	sprintf(str, "%.0e", pow(10, ymin));
	ev2d_drawString(x1 - 0.8 * strlen(str) * h, y1 - 0.3 * h, h, str);
}
