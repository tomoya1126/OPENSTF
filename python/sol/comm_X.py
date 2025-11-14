# -*- coding: utf-8 -*-
"""
comm_X.py
"""

from mpi4py import MPI
from numba import jit, prange

# X境界の電圧を共有する
def share(Parm, V, SendBuf_x, RecvBuf_x,
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

    for side in range(2):
        if bx[side]:
            # V to buffer
            i = isend[side]
            _V_to_buffer(i, V, SendBuf_x, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0)

            # MPI
            ipx = px[side]
            dst = (ipx * Npy * Npz) + (Ipy * Npz) + Ipz
            MPI.COMM_WORLD.Sendrecv(SendBuf_x, dst, recvbuf=RecvBuf_x, source=dst)

            # from buffer to V
            i = irecv[side]
            _buffer_to_V(i, V, RecvBuf_x, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0)

# (private) from V to buffer
@jit(cache=True, nopython=True, nogil=True, parallel=True)
def _V_to_buffer(i, V, buf, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0):

    for j in prange(jMin, jMax + 1):
        for k in range(kMin, kMax + 1):
            n = (Ni * i) + (Nj * j) + (Nk * k) + N0
            m = (j - jMin) * (kMax - kMin + 1) + (k - kMin)
            buf[m] = V[n]

# (private) from buffer to V
@jit(cache=True, nopython=True, nogil=True, parallel=True)
def _buffer_to_V(i, V, buf, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0):

    for j in prange(jMin, jMax + 1):
        for k in range(kMin, kMax + 1):
            n = (Ni * i) + (Nj * j) + (Nk * k) + N0
            m = (j - jMin) * (kMax - kMin + 1) + (k - kMin)
            V[n] = buf[m]
