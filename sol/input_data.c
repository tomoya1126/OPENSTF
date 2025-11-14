/*
input_data.c

input data
*/

#include "ost.h"
#include "ost_prototype.h"

static void setup_cells(int, int, int, int *, int *, int *);
static void setup_node(int, int, int, double *, double *, double *, int *, int *, int *);
static void fitgeometry(void);
static void setup_geomlines(void);

#define MAXTOKEN 1000

int input_data(FILE *fp)
{
	int    ntoken, ngeom, nline;
	//int    version = 0;
	int    nxr = 0, nyr = 0, nzr = 0;
	int    *dxr = NULL, *dyr = NULL, *dzr = NULL;
	double *xr = NULL, *yr = NULL, *zr = NULL;
	char   strline[BUFSIZ], strkey[BUFSIZ], strsave[BUFSIZ];
	char   *token[MAXTOKEN];
	const int array_inc = 10000;		// reduce malloc times
	const char sep[] = " \t";			// separator

	// initialize

	NVolt = 1;
	NEpsr = 1;
	Volt[0] = 0;
	Epsr[0] = 1;

	NGeom = 0;
	Geom = NULL;

	Solver.omega = 1.95;
	Solver.maxiter = 1000;
	Solver.nout = 50;
	Solver.converg = 1e-5;

	Plot3dGeom = 0;

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
				//version = (10 * atoi(token[1])) + atoi(token[2]);
			}
			nline++;
		}
		else if (!strcmp(strkey, "title")) {
			strcpy(Title, strchr(strsave, '=') + 2);
			//strncpy(Title, strchr(strsave, '=') + 2, sizeof(Title));
		}
		else if (!strcmp(strkey, "xmesh")) {
			if ((ntoken < 5) || (ntoken % 2 == 0)) {
				fprintf(stderr, "*** invalid %s data\n", strkey);
				return 1;
			}
			nxr = (ntoken - 3) / 2;
			xr = (double *)malloc((nxr + 1) * sizeof(double));
			dxr = (int *)malloc(nxr * sizeof(int));
			sscanf(token[2], "%lf", &xr[0]);
			for (int i = 0; i < nxr; i++) {
				sscanf(token[2 * i + 3], "%d", &dxr[i]);
				sscanf(token[2 * i + 4], "%lf", &xr[i + 1]);
			}
		}
		else if (!strcmp(strkey, "ymesh")) {
			if ((ntoken < 5) || (ntoken % 2 == 0)) {
				fprintf(stderr, "*** invalid %s data\n", strkey);
				return 1;
			}
			nyr = (ntoken - 3) / 2;
			yr = (double *)malloc((nyr + 1) * sizeof(double));
			dyr = (int *)malloc(nyr * sizeof(int));
			sscanf(token[2], "%lf", &yr[0]);
			for (int j = 0; j < nyr; j++) {
				sscanf(token[2 * j + 3], "%d", &dyr[j]);
				sscanf(token[2 * j + 4], "%lf", &yr[j + 1]);
			}
		}
		else if (!strcmp(strkey, "zmesh")) {
			if ((ntoken < 5) || (ntoken % 2 == 0)) {
				fprintf(stderr, "*** invalid %s data\n", strkey);
				return 1;
			}
			nzr = (ntoken - 3) / 2;
			zr = (double *)malloc((nzr + 1) * sizeof(double));
			dzr = (int *)malloc(nzr * sizeof(int));
			sscanf(token[2], "%lf", &zr[0]);
			for (int k = 0; k < nzr; k++) {
				sscanf(token[2 * k + 3], "%d", &dzr[k]);
				sscanf(token[2 * k + 4], "%lf", &zr[k + 1]);
			}
		}
		else if (!strcmp(strkey, "volt")) {
			if (NVolt >= 256) {
				fprintf(stderr, "*** too many %s data #%d\n", strkey, NVolt + 1);
				return 1;
			}
			Volt[NVolt++] = atof(token[2]);
		}
		else if (!strcmp(strkey, "epsr")) {
			if (NEpsr >= 256) {
				fprintf(stderr, "*** too many %s data #%d\n", strkey, NEpsr + 1);
				return 1;
			}
			Epsr[NEpsr++] = (real_t)atof(token[2]);
		}
		else if (!strcmp(strkey, "geometry")) {
			if (ntoken < 5) {
				fprintf(stderr, "*** invalid %s data #%d\n", strkey, NGeom + 1);
				return 1;
			}
			if (NGeom % array_inc == 0) {
				Geom = (geometry_t *)realloc(Geom, (NGeom + array_inc) * sizeof(geometry_t));
			}
			Geom[NGeom].type  = atoi(token[2]);        // =1/2
			Geom[NGeom].pid   = (id_t)atoi(token[3]);  // =1,2,...
			Geom[NGeom].shape = atoi(token[4]);        // =1,2,...
			switch (Geom[NGeom].shape) {
				case 1:
				case 2:
				case 11:
				case 12:
				case 13:
					ngeom = 6;
					break;
				case 31:
				case 32:
				case 33:
				case 41:
				case 42:
				case 43:
				case 51:
				case 52:
				case 53:
					ngeom = 8;
					break;
				default:
					ngeom = 0;
					break;
			}
			if (ntoken < 5 + ngeom) {
				fprintf(stderr, "*** invalid %s data #%d\n", strkey, NGeom + 1);
				return 1;
			}
			for (int n = 0; n < ngeom; n++) {
				Geom[NGeom].g[n] = atof(token[5 + n]);
			}
			NGeom++;
		}
		else if (!strcmp(strkey, "solver")) {
			if (ntoken > 5) {
				Solver.omega   = atof(token[2]);
				Solver.maxiter = atoi(token[3]);
				Solver.nout    = atoi(token[4]);
				Solver.converg = atof(token[5]);
			}
		}
		else if (!strcmp(strkey, "plot3dgeom")) {
			Plot3dGeom = atoi(token[2]);
		}
	}

	// debug
	//printf("title = %s\n", Title);
	//printf("xmesh = %e", xr[0]); for (int i = 0; i < nxr; i++) printf(" %d %e", dxr[i], xr[i + 1]); printf("\n");
	//printf("ymesh = %e", yr[0]); for (int j = 0; j < nyr; j++) printf(" %d %e", dyr[j], yr[j + 1]); printf("\n");
	//printf("zmesh = %e", zr[0]); for (int k = 0; k < nzr; k++) printf(" %d %e", dzr[k], zr[k + 1]); printf("\n");
	//for (int n = 0; n < NVolt; n++) printf("volt = %d %f\n", n, Volt[n]);
	//for (int n = 0; n < NEpsr; n++) printf("epsr = %d %f\n", n, Epsr[n]);
	//for (int n = 0; n < NGeom; n++) printf("geometry = %d %d %d %d %f %f %f %f %f %f\n", n, Geom[n].type, Geom[n].pid, Geom[n].shape, Geom[n].g[0], Geom[n].g[1], Geom[n].g[2], Geom[n].g[3], Geom[n].g[4], Geom[n].g[5]);
	//printf("solver = %f %d %d %e\n", Solver.omega, Solver.maxiter, Solver.nout, Solver.converg);

	// error check

	if (nxr <= 0) {
		fprintf(stderr, "*** no xmesh data\n");
		return 1;
	}
	if (nyr <= 0) {
		fprintf(stderr, "*** no ymesh data\n");
		return 1;
	}
	if (nzr <= 0) {
		fprintf(stderr, "*** no zmesh data\n");
		return 1;
	}
	for (int i = 0; i < nxr; i++) {
		if ((xr[i] > xr[i + 1]) || (dxr[i] <= 0)) {
			fprintf(stderr, "*** invalid xmesh data\n");
			return 1;
		}
	}
	for (int j = 0; j < nyr; j++) {
		if ((yr[j] > yr[j + 1]) || (dyr[j] <= 0)) {
			fprintf(stderr, "*** invalid ymesh data\n");
			return 1;
		}
	}
	for (int k = 0; k < nzr; k++) {
		if ((zr[k] > zr[k + 1]) || (dzr[k] <= 0)) {
			fprintf(stderr, "*** invalid zmesh data\n");
			return 1;
		}
	}
	if (NVolt < 3) {
		fprintf(stderr, "*** number of volt data < 2\n");
		return 1;
	}
	if ((Solver.maxiter <= 0) || (Solver.nout <= 0)) {
		fprintf(stderr, "*** invalid solver data\n");
		return 1;
	}

	for (int n = 0; n < NEpsr; n++) {
		if (Epsr[n] <= 0) {
			fprintf(stderr, "*** invalid epsr data #%d\n", n + 1);
			return 1;
		}
	}

	for (int n = 0; n < NGeom; n++) {
		if ((Geom[n].type < 1) || (Geom[n].type > 2)) {
			fprintf(stderr, "*** invalid type of geometry data #%d\n", n + 1);
			return 1;
		}
		if (Geom[n].pid < 1) {
			fprintf(stderr, "*** invalid property of geometry data #%d\n", n + 1);
			return 1;
		}
		if (Geom[n].shape < 1) {
			fprintf(stderr, "*** invalid shape of geometry data #%d\n", n + 1);
			return 1;
		}
		if ((Geom[n].type == 1) && (Geom[n].pid > NVolt)) {
			fprintf(stderr, "*** invalid volt of geometry data #%d\n", n + 1);
			return 1;
		}
		if ((Geom[n].type == 2) && (Geom[n].pid > NEpsr)) {
			fprintf(stderr, "*** invalid epsr of geometry data #%d\n", n + 1);
			return 1;
		}
	}

	// number of cells
	setup_cells(nxr, nyr, nzr, dxr, dyr, dzr);

	// node
	setup_node(nxr, nyr, nzr, xr, yr, zr, dxr, dyr, dzr);

	// fit geometry without thickness
	fitgeometry();

	// geometry lines
	setup_geomlines();

	// free
	free(xr);
	free(yr);
	free(zr);
	free(dxr);
	free(dyr);
	free(dzr);

	return 0;
}


