/*
monitor.c
*/

#include "ost.h"

// CPU memory size [MB]
static int cpu_memory_size(int vector)
{
	const int64_t n = ((int64_t)(Nx + 3)) * (Ny + 3) * (Nz + 3);
	size_t size
		= 1 * n * sizeof(real_t)          // V
		+ 2 * n * sizeof(id_t)            // idVolt, idEpsr
		+ NGeom * sizeof(geometry_t);     // Geom
	if (vector) {
		size += 1 * NN * sizeof(real_t);  // Epsr_v
	}

	return (int)(size / 1024 / 1024) + 1;
}


// GPU memory size [MB]
static int gpu_memory_size(int vector)
{
	size_t size
		= 1 * NN * sizeof(real_t)         // V
		+ 2 * NN * sizeof(id_t);          // idVolt, idEpsr
	if (vector) {
		size += 1 * NN * sizeof(real_t);  // Epsr_v
	}

	return (int)(size / 1024 / 1024) + 1;
}


// output filesize [MB]
static int output_size(void)
{
	const int64_t n = ((int64_t)(Nx + 1)) * (Ny + 1) * (Nz + 1);
	size_t size
		= 1 * n * sizeof(real_t)   // V
		+ 2 * n * sizeof(id_t);    // idVolt, idEpsr

	return (int)(size / 1024 / 1024) + 1;
}


// title or message
static void monitor1_(FILE *fp, const char msg[])
{
	fprintf(fp, "%s\n", msg);
	fflush(fp);
}


// condition
static void monitor2_(FILE *fp, int vector, int gpu)
{
	time_t now;
	time(&now);

	int nv = 0, ne = 0;
	for (int n = 0; n < NGeom; n++) {
		if (Geom[n].type == 1) nv++;
		if (Geom[n].type == 2) ne++;
	}

	fprintf(fp, "%s", ctime(&now));
	fprintf(fp, "Title = %s\n", Title);
	fprintf(fp, "Cells = %d x %d x %d = %zd\n", Nx, Ny, Nz, (int64_t)Nx * Ny * Nz);
	fprintf(fp, "No. of voltages     = %d\n", NVolt - 1);
	fprintf(fp, "No. of dielecrics   = %d\n", NEpsr - 1);
	fprintf(fp, "No. of geometries   = %d + %d = %d\n", nv, ne, NGeom);
	fprintf(fp, "CPU memory size     = %d [MB]\n", cpu_memory_size(vector));
	if (gpu) fprintf(fp, "GPU memory size     = %d [MB]\n", gpu_memory_size(vector));
	fprintf(fp, "Output file size    = %d [MB]\n", output_size());
	fprintf(fp, "Omega               = %g\n", Solver.omega);
	fprintf(fp, "Max iterations      = %d\n", Solver.maxiter);
	fprintf(fp, "Convergence = %.7f\n", Solver.converg);
	fprintf(fp, "=== iteration start ===\n");
	fprintf(fp, "      step    residual\n");
	fflush(fp);
}


// charge and energy
static void monitor3_(FILE *fp)
{
	fprintf(fp, "%s\n", "Volt#   Q[C]");
	for (int n = 1; n < NVolt; n++) {
		fprintf(fp, "%5d %13.5e\n", n, Echar[n]);
	}
	fprintf(fp, "Total energy [W] = %.5e\n", Echar[0]);
	fflush(fp);
}


// output files
static void monitor4_(FILE *fp)
{
	fprintf(fp, "=== output files ===\n");
	fprintf(fp, "%s, %s\n", FN_log, FN_out);
	fflush(fp);
}


// cpu time
static void monitor5_(FILE *fp, const double cpu[])
{
	time_t now;
	time(&now);

	fprintf(fp, "%s\n", "=== normal end ===");
	fprintf(fp, "%s", ctime(&now));
	fprintf(fp, "%s\n", "=== cpu time [sec] ===");
	fprintf(fp, "part-1 : %10.3f\n", cpu[1] - cpu[0]);
	fprintf(fp, "part-2 : %10.3f\n", cpu[2] - cpu[1]);
	fprintf(fp, "part-3 : %10.3f\n", cpu[3] - cpu[2]);
	fprintf(fp, "%s\n", "---------------------");
	fprintf(fp, "total  : %10.3f\n", cpu[3] - cpu[0]);
	fflush(fp);
}


void monitor1(FILE *fp, const char msg[])
{
	monitor1_(fp,     msg);
	monitor1_(stdout, msg);
}


void monitor2(FILE *fp, int vector, int commsize)
{
	monitor2_(fp,     vector, commsize);
	monitor2_(stdout, vector, commsize);
}


void monitor3(FILE *fp)
{
	monitor3_(fp);
	monitor3_(stdout);
}


void monitor4(FILE *fp)
{
	monitor4_(fp);
	monitor4_(stdout);
}


void monitor5(FILE *fp, const double cpu[])
{
	monitor5_(fp,     cpu);
	monitor5_(stdout, cpu);
}
