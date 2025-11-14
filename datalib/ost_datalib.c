/*
ost_datalib.c
OpenSTF datalib
*/

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <stddef.h>

#define PROGRAM "OpenSTF 4 2"

int _MAXSECTION;
int _MAXUNIT;
int _MAXL1D;
int _MAXP2D;

char     _title[BUFSIZ];
int      _xsections, _ysections, _zsections;
int      _xdivs, _ydivs, _zdivs;
double  *_xsection, *_ysection, *_zsection;
int     *_xdiv, *_ydiv, *_zdiv;
int      _volts;
double   _volt[256];
char     _volt_name[256][BUFSIZ];
int      _epsrs;
double   _epsr[256];
char     _epsr_name[256][BUFSIZ];
int      _units;
int     *_unit_type, *_unit_pid, *_unit_shape;
double (*_unit_pos)[8];
char   (*_unit_name)[BUFSIZ];
int      _maxiter, _nout;
double   _omega, _convergence;

int      _plotiter;
int      _plot1ds;
char   (*_1dcomponent)[3], (*_1ddirection)[3];
double  *_1dpos1, *_1dpos2;
int      _1ddb;
double   _1dscalemin, _1dscalemax;
int      _1dscale, _1dscalediv;
int      _1dlog;
int      _plot2ds;
char   (*_2dcomponent)[3], (*_2ddirection)[3];
double  *_2dpos0;
int      _2dfigure[2];
int      _2ddb;
int      _2dscale;
double   _2dscalemin, _2dscalemax;
int      _2dcontour;
int      _2dobject[2];
int      _2dzoomin;
double   _2dzoom[2][2];
int      _2dlog;


void ost_init(void)
{
	_MAXSECTION = 100;
	_MAXUNIT    = 10000;
	_MAXL1D     = 100;
	_MAXP2D     = 100;

	strcpy(_title, "");
	_xsections = _ysections = _zsections = 0;
	_xdivs = _ydivs = _zdivs = 0;
	_epsrs = _volts = _units = 0;

	_omega       = 1.97;
	_maxiter     = 3000;
	_nout        = 100;
	_convergence = 1e-5;

	_xsection  = (double *)malloc((_MAXSECTION + 1) * sizeof(double));
	_ysection  = (double *)malloc((_MAXSECTION + 1) * sizeof(double));
	_zsection  = (double *)malloc((_MAXSECTION + 1) * sizeof(double));
	_xdiv      =    (int *)malloc( _MAXSECTION      * sizeof(int));
	_ydiv      =    (int *)malloc( _MAXSECTION      * sizeof(int));
	_zdiv      =    (int *)malloc( _MAXSECTION      * sizeof(int));

	_unit_type  =            (int *)malloc(_MAXUNIT * sizeof(int));
	_unit_pid   =            (int *)malloc(_MAXUNIT * sizeof(int));
	_unit_shape =            (int *)malloc(_MAXUNIT * sizeof(int));
	_unit_pos   =    (double (*)[8])malloc(_MAXUNIT * 8 * sizeof(double));
	_unit_name  = (char (*)[BUFSIZ])malloc(_MAXUNIT * BUFSIZ * sizeof(char));

	 _plotiter   = 0;
	 _plot1ds    = 0;
	_1dcomponent = (char (*)[3])malloc(_MAXL1D * 3 * sizeof(char));
	_1ddirection = (char (*)[3])malloc(_MAXL1D * 3 * sizeof(char));
	_1dpos1      =    (double *)malloc(_MAXL1D     * sizeof(double));
	_1dpos2      =    (double *)malloc(_MAXL1D     * sizeof(double));
	_1ddb        = 0;
	_1dscale     = 0;
	_1dlog       = 1;
	_plot2ds     = 0;
	_2dcomponent = (char (*)[3])malloc(_MAXP2D * 3 * sizeof(char));
	_2ddirection = (char (*)[3])malloc(_MAXP2D * 3 * sizeof(char));
	_2dpos0      =    (double *)malloc(_MAXP2D     * sizeof(double));
	_2dfigure[0] = _2dfigure[1] = 1;
	_2ddb        = 0;
	_2dscale     = 0;
	_2dcontour   = 0;
	_2dobject[0] = _2dobject[1] = 1;
	_2dzoomin    = 0;
	_2dlog       = 1;
}


