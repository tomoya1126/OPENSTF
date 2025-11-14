// ost.h
#ifndef _OST_H_
#define _OST_H_

#ifdef __cplusplus
extern "C" {
#endif

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <time.h>
#include <ctype.h>
#include <limits.h>
#include <assert.h>

#ifdef _OPENMP
#include <omp.h>
#endif

#define PROGRAM "OpenSTF"
#define VERSION_MAJOR (4)
#define VERSION_MINOR (2)
#define VERSION_BUILD (2)

#ifdef MAIN
#define EXTERN
#else
#define EXTERN extern
#endif

#define FN_out      "ost.out"
#define FN_log      "ost.log"
#define FN_geom3d_0 "geom3d.htm"
#define FN_ev2d_0   "ev2d.htm"
#define FN_ev3d_0   "ev3d.htm"
#define FN_geom3d_1 "geom.ev3"
#define FN_ev2d_1   "ev.ev2"
#define FN_ev3d_1   "ev.ev3"
#define FN_1d       "1d.log"
#define FN_2d       "2d.log"

#define PI     (4.0*atan(1.0))
#define DTOR   (PI/180)
#define C      (2.99792458e8)
#define ETA0   (C*4*PI*1e-7)
#define EPS0   (1/(C*ETA0))
#define EPS    (1e-6)
#define EPS2   (EPS*EPS)
#define PEC    (1)

#define MAX(x,y) ((x) > (y) ? (x) : (y))
#define MIN(x,y) ((x) < (y) ? (x) : (y))

//#define D(i,j,k) ((i + 1) * (Ny + 3) * (Nz + 3) + (j + 1) * (Nz + 3) + (k + 1))
#define D(i,j,k) ((i) * Ni + (j) * Nj + (k) * Nk + N0)

#if defined(_DOUBLE)
#define real_t double
#define MPI_REAL_T MPI_DOUBLE
#else
#define real_t float
#define MPI_REAL_T MPI_FLOAT
#endif

#if defined(_ID64)
#define id_t   int64_t
#define MPI_ID_T MPI_UNSIGNED_LONG
#elif defined(_ID32)
#define id_t   int
#define MPI_ID_T MPI_UNSIGNED
#elif defined(_ID16)
#define id_t   unsigned short
#define MPI_ID_T MPI_UNSIGNED_SHORT
#else
#define id_t   unsigned char
#define MPI_ID_T MPI_UNSIGNED_CHAR
#endif

// === struct ===

typedef struct {
int    type;                    // type: 1=electrode, 2:dielectric
id_t   pid;                     // property: =1,2,...
int    shape;                   // shape: 1=rectangle, 2=sphere, ...
double g[8];                    // coordinate [m]
} geometry_t;                   // geometry

typedef struct {
double     omega;               // over-relaxation factor
int        maxiter;
int        nout;
double     converg;
} solver_t;

typedef struct {
int        db;                  // db ? (0/1)
int        user;                // 0/1 : auto/user
double     min, max;            // min, max
int        div;                 // division
} scale_t;                      // scale

typedef struct {
char       component;
char       direction;
double     position[2];
int        posid[2];
} l1d_t;

typedef struct {
char       component[3];
char       direction;
double     position;
int        posid;
} p2d_t;

// === solver ===

EXTERN char       Title[256];          // title

EXTERN int        Nx, Ny, Nz;          // number of cells
EXTERN int        iMin, iMax, jMin, jMax, kMin, kMax;
EXTERN int        Ni, Nj, Nk, N0;
EXTERN int64_t    NN;

EXTERN double     *Xn, *Yn, *Zn;       // node
EXTERN real_t     *RXp, *RYp, *RZp;
EXTERN real_t     *RXm, *RYm, *RZm;

EXTERN int        NGeom;               // number of geometries
EXTERN geometry_t *Geom;               // geometry

EXTERN int        NVolt;               // number of voltages
EXTERN double     Volt[256];           // voltage [V] (id_t = unsigned char)

EXTERN int        NEpsr;               // number of permittivities
EXTERN real_t     Epsr[256];           // permittivity (id_t = unsigned char)

EXTERN solver_t   Solver;

EXTERN int        NGline;              // number of geometry lines
EXTERN double     (*Gline)[2][3];      // geometery lines
EXTERN int        *MGline;             // property of geometry lines

EXTERN real_t     *V;
EXTERN id_t       *idVolt, *idEpsr;
EXTERN real_t     *Epsr_v;

EXTERN int        NumIter;
EXTERN double     *Residual;

EXTERN double     *Echar;

EXTERN int        Plot3dGeom;

EXTERN int        commSize, commRank;  // MPI
EXTERN int        Npx, Npy, Npz, Ipx, Ipy, Ipz;  // block
EXTERN real_t     *SendBuf_x, *SendBuf_y, *SendBuf_z;
EXTERN real_t     *RecvBuf_x, *RecvBuf_y, *RecvBuf_z;
EXTERN real_t     *g_V;
EXTERN id_t       *g_idVolt, *g_idEpsr;

// === post ===

EXTERN int        HTML;                // 0:ev, 1:HTML

EXTERN int        Piter;

EXTERN int        NL1d;
EXTERN l1d_t      *L1d;
EXTERN scale_t    L1dScale;
EXTERN int        L1dLog;
EXTERN double     ***F1d;

EXTERN int        NP2d;
EXTERN p2d_t      *P2d;
EXTERN int        P2dFigure[2];
EXTERN scale_t    P2dScale;
EXTERN int        P2dObject[2];
EXTERN int        P2dContour;
EXTERN int        P2dZoomin;
EXTERN double     P2dZoom[2][2];
EXTERN int        P2dLog;
EXTERN double     ****F2d;

EXTERN double     Width2d, Height2d;   // window size (2D)
EXTERN double     Fontsize2d;          // font size (2D)

#ifdef __cplusplus
}
#endif

#endif  // _OST_H_
