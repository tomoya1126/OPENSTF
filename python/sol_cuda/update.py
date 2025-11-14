# -*- coding: utf-8 -*-
"""
update.py (CUDA)
V更新と残差の計算, red-black法
"""

from numba import cuda

# novectorモード (kernel関数)
@cuda.jit(cache=True)
def no_vector(oe,
    V, res2, idVolt, idEpsr, fEpsr,
    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0,
    RXp, RXm, RYp, RYm, RZp, RZm, omega):

    k, j, i = cuda.grid(3)

    i += iMin
    j += jMin
    k += kMin

    n = (Ni * i) + (Nj * j) + (Nk * k) + N0
    if ((i < iMax + 1) and
        (j < jMax + 1) and
        (k < kMax + 1) and
        ((i + j + k) % 2 == oe) and
        (idVolt[n] == 0)):

        e0 = fEpsr[idEpsr[n]]

        axp = (e0 + fEpsr[idEpsr[n + Ni]]) * RXp[i]
        axm = (e0 + fEpsr[idEpsr[n - Ni]]) * RXm[i]
        ayp = (e0 + fEpsr[idEpsr[n + Nj]]) * RYp[j]
        aym = (e0 + fEpsr[idEpsr[n - Nj]]) * RYm[j]
        azp = (e0 + fEpsr[idEpsr[n + Nk]]) * RZp[k]
        azm = (e0 + fEpsr[idEpsr[n - Nk]]) * RZm[k]
        asum = axp + axm + ayp + aym + azp + azm

        res = ((axp * V[n + Ni]) + (axm * V[n - Ni]) + \
               (ayp * V[n + Nj]) + (aym * V[n - Nj]) + \
               (azp * V[n + Nk]) + (azm * V[n - Nk])) / asum - V[n]
        res *= omega

        V[n] += res
        if ((i == 0) or (i > iMin)) and \
           ((j == 0) or (j > jMin)) and \
           ((k == 0) or (k > kMin)):  # MPI
            res2[n] = res**2

# vectorモード (kernel関数)
@cuda.jit(cache=True)
def vector(oe,
    V, res2, idVolt, fEpsr_v,
    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0,
    RXp, RXm, RYp, RYm, RZp, RZm, omega):

    k, j, i = cuda.grid(3)

    i += iMin
    j += jMin
    k += kMin

    n = (Ni * i) + (Nj * j) + (Nk * k) + N0
    if ((i < iMax + 1) and
        (j < jMax + 1) and
        (k < kMax + 1) and
        ((i + j + k) % 2 == oe) and
        (idVolt[n] == 0)):

        e0 = fEpsr_v[n]

        axp = (e0 + fEpsr_v[n + Ni]) * RXp[i]
        axm = (e0 + fEpsr_v[n - Ni]) * RXm[i]
        ayp = (e0 + fEpsr_v[n + Nj]) * RYp[j]
        aym = (e0 + fEpsr_v[n - Nj]) * RYm[j]
        azp = (e0 + fEpsr_v[n + Nk]) * RZp[k]
        azm = (e0 + fEpsr_v[n - Nk]) * RZm[k]
        asum = axp + axm + ayp + aym + azp + azm

        res = ((axp * V[n + Ni]) + (axm * V[n - Ni]) + \
               (ayp * V[n + Nj]) + (aym * V[n - Nj]) + \
               (azp * V[n + Nk]) + (azm * V[n - Nk])) / asum - V[n]
        res *= omega

        V[n] += res
        if ((i == 0) or (i > iMin)) and \
           ((j == 0) or (j > jMin)) and \
           ((k == 0) or (k > kMin)):  # MPI
            res2[n] = res**2
