PROGRAM = ../ost_mpi.exe

MPIOPT  = /D_MPI
OMPOPT  = /openmp

OBJS    =       \
Main.obj        \
solve.obj       \
setup_mpi.obj   \
comm.obj        \
comm_X.obj      \
comm_Y.obj      \
comm_Z.obj      \
../sol/input_data.obj  \
../sol/monitor.obj     \
../sol/geomlines.obj   \
../sol/setupsize.obj   \
../sol/setupfactor.obj \
../sol/setupid.obj     \
../sol/ingeometry.obj  \
../sol/update.obj      \
../sol/vmisc.obj       \
../sol/echar.obj       \
../sol/writeout.obj    \
../sol/utils.obj       \
../sol/plot3dGeom.obj  \
../sol/ev3d.obj

CC      = cl.exe
CFLAGS  = /O2 /nologo /I../include /W4 /wd4996
#CFLAGS  = $(CFLAGS) /D_DOUBLE
#CFLAGS  = $(CFLAGS) /D_ID32
LDFLAGS = /O2 /nologo
LIBS    = msmpi.lib

$(PROGRAM): $(OBJS)
	@echo "Loading $(PROGRAM) ... "
	@$(CC) $(LDFLAGS) /Fe$(PROGRAM) $(OBJS) $(LIBS)

Main.obj:
	$(CC) /c $(CFLAGS) $(OMPOPT) $?
solve.obj:
	$(CC) /c $(CFLAGS) $(OMPOPT) $?
comm.obj:
	$(CC) /c $(CFLAGS) $(MPIOPT) $?
comm_X.obj:
	$(CC) /c $(CFLAGS) $(MPIOPT) $?
comm_Y.obj:
	$(CC) /c $(CFLAGS) $(MPIOPT) $?
comm_Z.obj:
	$(CC) /c $(CFLAGS) $(MPIOPT) $?

.c.obj:
	$(CC) /c $(CFLAGS) $<

clean:
	del *.obj
