# -*- coding: utf-8 -*-
"""
comm_Z.py (CUDA + MPI)
"""

import math
from numba import cuda
from mpi4py import MPI

# Z境界の電圧を共有する
def share(Parm, d_V,
    SendBuf_z, RecvBuf_z, d_SendBuf_z, d_RecvBuf_z,
    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0):

    Npx = Parm['Npx']
    Npy = Parm['Npy']
    Npz = Parm['Npz']
    Ipx = Parm['Ipx']
    Ipy = Parm['Ipy']
    Ipz = Parm['Ipz']

    bz = [Ipz > 0, Ipz < Npz - 1]
    pz = [Ipz - 1, Ipz + 1]
    ksend = [kMin + 1, kMax - 1]
    krecv = [kMin - 1, kMax + 1]

    # grid, block
    block = (16, 16)
    grid = (math.ceil((iMax - iMin + 1) / block[0]),
            math.ceil((jMax - jMin + 1) / block[1]))

    for side in range(2):
        if bz[side]:
            # from device memory to host buffer
            k = ksend[side]
            _d2h_gpu[grid, block](k, d_V, d_SendBuf_z, iMin, iMax, jMin, jMax, Ni, Nj, Nk, N0)
            d_SendBuf_z.copy_to_host(SendBuf_z)

            # MPI
            ipz = pz[side]
            dst = (Ipx * Npy * Npz) + (Ipy * Npz) + ipz
            MPI.COMM_WORLD.Sendrecv(SendBuf_z, dst, recvbuf=RecvBuf_z, source=dst)

            # from host buffer to device memory
            k = krecv[side]
            d_RecvBuf_z = cuda.to_device(RecvBuf_z)
            _h2d_gpu[grid, block](k, d_V, d_RecvBuf_z, iMin, iMax, jMin, jMax, Ni, Nj, Nk, N0)

# (private) (kernel関数)
@cuda.jit(cache=True)
def _d2h_gpu(k, v, buf, iMin, iMax, jMin, jMax, Ni, Nj, Nk, N0):

    i, j = cuda.grid(2)
    i += iMin
    j += jMin
    if (i < iMax + 1) and \
       (j < jMax + 1):
        n = (Ni * i) + (Nj * j) + (Nk * k) + N0
        m = (i - iMin) * (jMax - jMin + 1) + (j - jMin)
        buf[m] = v[n]

# (private) (kernel関数)
@cuda.jit(cache=True)
def _h2d_gpu(k, v, buf, iMin, iMax, jMin, jMax, Ni, Nj, Nk, N0):

    i, j = cuda.grid(2)
    i += iMin
    j += jMin
    if (i < iMax + 1) and \
       (j < jMax + 1):
        n = (Ni * i) + (Nj * j) + (Nk * k) + N0
        m = (i - iMin) * (jMax - jMin + 1) + (j - jMin)
        v[n] = buf[m]
