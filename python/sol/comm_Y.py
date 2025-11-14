# -*- coding: utf-8 -*-
"""
comm_Y.py
"""

from mpi4py import MPI
from numba import jit, prange

# Y境界の電圧を共有する
def share(Parm, V, SendBuf_y, RecvBuf_y,
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

    for side in range(2):
        if by[side]:
            # V to buffer
            j = jsend[side]
            _V_to_buffer(j, V, SendBuf_y, kMin, kMax, iMin, iMax, Ni, Nj, Nk, N0)

            # MPI
            ipy = py[side]
            dst = (Ipx * Npy * Npz) + (ipy * Npz) + Ipz
            MPI.COMM_WORLD.Sendrecv(SendBuf_y, dst, recvbuf=RecvBuf_y, source=dst)

            # from buffer to V
            j = jrecv[side]
            _buffer_to_V(j, V, RecvBuf_y, kMin, kMax, iMin, iMax, Ni, Nj, Nk, N0)

# (private) from V to buffer
@jit(cache=True, nopython=True, nogil=True, parallel=True)
def _V_to_buffer(j, V, buf, kMin, kMax, iMin, iMax, Ni, Nj, Nk, N0):

    for k in prange(kMin, kMax + 1):
        for i in range(iMin, iMax + 1):
            n = (Ni * i) + (Nj * j) + (Nk * k) + N0
            m = (k - kMin) * (iMax - iMin + 1) + (i - iMin)
            buf[m] = V[n]

# (private) from buffer to V
@jit(cache=True, nopython=True, nogil=True, parallel=True)
def _buffer_to_V(j, V, buf, kMin, kMax, iMin, iMax, Ni, Nj, Nk, N0):

    for k in prange(kMin, kMax + 1):
        for i in range(iMin, iMax + 1):
            n = (Ni * i) + (Nj * j) + (Nk * k) + N0
            m = (k - kMin) * (iMax - iMin + 1) + (i - iMin)
            V[n] = buf[m]