// number of cells
static void setup_cells(int nxr, int nyr, int nzr, int *dxr, int *dyr, int *dzr)
{
	int xsum = 0;
	for (int i = 0; i < nxr; i++) {
		xsum += dxr[i];
	}
	Nx = xsum;

	int ysum = 0;
	for (int j = 0; j < nyr; j++) {
		ysum += dyr[j];
	}
	Ny = ysum;

	int zsum = 0;
	for (int k = 0; k < nzr; k++) {
		zsum += dzr[k];
	}
	Nz = zsum;
}

// node
static void setup_node(int nxr, int nyr, int nzr, double *xr, double *yr, double *zr, int *dxr, int *dyr, int *dzr)
{
	if ((nxr <= 0) || (nyr <= 0) || (nzr <= 0)) return;

	Xn = (double *)malloc((Nx + 1) * sizeof(double));
	Yn = (double *)malloc((Ny + 1) * sizeof(double));
	Zn = (double *)malloc((Nz + 1) * sizeof(double));

	int xid = 0;
	for (int mx = 0; mx < nxr; mx++) {
		double dx = (xr[mx + 1] - xr[mx]) / dxr[mx];
		for (int i = 0; i < dxr[mx]; i++) {
			Xn[xid++] = xr[mx] + (i * dx);
		}
	}
	Xn[xid] = xr[nxr];

	int yid = 0;
	for (int my = 0; my < nyr; my++) {
		double dy = (yr[my + 1] - yr[my]) / dyr[my];
		for (int j = 0; j < dyr[my]; j++) {
			Yn[yid++] = yr[my] + (j * dy);
		}
	}
	Yn[yid] = yr[nyr];

	int zid = 0;
	for (int mz = 0; mz < nzr; mz++) {
		double dz = (zr[mz + 1] - zr[mz]) / dzr[mz];
		for (int k = 0; k < dzr[mz]; k++) {
			Zn[zid++] = zr[mz] + (k * dz);
		}
	}
	Zn[zid] = zr[nzr];

	// debug
	//for (int i = 0; i <= Nx; i++) printf("Xn[%d]=%.5f\n", i, Xn[i] * 1e3);
	//for (int j = 0; j <= Ny; j++) printf("Yn[%d]=%.5f\n", j, Yn[j] * 1e3);
	//for (int k = 0; k <= Nz; k++) printf("Zn[%d]=%.5f\n", k, Zn[k] * 1e3);
}


