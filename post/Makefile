PROGRAM = ../ost_post.exe

OBJS    =       \
Main.obj        \
post_data.obj   \
readout.obj     \
post.obj        \
makeL1d.obj     \
makeP2d.obj     \
plotIter.obj    \
plotL1d.obj     \
plotP2d.obj     \
ev2d.obj        \
ev2dlib.obj     \
ev3dlib.obj     \
../sol/utils.obj       \
../sol/ev3d.obj

CC      = cl.exe
CFLAGS  = /O2 /nologo /I../include /W4 /wd4996
LDFLAGS = /O2 /nologo
LIBS    =

$(PROGRAM): $(OBJS)
	@echo "Loading $(PROGRAM) ... "
	@$(CC) $(LDFLAGS) /Fe$(PROGRAM) $(OBJS) $(LIBS)

.c.obj:
	$(CC) /c $(CFLAGS) $<

clean:
	del *.obj
