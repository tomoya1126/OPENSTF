PROGRAM = ../ost_cuda_mpi.exe

TRASH   = ..\ost_cuda_mpi.exp ..\ost_cuda_mpi.lib

#MPIOPT  = -D_MPI -I../../../../progra~2/micros~1/MPI/Include
MPIOPT  = -D_MPI -I"C:\Program Files (x86)\Microsoft SDKs\MPI\Include"
#MPIOPT  = -D_MPI -Xcompiler "/I\"$(MSMPI_INC)""

OBJS    =        \
Main.obj         \
solve.obj        \
comm_cuda_X.obj  \
comm_cuda_Y.obj  \
comm_cuda_Z.obj  \
info_gpu_mpi.obj \
rank2device.obj  \
../mpi/comm.obj          \
../mpi/comm_X.obj        \
../mpi/comm_Y.obj        \
../mpi/comm_Z.obj        \
../mpi/setup_mpi.obj     \
../cuda/allocfree_gpu.obj \
../cuda/check_gpu.obj     \
../cuda/cuda_memory.obj   \
../cuda/setup_gpu.obj     \
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
../sol/plot3dGeom.obj    \
../sol/ev3d.obj

CC      = nvcc.exe
#CFLAGS  = -O3 -I../include -Xcompiler "/wd4819 /W4"
CFLAGS  = -O3 -I../include -Xcompiler "/W4"
#CFLAGS  = $(CFLAGS) -D_DOUBLE
#CFLAGS  = $(CFLAGS) -D_ID32
LDFLAGS = -O3
LIBS    = msmpi.lib

$(PROGRAM): $(OBJS)
	@echo "Loading $(PROGRAM) ... "
	@$(CC) $(LDFLAGS) -o $(PROGRAM) $(OBJS) $(LIBS)
	del $(TRASH)

.SUFFIXES: .cu

comm_cuda_X.obj:
	$(CC) -c $(CFLAGS) $(MPIOPT) $?
comm_cuda_Y.obj:
	$(CC) -c $(CFLAGS) $(MPIOPT) $?
comm_cuda_Z.obj:
	$(CC) -c $(CFLAGS) $(MPIOPT) $?

.cu.obj:
	$(CC) -c $(CFLAGS) $<

clean:
	del *.obj
