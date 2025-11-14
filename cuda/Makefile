PROGRAM = ../ost_cuda.exe

TRASH   = ..\ost_cuda.exp ..\ost_cuda.lib

OBJS    =         \
Main.obj          \
solve.obj         \
setup_gpu.obj     \
allocfree_gpu.obj \
info_gpu.obj      \
check_gpu.obj     \
cuda_memory.obj   \
../sol/input_data.obj    \
../sol/monitor.obj       \
../sol/geomlines.obj     \
../sol/setupsize.obj     \
../sol/setupfactor.obj   \
../sol/setupid.obj       \
../sol/ingeometry.obj    \
../sol/vmisc.obj         \
../sol/echar.obj         \
../sol/writeout.obj      \
../sol/utils.obj         \
../sol/cputime.obj       \
../sol/plot3dGeom.obj    \
../sol/ev3d.obj

CC      = nvcc.exe
CFLAGS  = -O3 -I../include -Xcompiler "/W4"
#CFLAGS  = $(CFLAGS) -D_DOUBLE
#CFLAGS  = $(CFLAGS) -D_ID32
LDFLAGS = -O3
LIBS    =

$(PROGRAM): $(OBJS)
	@echo "Loading $(PROGRAM) ... "
	@$(CC) $(LDFLAGS) -o $(PROGRAM) $(OBJS) $(LIBS)
	del $(TRASH)

.SUFFIXES: .cu

#echar.obj: ../sol/echar.c
#	$(CC) -c -Xcompiler "/openmp" $(CFLAGS) $?

.cu.obj:
	$(CC) -c $(CFLAGS) $<

clean:
	del *.obj
