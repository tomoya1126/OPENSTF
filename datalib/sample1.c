/*
sample1.c
sample program of OpenSTF datalib
*/

#include "ost_datalib.h"

int main()
{
	// (1) initialize

	ost_init();

	// (2) title

	ost_title("sample1");

	// (3) mesh

	ost_xsection(2, -5.0, +5.0);
	ost_xdivision(1, 50);

	ost_ysection(2, -5.0, +5.0);
	ost_ydivision(1, 50);

	ost_zsection(2, -5.0, +5.0);
	ost_zdivision(1, 50);

	// (4) volt

	ost_volt(-1);
	ost_volt(+1);

	// (5) dielectric

	ost_epsr(2.0);

	// (6) geometry

	ost_unit6(2, 1, 1, -2.0, +2.0, -2.0, +2.0, -2.0, +2.0);		// dielectric
	ost_unit6(1, 1, 1, -2.0, +2.0, -2.0, +2.0, -2.0, -2.0);		// -electrode
	ost_unit6(1, 2, 1, -2.0, +2.0, -2.0, +2.0, +2.0, +2.0);		// +electrode

	// (7) solver

	ost_solver(1.97, 3000, 100, 1e-5);

	// (8) post

	ost_plotiter();

	ost_plot1d("E", "Z", 0, 0);
	//ost_1ddb();
	//ost_1dscale(-50, 10, 6);

	ost_plot2d("E", "X", 0);
	//ost_2dfigure(1, 1);
	//ost_2ddb();
	//ost_2dscale(-50, 10, 0);
	//ost_2dobject(1, 1);

	// (9) output

	ost_outdata("sample1.ost");

	return 0;
}
