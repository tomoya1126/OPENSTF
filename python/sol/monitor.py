# -*- coding: utf-8 -*-
# monitor.py

import sys
import numpy as np
import datetime

def monitor1(fp, msg):
    monitor1_(fp,         msg)
    monitor1_(sys.stdout, msg)

def monitor2(fp, GPU, VECTOR, Parm, Nx, Ny, Nz, fVolt, fEpsr, iGeometry):
    monitor2_(fp,         GPU, VECTOR, Parm, Nx, Ny, Nz, fVolt, fEpsr, iGeometry)
    monitor2_(sys.stdout, GPU, VECTOR, Parm, Nx, Ny, Nz, fVolt, fEpsr, iGeometry)

def monitor3(fp, Echar):
    monitor3_(fp,         Echar)
    monitor3_(sys.stdout, Echar)

def monitor4(fp, fn_log, fn_out):
    monitor4_(fp,         fn_log, fn_out)
    monitor4_(sys.stdout, fn_log, fn_out)

def monitor5(fp, cpu):
    monitor5_(fp,         cpu)
    monitor5_(sys.stdout, cpu)

# (private)
def monitor1_(fp, msg):
    fp.write('%s\n' % msg)
    fp.flush()

# (private)
def monitor2_(fp, GPU, VECTOR, Parm, Nx, Ny, Nz, fVolt, fEpsr, iGeometry):

    nvolt = (iGeometry[:, 0] < 0).sum()
    nepsr = (iGeometry[:, 0] > 0).sum()

    fp.write('%s\n' % datetime.datetime.now().ctime())
    fp.write('Title = %s\n' % Parm['title'])
    fp.write('Cells = %d x %d x %d = %d\n' % (Nx, Ny, Nz, Nx * Ny * Nz))
    fp.write('No. of voltages    = %d\n' % (len(fVolt) - 1))
    fp.write('No. of dielecrics  = %d\n' % (len(fEpsr) - 1))
    fp.write('No. of geometries  = %d + %d = %d\n' % (nvolt, nepsr, iGeometry.shape[0]))
    fp.write('Memory size        = %d [MB]\n' % _memory_size(GPU, VECTOR, Parm, Nx, Ny, Nz))
    fp.write('Output filesize    = %d [MB]\n' % _file_size(Parm, Nx, Ny, Nz))
    fp.write('Omega              = %g\n' % Parm['solver'][0])
    fp.write('Max iterations     = %d\n' % Parm['solver'][1])
    fp.write('Convergence = %.7f\n' % Parm['solver'][3])
    fp.write('=== iteration start ===\n')
    fp.write('      step    residual\n')
    fp.flush()

# (private)
def monitor3_(fp, Echar):
    fp.write('Volt#   Q[C]\n')
    for n in range(1, len(Echar)):
        fp.write('%5d %13.5e\n' % (n + 1, Echar[n]))
    fp.write('Total energy [W] = %.5e\n' % Echar[0])
    fp.flush()

# (private)
def monitor4_(fp, fn_log, fn_out):
    fp.write('=== output files ===\n')
    fp.write('%s, %s\n' % (fn_log, fn_out))
    fp.flush()

# (private)
def monitor5_(fp, cpu):
    fp.write('=== normal end ===\n')
    fp.write('%s\n' % datetime.datetime.now().ctime())
    fp.write('=== cpu time [sec] ===\n')
    fp.write('part-1 : %10.3f\n' % (cpu[1] - cpu[0]))
    fp.write('part-2 : %10.3f\n' % (cpu[2] - cpu[1]))
    fp.write('part-3 : %10.3f\n' % (cpu[3] - cpu[2]))
    fp.write('-------------------\n')
    fp.write('total  : %10.3f\n' % (cpu[3] - cpu[0]))
    fp.flush()

# (private) memory size [MB]
def _memory_size(GPU, VECTOR, Parm, Nx, Ny, Nz):
    nf = 4 if Parm['f_dtype'] == 'f4' else 8
    ni = 1 if Parm['i_dtype'] == 'u1' else 4
    mem = Nx * Ny * Nz * (nf + ni + ni)  # V, idVolt, idEpsr
    if GPU:
        mem += Nx * Ny * Nz * nf   # d_res2
    if VECTOR:
        mem += Nx * Ny * Nz * nf   # fEpsr_v

    return np.ceil(mem / 1024**2)

# (private) file size [MB]
def _file_size(Parm, Nx, Ny, Nz):
    nf = 4 if Parm['f_dtype'] == 'f4' else 8
    ni = 1 if Parm['i_dtype'] == 'u1' else 4
    mem = Nx * Ny * Nz * (nf + ni + ni)  # V, idVolt, idEpsr

    return np.ceil(mem / 1024**2)
