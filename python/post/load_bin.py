# -*- coding: utf-8 -*-
"""
load_bin.py
"""

import numpy as np

def load(fn):
    d = np.load(fn)
    Nx       = d[d.files[0]]
    Ny       = d[d.files[1]]
    Nz       = d[d.files[2]]
    Ni       = d[d.files[3]]
    Nj       = d[d.files[4]]
    Nk       = d[d.files[5]]
    N0       = d[d.files[6]]
    Xn       = d[d.files[7]]
    Yn       = d[d.files[8]]
    Zn       = d[d.files[9]]
    RXp      = d[d.files[10]]
    RXm      = d[d.files[11]]
    RYp      = d[d.files[12]]
    RYm      = d[d.files[13]]
    RZp      = d[d.files[14]]
    RZm      = d[d.files[15]]
    idVolt   = d[d.files[16]]
    idEpsr   = d[d.files[17]]
    fEpsr    = d[d.files[18]]
    V        = d[d.files[19]]
    nRes     = d[d.files[20]]
    fRes     = d[d.files[21]]
    iRes     = d[d.files[22]]
    gline    = d[d.files[23]]
    mline    = d[d.files[24]]
    Title    = d[d.files[25]]
    EPS0     = d[d.files[26]]

    return \
    Nx, Ny, Nz, Ni, Nj, Nk, N0, \
    Xn, Yn, Zn, RXp, RXm, RYp, RYm, RZp, RZm, \
    idVolt, idEpsr, fEpsr, V, nRes, fRes, iRes, \
    gline, mline, Title, EPS0
