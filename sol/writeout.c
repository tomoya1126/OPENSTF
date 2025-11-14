/*
writeout.c
*/

#include "ost.h"

void writeout(FILE *fp)
{
	size_t num = 0;

	num += fwrite(Title,    sizeof(char),              256, fp);
	num += fwrite(&Nx,      sizeof(int),                 1, fp);
	num += fwrite(&Ny,      sizeof(int),                 1, fp);
	num += fwrite(&Nz,      sizeof(int),                 1, fp);
	num += fwrite(&Ni,      sizeof(int),                 1, fp);
	num += fwrite(&Nj,      sizeof(int),                 1, fp);
	num += fwrite(&Nk,      sizeof(int),                 1, fp);
	num += fwrite(&N0,      sizeof(int),                 1, fp);
	num += fwrite(&NumIter, sizeof(int),                 1, fp);
	num += fwrite(&NGline,  sizeof(int),                 1, fp);

	num += fwrite(Xn,       sizeof(double),         Nx + 1, fp);
	num += fwrite(Yn,       sizeof(double),         Ny + 1, fp);
	num += fwrite(Zn,       sizeof(double),         Nz + 1, fp);
	num += fwrite(RXp,      sizeof(real_t),         Nx + 1, fp);
	num += fwrite(RYp,      sizeof(real_t),         Ny + 1, fp);
	num += fwrite(RZp,      sizeof(real_t),         Nz + 1, fp);
	num += fwrite(RXm,      sizeof(real_t),         Nx + 1, fp);
	num += fwrite(RYm,      sizeof(real_t),         Ny + 1, fp);
	num += fwrite(RZm,      sizeof(real_t),         Nz + 1, fp);
	num += fwrite(Epsr,     sizeof(real_t),            256, fp);
	num += fwrite(Residual, sizeof(double),        NumIter, fp);
	num += fwrite(Gline,    sizeof(double), 2 * 3 * NGline, fp);
	num += fwrite(MGline,   sizeof(int),            NGline, fp);

	// over 4GB ?
	num += fwrite(V,        sizeof(real_t), (Nx + 3) * (Ny + 3) * (Nz + 3), fp);
	num += fwrite(idVolt,   sizeof(id_t),   (Nx + 3) * (Ny + 3) * (Nz + 3), fp);
	num += fwrite(idEpsr,   sizeof(id_t),   (Nx + 3) * (Ny + 3) * (Nz + 3), fp);
/*
	for (int i = 0; i <= Nx; i++) {
		num += fwrite(     &V[D(i, -1, -1)], sizeof(real_t), Ni, fp);
		num += fwrite(&idVolt[D(i, -1, -1)], sizeof(id_t),   Ni, fp);
		num += fwrite(&idEpsr[D(i, -1, -1)], sizeof(id_t),   Ni, fp);
	}
*/
	fwrite(&num, sizeof(size_t), 1, fp);
	//printf("%zd\n", num);

	// free
	free(Residual);
	free(Gline);
	free(MGline);
	free(V);
	free(idVolt);
	free(idEpsr);
}