void ost_section_size(int size)
{
	_MAXSECTION = size;
	_xsection = (double *)realloc(_xsection, (_MAXSECTION + 1) * sizeof(double));
	_ysection = (double *)realloc(_ysection, (_MAXSECTION + 1) * sizeof(double));
	_zsection = (double *)realloc(_zsection, (_MAXSECTION + 1) * sizeof(double));
	_xdiv     =    (int *)realloc(_xdiv,      _MAXSECTION      * sizeof(int));
	_ydiv     =    (int *)realloc(_ydiv,      _MAXSECTION      * sizeof(int));
	_zdiv     =    (int *)realloc(_zdiv,      _MAXSECTION      * sizeof(int));
}
void ost_unit_size(int size)
{
	_MAXUNIT = size;
	_unit_type  =            (int *)realloc(_unit_type,  _MAXUNIT * sizeof(int));
	_unit_pid   =            (int *)realloc(_unit_pid,   _MAXUNIT * sizeof(int));
	_unit_shape =            (int *)realloc(_unit_shape, _MAXUNIT * sizeof(int));
	_unit_pos   =    (double (*)[8])realloc(_unit_pos,   _MAXUNIT * 8 * sizeof(double));
	_unit_name  = (char (*)[BUFSIZ])realloc(_unit_name,  _MAXUNIT * BUFSIZ * sizeof(char));
}
void ost_1d_size(int size)
{
	_MAXL1D = size;
	_1dcomponent = (char (*)[3])realloc(_1dcomponent, _MAXL1D * 3 * sizeof(char));
	_1ddirection = (char (*)[3])realloc(_1ddirection, _MAXL1D * 3 * sizeof(char));
	_1dpos1      =    (double *)realloc(_1dpos1,      _MAXL1D     * sizeof(double));
	_1dpos2      =    (double *)realloc(_1dpos2,      _MAXL1D     * sizeof(double));
}
void ost_2d_size(int size)
{
	_MAXP2D = size;
	_2dcomponent = (char (*)[3])realloc(_2dcomponent, _MAXP2D * 3 * sizeof(char));
	_2ddirection = (char (*)[3])realloc(_2ddirection, _MAXP2D * 3 * sizeof(char));
	_2dpos0      =    (double *)realloc(_2dpos0,      _MAXP2D     * sizeof(double));
}


void ost_title(const char *title) {strcpy(_title, title);}


void ost_xsection1(double x) {_xsection[_xsections++] = x;}
void ost_ysection1(double y) {_ysection[_ysections++] = y;}
void ost_zsection1(double z) {_zsection[_zsections++] = z;}
void ost_xdivision1(int n) {_xdiv[_xdivs++] = (n != 0) ? n : 1;}
void ost_ydivision1(int n) {_ydiv[_ydivs++] = (n != 0) ? n : 1;}
void ost_zdivision1(int n) {_zdiv[_zdivs++] = (n != 0) ? n : 1;}


void ost_xsection(int n, ...)
{
	va_list ap;
	va_start(ap, n);
	for (int i = 0; i < n; i++) {
		_xsection[i] = va_arg(ap, double);
	}
	va_end(ap);
	_xsections = n;
}


void ost_ysection(int n, ...)
{
	va_list ap;
	va_start(ap, n);
	for (int j = 0; j < n; j++) {
		_ysection[j] = va_arg(ap, double);
	}
	va_end(ap);
	_ysections = n;
}


void ost_zsection(int n, ...)
{
	va_list ap;
	va_start(ap, n);
	for (int k = 0; k < n; k++) {
		_zsection[k] = va_arg(ap, double);
	}
	va_end(ap);
	_zsections = n;
}


void ost_xdivision(int n, ...)
{
	va_list ap;
	va_start(ap, n);
	for (int i = 0; i < n; i++) {
		_xdiv[i] = va_arg(ap, int);
		if (_xdiv[i] == 0) _xdiv[i] = 1;
	}
	va_end(ap);
	_xdivs = n;
}


void ost_ydivision(int n, ...)
{
	va_list ap;
	va_start(ap, n);
	for (int j = 0; j < n; j++) {
		_ydiv[j] = va_arg(ap, int);
		if (_ydiv[j] == 0) _ydiv[j] = 1;
	}
	va_end(ap);
	_ydivs = n;
}


void ost_zdivision(int n, ...)
{
	va_list ap;
	va_start(ap, n);
	for (int k = 0; k < n; k++) {
		_zdiv[k] = va_arg(ap, int);
		if (_zdiv[k] == 0) _zdiv[k] = 1;
	}
	va_end(ap);
	_zdivs = n;
}


void ost_volt(double volt)
{
	if (_volts < 256) {
		_volt[_volts] = volt;
		strcpy(_volt_name[_volts], "");
		_volts++;
	}
}


void ost_volt_name(const char name[])
{
	if (_volts > 0) {
		strcpy(_volt_name[_volts - 1], name);
	}
}