// fit geometry without thickness to the nearest node
static void fitgeometry(void)
{
	if ((Nx <= 0) || (Ny <= 0) || (Nz <= 0)) return;

	double d0 = EPS * (
		fabs(Xn[Nx] - Xn[0]) +
		fabs(Yn[Ny] - Yn[0]) +
		fabs(Zn[Nz] - Zn[0]));

	for (int n = 0; n < NGeom; n++) {
		int    shape = Geom[n].shape;
		double *g = Geom[n].g;

		if      ((shape == 1) || (shape == 2)) {
			if (fabs(g[0] - g[1]) < d0) {
				int i = nearest(g[0], 0, Nx, Xn);
				g[0] = g[1] = Xn[i];
			}
			if (fabs(g[2] - g[3]) < d0) {
				int j = nearest(g[2], 0, Ny, Yn);
				g[2] = g[3] = Yn[j];
			}
			if (fabs(g[4] - g[5]) < d0) {
				int k = nearest(g[4], 0, Nz, Zn);
				g[4] = g[5] = Zn[k];
			}
		}
		else if ((shape == 11) || (shape == 64) || (shape == 65)) {
			if (fabs(g[0] - g[1]) < d0) {
				int i = nearest(g[0], 0, Nx, Xn);
				g[0] = g[1] = Xn[i];
			}
		}
		else if ((shape == 12) || (shape == 61) || (shape == 66)) {
			if (fabs(g[2] - g[3]) < d0) {
				int j = nearest(g[2], 0, Ny, Yn);
				g[2] = g[3] = Yn[j];
			}
		}
		else if ((shape == 13) || (shape == 62) || (shape == 63)) {
			if (fabs(g[4] - g[5]) < d0) {
				int k = nearest(g[4], 0, Nz, Zn);
				g[4] = g[5] = Zn[k];
			}
		}
	}
}


