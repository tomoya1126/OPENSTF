# -*- coding: utf-8 -*-
# char.py

import numpy as np
from numba import jit, prange

# 電極電荷と全静電エネルギーを計算する
# inlineすると高速化され、かつ並列化される
#@jit(cache=True, nopython=True, nogil=True, parallel=True) # NG
@jit(cache=True, nopython=True)
def calc(
    Xn, Yn, Zn, DXn, DYn, DZn, RXp, RXm, RYp, RYm, RZp, RZm,
    Nx, Ny, Nz, iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0,
    idVolt, idEpsr, fVolt, fEpsr, V, EPS0):

    Echar = np.zeros(len(fVolt), 'f8')

    wsum = 0
    for i in prange(iMin, iMax + 1):
        for j in range(jMin, jMax + 1):
            for k in range(kMin, kMax + 1):
                if ((i == 0) or (i > iMin)) and \
                   ((j == 0) or (j > jMin)) and \
                   ((k == 0) or (k > kMin)):  # MPI
                    # inline (vedq.py)
                    dv = DXn[i] * DYn[j] * DZn[k]

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

                    # E
                    ex = -(V[nxp] - V[nxm]) / (Xn[ip] - Xn[im]) if (Nx > 2) else 0
                    ey = -(V[nyp] - V[nym]) / (Yn[jp] - Yn[jm]) if (Ny > 2) else 0
                    ez = -(V[nzp] - V[nzm]) / (Zn[kp] - Zn[km]) if (Nz > 2) else 0
                    e2 = ex**2 + ey**2 + ez**2

                    # Q
                    if idVolt[n] > 0:  # 電極のみ
                        v = V[n]
                        e = fEpsr[idEpsr[n]]
                        q = EPS0 * (
                            (v - V[nxp]) * (e + fEpsr[idEpsr[nxp]]) / 2 * RXp[i] +
                            (v - V[nxm]) * (e + fEpsr[idEpsr[nxm]]) / 2 * RXm[i] +
                            (v - V[nyp]) * (e + fEpsr[idEpsr[nyp]]) / 2 * RYp[j] +
                            (v - V[nym]) * (e + fEpsr[idEpsr[nym]]) / 2 * RYm[j] +
                            (v - V[nzp]) * (e + fEpsr[idEpsr[nzp]]) / 2 * RZp[k] +
                            (v - V[nzm]) * (e + fEpsr[idEpsr[nzm]]) / 2 * RZm[k])
                        Echar[idVolt[n]] += q * dv

                    # W
                    wsum += e2 * fEpsr[idEpsr[n]] * dv

    # 全静電エネルギー
    Echar[0] = 0.5 * wsum * EPS0

    return Echar
