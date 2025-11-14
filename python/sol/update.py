# -*- coding: utf-8 -*-
"""
update_cpu.py
V更新と残差の計算
"""

from numba import jit, prange

# vector
@jit(cache=True, nopython=True, nogil=True, parallel=True)
def no_vector(oe,
    V, idVolt, idEpsr, fEpsr,
    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0,
    RXp, RXm, RYp, RYm, RZp, RZm, omega):

    res2_sum = 0

    for i in prange(iMin, iMax + 1):
        for j in range(jMin, jMax + 1):
            for k in range(kMin, kMax + 1):
                n = (Ni * i) + (Nj * j) + (Nk * k) + N0
                if ((i + j + k) % 2 == oe) and (idVolt[n] == 0):
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
                        res2_sum += res**2

    return res2_sum

# vector
@jit(cache=True, nopython=True, nogil=True, parallel=True)
def vector(oe,
    V, idVolt, fEpsr_v,
    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0,
    RXp, RXm, RYp, RYm, RZp, RZm, omega):

    res2_sum = 0

    for i in prange(iMin, iMax + 1):
        for j in range(jMin, jMax + 1):
            for k in range(kMin, kMax + 1):
                n = (Ni * i) + (Nj * j) + (Nk * k) + N0
                if ((i + j + k) % 2 == oe) and (idVolt[n] == 0):
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
                        res2_sum += res**2

    return res2_sum
