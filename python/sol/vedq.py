# -*- coding: utf-8 -*-
# vedq.py
# 指定した節点(i,j,k)での V/E/D/Q を計算する

import math
import numpy as np
from numba import jit

@jit(cache=True, nopython=True)
def calc(i, j, k, Nx, Ny, Nz, Ni, Nj, Nk, N0,
    Xn, Yn, Zn, RXp, RXm, RYp, RYm, RZp, RZm,
    idVolt, idEpsr, fEpsr, V, EPS0):

    # alloc
    f = np.zeros(10, float)  # V/E/Ex/Ey/Ez/D/Dx/Dy/Dz/Q

    # error check
    if (i < 0) or (i > Nx) or (j < 0) or (j > Ny) or (k < 0) or (k > Nz):
        return f

    ip =  (i + 1) if (i < Nx) else i
    im =  (i - 1) if (i > 0 ) else i
    jp =  (j + 1) if (j < Ny) else j
    jm =  (j - 1) if (j > 0 ) else j
    kp =  (k + 1) if (k < Nz) else k
    km =  (k - 1) if (k > 0 ) else k

    n   = (Ni * i ) + (Nj * j ) + (Nk * k ) + N0
    nxp = (Ni * ip) + (Nj * j ) + (Nk * k ) + N0
    nxm = (Ni * im) + (Nj * j ) + (Nk * k ) + N0
    nyp = (Ni * i ) + (Nj * jp) + (Nk * k ) + N0
    nym = (Ni * i ) + (Nj * jm) + (Nk * k ) + N0
    nzp = (Ni * i ) + (Nj * j ) + (Nk * kp) + N0
    nzm = (Ni * i ) + (Nj * j ) + (Nk * km) + N0

    # V [V]
    f[0] = V[n]

    # E [V/m]
    f[2] = -(V[nxp] - V[nxm]) / (Xn[ip] - Xn[im]) if (Nx > 2) else 0
    f[3] = -(V[nyp] - V[nym]) / (Yn[jp] - Yn[jm]) if (Ny > 2) else 0
    f[4] = -(V[nzp] - V[nzm]) / (Zn[kp] - Zn[km]) if (Nz > 2) else 0
    f[1] = math.sqrt(f[2]**2 + f[3]**2 + f[4]**2)

    # D [C/m^2]
    f[5:9] = EPS0 * fEpsr[idEpsr[n]] * f[1:5]

    # Q [C/m^3]
    if idVolt[n] > 0:  # 電極のみ
        v = V[n]
        e = fEpsr[idEpsr[n]]
        f[9] = EPS0 * (
            (v - V[nxp]) * (e + fEpsr[idEpsr[nxp]]) / 2 * RXp[i] +
            (v - V[nxm]) * (e + fEpsr[idEpsr[nxm]]) / 2 * RXm[i] +
            (v - V[nyp]) * (e + fEpsr[idEpsr[nyp]]) / 2 * RYp[j] +
            (v - V[nym]) * (e + fEpsr[idEpsr[nym]]) / 2 * RYm[j] +
            (v - V[nzp]) * (e + fEpsr[idEpsr[nzp]]) / 2 * RZp[k] +
            (v - V[nzm]) * (e + fEpsr[idEpsr[nzm]]) / 2 * RZm[k])

    return f