void ost_epsr(double epsr)
{
	if (_epsrs < 256) {
		_epsr[_epsrs] = epsr;
		strcpy(_epsr_name[_epsrs], "");
		_epsrs++;
	}
}


void ost_epsr_name(const char name[])
{
	if (_epsrs > 0) {
		strcpy(_epsr_name[_epsrs - 1], name);
	}
}


void ost_unit(int type, int pid, int shape, const double pos[])
{
	if ((type < 1) || (2 < type)) return;
	if (pid < 1) return;
	if (shape < 1) return;
	if (_units >= _MAXUNIT) return;

	int narray = (shape == 31) || (shape == 32) || (shape == 33) ? 8 : 6;
	_unit_type[_units]  = type;
	_unit_pid[_units]   = pid;
	_unit_shape[_units] = shape;
	memcpy(_unit_pos[_units], pos, narray * sizeof(double));

	_units++;
}


void ost_unit6(int type, int pid, int shape, double x1, double x2, double y1, double y2, double z1, double z2)
{
	double pos[8];
	pos[0] = x1;
	pos[1] = x2;
	pos[2] = y1;
	pos[3] = y2;
	pos[4] = z1;
	pos[5] = z2;
	pos[6] =
	pos[7] = 0;

	ost_unit(type, pid, shape, pos);
}


void ost_unit_name(const char name[])
{
	if (_units > 0) {
		strcpy(_unit_name[_units - 1], name);
	}
}


void ost_solver(double omega, int maxiter, int nout, double convergence)
{
	_omega       = omega;
	_maxiter     = maxiter;
	_nout        = nout;
	_convergence = convergence;
}


void ost_plotiter(void) {_plotiter = 1;}


void ost_plot1d(const char component[], const char direction[], double pos1, double pos2)
{
	if (_plot1ds < _MAXL1D) {
		strcpy(_1dcomponent[_plot1ds], component);
		strcpy(_1ddirection[_plot1ds], direction);
		_1dpos1[_plot1ds] = pos1;
		_1dpos2[_plot1ds] = pos2;
		_plot1ds++;
	}
}
void ost_1ddb(void)
{
	_1ddb = 1;
}
void ost_1dscale(double min, double max, int div)
{
	_1dscale = 1;
	_1dscalemin = min;
	_1dscalemax = max;
	_1dscalediv = div;
}
void ost_1dlog(int i1)
{
	_1dlog = i1;
}


void ost_plot2d(const char component[], const char direction[], double pos0)
{
	if (_plot2ds < _MAXP2D) {
		strcpy(_2dcomponent[_plot2ds], component);
		strcpy(_2ddirection[_plot2ds], direction);
		_2dpos0[_plot2ds] = pos0;
		_plot2ds++;
	}
}
void ost_2dfigure(int i1, int i2)
{
	_2dfigure[0] = i1;
	_2dfigure[1] = i2;
}
void ost_2ddb(void)
{
	_2ddb = 1;
}
void ost_2dscale(double min, double max)
{
	_2dscale = 1;
	_2dscalemin = min;
	_2dscalemax = max;
}
void ost_2dcontour(int i1)
{
	_2dcontour = i1;
}
void ost_2dobject(int i1, int i2)
{
	_2dobject[0] = i1;
	_2dobject[1] = i2;
}
void ost_2dzoom(double x1, double x2, double y1, double y2)
{
	_2dzoomin = 1;
	_2dzoom[0][0] = x1;
	_2dzoom[0][1] = x2;
	_2dzoom[1][0] = y1;
	_2dzoom[1][1] = y2;
}
void ost_2dlog(int i)
{
	_2dlog = i;
}


