# -*- coding: utf-8 -*-
"""
comm_Z.py
"""

from mpi4py import MPI
from numba import jit, prange

# Z境界の電圧を共有する
def share(Parm, V, SendBuf_z, RecvBuf_z,
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

    for side in range(2):
        if bz[side]:
            # V to buffer
            k = ksend[side]
            _V_to_buffer(k, V, SendBuf_z, iMin, iMax, jMin, jMax, Ni, Nj, Nk, N0)

            # MPI
            ipz = pz[side]
            dst = (Ipx * Npy * Npz) + (Ipy * Npz) + ipz
            MPI.COMM_WORLD.Sendrecv(SendBuf_z, dst, recvbuf=RecvBuf_z, source=dst)

            # from buffer to V
            k = krecv[side]
            _buffer_to_V(k, V, RecvBuf_z, iMin, iMax, jMin, jMax, Ni, Nj, Nk, N0)

# (private) from V to buffer
@jit(cache=True, nopython=True, nogil=True, parallel=True)
def _V_to_buffer(k, V, buf, iMin, iMax, jMin, jMax, Ni, Nj, Nk, N0):

    for i in prange(iMin, iMax + 1):
        for j in range(jMin, jMax + 1):
            n = (Ni * i) + (Nj * j) + (Nk * k) + N0
            m = (i - iMin) * (jMax - jMin + 1) + (j - jMin)
            buf[m] = V[n]

# (private) from buffer to V
@jit(cache=True, nopython=True, nogil=True, parallel=True)
def _buffer_to_V(k, V, buf, iMin, iMax, jMin, jMax, Ni, Nj, Nk, N0):

    for i in prange(iMin, iMax + 1):
        for j in range(jMin, jMax + 1):
            n = (Ni * i) + (Nj * j) + (Nk * k) + N0
            m = (i - iMin) * (jMax - jMin + 1) + (j - jMin)
            V[n] = buf[m]
