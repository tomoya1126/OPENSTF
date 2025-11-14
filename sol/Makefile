PROGRAM = ../ost.exe

OMPOPT  = /openmp

OBJS    =       \
Main.obj        \
input_data.obj  \
monitor.obj     \
geomlines.obj   \
setupsize.obj   \
setupfactor.obj \
setupid.obj     \
ingeometry.obj  \
solve.obj       \
update.obj      \
vmisc.obj       \
echar.obj       \
writeout.obj    \
utils.obj       \
cputime.obj     \
plot3dGeom.obj  \
ev3d.obj

CC      = cl.exe
CFLAGS  = /O2 /nologo /I../include /W4 /wd4996

#CFLAGS  = $(CFLAGS) /D_DOUBLE
#CFLAGS  = $(CFLAGS) /D_ID32
LDFLAGS = /O2 /nologo
LIBS    =

$(PROGRAM): $(OBJS)
	@echo "Loading $(PROGRAM) ... "
	@$(CC) $(LDFLAGS) /Fe$(PROGRAM) $(OBJS) $(LIBS)

Main.obj:
	$(CC) /c $(CFLAGS) $(OMPOPT) $?
update.obj:
	$(CC) /c $(CFLAGS) $(OMPOPT) $?
echar.obj:
	$(CC) /c $(CFLAGS) $(OMPOPT) $?

.c.obj:
	$(CC) /c $(CFLAGS) $<

clean:
	del *.obj