// geometry lines
static void setup_geomlines(void)
{
	// alloc work array
	int *shape     =         (int *)malloc(NGeom * sizeof(int));
	int *id        =         (int *)malloc(NGeom * sizeof(int));
	double (*g)[8] = (double (*)[8])malloc(NGeom * 8 * sizeof(double));

	// set work array
	for (int n = 0; n < NGeom; n++) {
		shape[n] = Geom[n].shape;
		id[n] = Geom[n].type;
		memcpy(g[n], Geom[n].g, 8 * sizeof(double));
	}

	// get array size
	NGline = geomlines(0, NGeom, shape, NULL, NULL, NULL, NULL, 0);

	// alloc data
	Gline  = (double (*)[2][3])malloc(NGline * 2 * 3 * sizeof(double));
	MGline =            (int *)malloc(NGline * sizeof(int));
	memset(Gline, 0, NGline * 2 * 3 * sizeof(double));
	memset(MGline, 0, NGline * sizeof(int));

	// set data
	const double eps = EPS * (fabs(Xn[Nx] - Xn[0]) + fabs(Yn[Ny] - Yn[0]) + fabs(Zn[Nz] - Zn[0]));
	geomlines(1, NGeom, shape, id, g, Gline, MGline, eps);

	// free work array
	free(shape);
	free(id);
	free(g);
}