void ost_outdata(const char fn[])
{
	FILE  *fp;
	if ((fp = fopen(fn, "w")) == NULL) {fprintf(stderr, "*** output file %s open error.\n", fn); exit(0);}

	fprintf(fp, "%s\n", PROGRAM);

	if (strcmp(_title, "")) {
		fprintf(fp, "title = %s\n", _title);
	}

	if (_xsections != _xdivs + 1) {fprintf(stderr, "*** invalid X-sections. (%d != %d)\n", _xsections, _xdivs + 1); exit(0);}
	if (_xdivs > 0) {
		fprintf(fp, "%s", "xmesh = ");
		for (int i = 0; i < _xdivs; i++) {
			fprintf(fp, "%g %d ", _xsection[i], _xdiv[i]);
		}
		fprintf(fp, "%g\n", _xsection[_xdivs]);
	}

	if (_ysections != _ydivs + 1) {fprintf(stderr, "*** invalid Y-sections. (%d != %d)\n", _ysections, _ydivs + 1); exit(0);}
	if (_ydivs > 0) {
		fprintf(fp, "%s", "ymesh = ");
		for (int j = 0; j < _ydivs; j++) {
			fprintf(fp, "%g %d ", _ysection[j], _ydiv[j]);
		}
		fprintf(fp, "%g\n", _ysection[_ydivs]);
	}

	if (_zsections != _zdivs + 1) {fprintf(stderr, "*** invalid Z-sections. (%d != %d)\n", _zsections, _zdivs + 1); exit(0);}
	if (_zdivs > 0) {
		fprintf(fp, "%s", "zmesh = ");
		for (int k = 0; k < _zdivs; k++) {
			fprintf(fp, "%g %d ", _zsection[k], _zdiv[k]);
		}
		fprintf(fp, "%g\n", _zsection[_zdivs]);
	}

	for (int n = 0; n < _volts; n++) {
		fprintf(fp, "volt = %g %s\n", _volt[n], _volt_name[n]);
	}

	for (int n = 0; n < _epsrs; n++) {
		fprintf(fp, "epsr = %g %s\n", _epsr[n], _epsr_name[n]);
	}

	for (int n = 0; n < _units; n++) {
		if ((_unit_type[n] < 1) || (_unit_type[n] > 2)) {fprintf(stderr, "*** invalid type : geometry number = %d\n", n + 1); continue;}
		if ((_unit_type[n] == 1) && (_unit_pid[n] > _volts)) {fprintf(stderr, "*** too large volt id : geometry number = %d\n", n + 1); continue;}
		if ((_unit_type[n] == 2) && (_unit_pid[n] > _epsrs)) {fprintf(stderr, "*** too large epsr id : geometry number = %d\n", n + 1); continue;}
		fprintf(fp, "geometry = %d %d %d %g %g %g %g %g %g",
			_unit_type[n], _unit_pid[n], _unit_shape[n], _unit_pos[n][0], _unit_pos[n][1], _unit_pos[n][2], _unit_pos[n][3], _unit_pos[n][4], _unit_pos[n][5]);
		int shape = _unit_shape[n];
		if ((shape == 31) || (shape == 32) || (shape == 33)) {
			fprintf(fp, " %g %g", _unit_pos[n][6], _unit_pos[n][7]);
		}
		fprintf(fp, " %s\n", _unit_name[n]);
	}

	fprintf(fp, "solver = %g %d %d %g\n", _omega, _maxiter, _nout, _convergence);

	if (_plotiter) fprintf(fp, "plotiter = %d\n", _plotiter);
	if (_plot1ds) {
		for (int n = 0; n < _plot1ds; n++) {
			fprintf(fp, "plot1d = %s %s %g %g\n", _1dcomponent[n], _1ddirection[n], _1dpos1[n], _1dpos2[n]);
		}
		fprintf(fp, "1ddb = %d\n", _1ddb);
		if (_1dscale) fprintf(fp, "1dscale = %g %g %d\n", _1dscalemin, _1dscalemax, _1dscalediv);
		fprintf(fp, "1dlog = %d\n", _1dlog);
	}
	if (_plot2ds) {
		for (int n = 0; n < _plot2ds; n++) {
			fprintf(fp, "plot2d = %s %s %g\n", _2dcomponent[n], _2ddirection[n], _2dpos0[n]);
		}
		fprintf(fp, "2dfigure = %d %d\n", _2dfigure[0], _2dfigure[1]);
		fprintf(fp, "2ddb = %d\n", _2ddb);
		if (_2dscale) fprintf(fp, "2dscale = %g %g\n", _2dscalemin, _2dscalemax);
		fprintf(fp, "2dcontour = %d\n", _2dcontour);
		fprintf(fp, "2dobject = %d %d\n", _2dobject[0], _2dobject[1]);
		if (_2dzoomin) fprintf(fp, "2dzoom = %g %g %g %g\n", _2dzoom[0][0], _2dzoom[0][1], _2dzoom[1][0], _2dzoom[1][1]);
		fprintf(fp, "2dlog = %d\n", _2dlog);
	}

	fprintf(fp, "%s\n", "end");

	fflush(fp);

	fclose(fp);

	printf("output file -> %s\n", fn);

	// free
	free(_xsection);
	free(_ysection);
	free(_zsection);
	free(_xdiv);
	free(_ydiv);
	free(_zdiv);
	free(_unit_shape);
	free(_unit_type);
	free(_unit_pid);
	free(_unit_pos);
}
