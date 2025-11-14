# -*- coding: utf-8 -*-
"""
comm_Y.py (CUDA + MPI)
"""

import math
from numba import cuda
from mpi4py import MPI

# Y境界の電圧を共有する
def share(Parm, d_V,
    SendBuf_y, RecvBuf_y, d_SendBuf_y, d_RecvBuf_y,
    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0):

    Npx = Parm['Npx']
    Npy = Parm['Npy']
    Npz = Parm['Npz']
    Ipx = Parm['Ipx']
    Ipy = Parm['Ipy']
    Ipz = Parm['Ipz']

    by = [Ipy > 0, Ipy < Npy - 1]
    py = [Ipy - 1, Ipy + 1]
    jsend = [jMin + 1, jMax - 1]
    jrecv = [jMin - 1, jMax + 1]

    # grid, block
    block = (16, 16)
    grid = (math.ceil((kMax - kMin + 1) / block[0]),
            math.ceil((iMax - iMin + 1) / block[1]))

    for side in range(2):
        if by[side]:
            # from device memory to host buffer
            j = jsend[side]
            _d2h_gpu[grid, block](j, d_V, d_SendBuf_y, kMin, kMax, iMin, iMax, Ni, Nj, Nk, N0)
            d_SendBuf_y.copy_to_host(SendBuf_y)

            # MPI
            ipy = py[side]
            dst = (Ipx * Npy * Npz) + (ipy * Npz) + Ipz
            MPI.COMM_WORLD.Sendrecv(SendBuf_y, dst, recvbuf=RecvBuf_y, source=dst)

            # from host buffer to device memory
            j = jrecv[side]
            d_RecvBuf_y = cuda.to_device(RecvBuf_y)
            _h2d_gpu[grid, block](j, d_V, d_RecvBuf_y, kMin, kMax, iMin, iMax, Ni, Nj, Nk, N0)

# (private) (kernel関数)
@cuda.jit(cache=True)
def _d2h_gpu(j, v, buf, kMin, kMax, iMin, iMax, Ni, Nj, Nk, N0):

    k, i = cuda.grid(2)
    k += kMin
    i += iMin
    if (k < kMax + 1) and \
       (i < iMax + 1):
        n = (Ni * i) + (Nj * j) + (Nk * k) + N0
        m = (k - kMin) * (iMax - iMin + 1) + (i - iMin)
        buf[m] = v[n]

# (private) (kernel関数)
@cuda.jit(cache=True)
def _h2d_gpu(j, v, buf, kMin, kMax, iMin, iMax, Ni, Nj, Nk, N0):

    k, i = cuda.grid(2)
    k += kMin
    i += iMin
    if (k < kMax + 1) and \
       (i < iMax + 1):
        n = (Ni * i) + (Nj * j) + (Nk * k) + N0
        m = (k - kMin) * (iMax - iMin + 1) + (i - iMin)
        v[n] = buf[m]
