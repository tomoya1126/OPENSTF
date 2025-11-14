# -*- coding: utf-8 -*-
"""
setup_mpi.py
"""

import numpy as np

def alloc_buffer(Parm, Npx, Npy, Npz, iMin, iMax, jMin, jMax, kMin, kMax):

    SendBuf_x = SendBuf_y = SendBuf_z = RecvBuf_x = RecvBuf_y = RecvBuf_z = None
    f_dtype = Parm['f_dtype']

    if Npx > 1:
        nbuf = (jMax - jMin + 1) * (kMax - kMin + 1)
        SendBuf_x = np.zeros(nbuf, f_dtype)
        RecvBuf_x = np.zeros(nbuf, f_dtype)

    if Npy > 1:
        nbuf = (kMax - kMin + 1) * (iMax - iMin + 1)
        SendBuf_y = np.zeros(nbuf, f_dtype)
        RecvBuf_y = np.zeros(nbuf, f_dtype)

    if Npz > 1:
        nbuf = (iMax - iMin + 1) * (jMax - jMin + 1)
        SendBuf_z = np.zeros(nbuf, f_dtype)
        RecvBuf_z = np.zeros(nbuf, f_dtype)

    return SendBuf_x, SendBuf_y, SendBuf_z, RecvBuf_x, RecvBuf_y, RecvBuf_z
