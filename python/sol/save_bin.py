# -*- coding: utf-8 -*-
"""
save_bin.py
"""

import numpy as np

def save(fn,
    Nx, Ny, Nz, Ni, Nj, Nk, N0,
    Xn, Yn, Zn, RXp, RXm, RYp, RYm, RZp, RZm,
    idVolt, idEpsr, fEpsr, V, nRes, fRes, iRes,
    gline, mline, Title, EPS0):

    np.savez(fn,
    Nx, Ny, Nz, Ni, Nj, Nk, N0,
    Xn, Yn, Zn, RXp, RXm, RYp, RYm, RZp, RZm,
    idVolt, idEpsr, fEpsr, V, nRes, fRes, iRes,
    gline, mline, Title, EPS0)
