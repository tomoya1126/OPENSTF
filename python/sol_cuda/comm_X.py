# -*- coding: utf-8 -*-
"""
comm_X.py (CUDA + MPI)
"""

import math
from numba import cuda
from mpi4py import MPI

# X境界の電圧を共有する
def share(Parm, d_V,
    SendBuf_x, RecvBuf_x, d_SendBuf_x, d_RecvBuf_x,
    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0):

    Npx = Parm['Npx']
    Npy = Parm['Npy']
    Npz = Parm['Npz']
    Ipx = Parm['Ipx']
    Ipy = Parm['Ipy']
    Ipz = Parm['Ipz']

    bx = [Ipx > 0, Ipx < Npx - 1]
    px = [Ipx - 1, Ipx + 1]
    isend = [iMin + 1, iMax - 1]
    irecv = [iMin - 1, iMax + 1]

    # grid, block
    block = (16, 16)
    grid = (math.ceil((jMax - jMin + 1) / block[0]),
            math.ceil((kMax - kMin + 1) / block[1]))

    for side in range(2):
        if bx[side]:
            # from device memory to host buffer
            i = isend[side]
            _d2h_gpu[grid, block](i, d_V, d_SendBuf_x, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0)
            d_SendBuf_x.copy_to_host(SendBuf_x)

            # MPI
            ipx = px[side]
            dst = (ipx * Npy * Npz) + (Ipy * Npz) + Ipz
            MPI.COMM_WORLD.Sendrecv(SendBuf_x, dst, recvbuf=RecvBuf_x, source=dst)

            # from host buffer to device memory
            i = irecv[side]
            d_RecvBuf_x = cuda.to_device(RecvBuf_x)
            _h2d_gpu[grid, block](i, d_V, d_RecvBuf_x, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0)

# (private) (kernel関数)
@cuda.jit(cache=True)
def _d2h_gpu(i, v, buf, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0):

    j, k = cuda.grid(2)
    j += jMin
    k += kMin
    if (j < jMax + 1) and \
       (k < kMax + 1):
        n = (Ni * i) + (Nj * j) + (Nk * k) + N0
        m = (j - jMin) * (kMax - kMin + 1) + (k - kMin)
        buf[m] = v[n]

# (private) (kernel関数)
@cuda.jit(cache=True)
def _h2d_gpu(i, v, buf, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0):

    j, k = cuda.grid(2)
    j += jMin
    k += kMin
    if (j < jMax + 1) and \
       (k < kMax + 1):
        n = (Ni * i) + (Nj * j) + (Nk * k) + N0
        m = (j - jMin) * (kMax - kMin + 1) + (k - kMin)
        v[n] = buf[m]
