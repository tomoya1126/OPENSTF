/*
readout.c

read ost.out
*/

#include "ost.h"

void readout(FILE *fp)
{
	size_t num = 0;

	num += fread(Title,    sizeof(char), 256, fp);
	num += fread(&Nx,      sizeof(int),    1, fp);
	num += fread(&Ny,      sizeof(int),    1, fp);
	num += fread(&Nz,      sizeof(int),    1, fp);
	num += fread(&Ni,      sizeof(int),    1, fp);
	num += fread(&Nj,      sizeof(int),    1, fp);
	num += fread(&Nk,      sizeof(int),    1, fp);
	num += fread(&N0,      sizeof(int),    1, fp);
	num += fread(&NumIter, sizeof(int),    1, fp);
	num += fread(&NGline,  sizeof(int),    1, fp);

	Xn       =         (double *)malloc((Nx + 1)                       * sizeof(double));
	Yn       =         (double *)malloc((Ny + 1)                       * sizeof(double));
	Zn       =         (double *)malloc((Nz + 1)                       * sizeof(double));
	RXp      =         (real_t *)malloc((Nx + 1)                       * sizeof(real_t));
	RYp      =         (real_t *)malloc((Ny + 1)                       * sizeof(real_t));
	RZp      =         (real_t *)malloc((Nz + 1)                       * sizeof(real_t));
	RXm      =         (real_t *)malloc((Nx + 1)                       * sizeof(real_t));
	RYm      =         (real_t *)malloc((Ny + 1)                       * sizeof(real_t));
	RZm      =         (real_t *)malloc((Nz + 1)                       * sizeof(real_t));
	Residual =         (double *)malloc(NumIter                        * sizeof(double));
	Gline    = (double (*)[2][3])malloc(NGline * 2 * 3                 * sizeof(double));
	MGline   =            (int *)malloc(NGline                         * sizeof(int));
	V        =         (real_t *)malloc((Nx + 3) * (Ny + 3) * (Nz + 3) * sizeof(real_t));
	idVolt   =           (id_t *)malloc((Nx + 3) * (Ny + 3) * (Nz + 3) * sizeof(id_t));
	idEpsr   =           (id_t *)malloc((Nx + 3) * (Ny + 3) * (Nz + 3) * sizeof(id_t));

	num += fread(Xn,       sizeof(double),         Nx + 1, fp);
	num += fread(Yn,       sizeof(double),         Ny + 1, fp);
	num += fread(Zn,       sizeof(double),         Nz + 1, fp);
	num += fread(RXp,      sizeof(real_t),         Nx + 1, fp);
	num += fread(RYp,      sizeof(real_t),         Ny + 1, fp);
	num += fread(RZp,      sizeof(real_t),         Nz + 1, fp);
	num += fread(RXm,      sizeof(real_t),         Nx + 1, fp);
	num += fread(RYm,      sizeof(real_t),         Ny + 1, fp);
	num += fread(RZm,      sizeof(real_t),         Nz + 1, fp);
	num += fread(Epsr,     sizeof(real_t),            256, fp);
	num += fread(Residual, sizeof(double),        NumIter, fp);
	num += fread(Gline,    sizeof(double), 2 * 3 * NGline, fp);
	num += fread(MGline,   sizeof(int),            NGline, fp);

	// over 4GB ?
	num += fread(V,        sizeof(real_t), (Nx + 3) * (Ny + 3) * (Nz + 3), fp);
	num += fread(idVolt,   sizeof(id_t),   (Nx + 3) * (Ny + 3) * (Nz + 3), fp);
	num += fread(idEpsr,   sizeof(id_t),   (Nx + 3) * (Ny + 3) * (Nz + 3), fp);
/*
	for (int i = 0; i <= Nx; i++) {
		num += fread(     &V[D(i, -1, -1)], sizeof(real_t), Ni, fp);
		num += fread(&idVolt[D(i, -1, -1)], sizeof(id_t),   Ni, fp);
		num += fread(&idEpsr[D(i, -1, -1)], sizeof(id_t),   Ni, fp);
	}
*/
	size_t num0;
	size_t size = fread(&num0, sizeof(size_t), 1, fp);
	size = size;  // suppress gcc warning

	if (num != num0) {
		fprintf(stderr, "*** invalid file length : (%zd, %zd)\n", num0, num);
	}
}
