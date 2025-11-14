# -*- coding: utf-8 -*-
# solve.py

from numba import jit

# 電極に電圧を代入する
@jit(cache=True, nopython=True)
def electrode(V, idVolt, fVolt,
    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0):

    for i in range(iMin - 1, iMax + 2):
        for j in range(jMin - 1, jMax + 2):
            for k in range(kMin - 1, kMax + 2):
                n = (Ni * i) + (Nj * j) + (Nk * k) + N0
                # 電極のみ
                if idVolt[n] > 0:
                    V[n] = fVolt[idVolt[n]]

# 電圧の最小・最大を求める
@jit(cache=True, nopython=True)
def getscale(iGeometry, fVolt):

    #print(iGeometry)
    # 電圧の最小・最大を求める
    vmin = +1e10
    vmax = -1e10
    for n in range(iGeometry.shape[0]):
        if iGeometry[n, 0] < 0:
            v = fVolt[-iGeometry[n, 0]]
            vmin = min(vmin, v)
            vmax = max(vmax, v)
    #print(vmin, vmax)

    return vmin, vmax

# 電圧スケーリング
@jit(cache=True, nopython=True)
def scaling(V, idVolt, vmin, vmax,
    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0):

    # スケール因子
    v0 = (vmin + vmax) / 2
    f = 2 / (vmax - vmin)

    # スケーリング
    for i in range(iMin - 1, iMax + 2):
        for j in range(jMin - 1, jMax + 2):
            for k in range(kMin - 1, kMax + 2):
                n = (Ni * i) + (Nj * j) + (Nk * k) + N0
                if idVolt[n] > 0:
                    V[n] = f * (V[n] - v0)
                else:
                    V[n] = 0

# 電圧スケーリングを戻す
@jit(cache=True, nopython=True)
def rescaling(V, vmin, vmax,
    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0):

    # スケール因子
    v0 = (vmin + vmax) / 2
    f = (vmax - vmin) / 2

    # スケーリング
    for i in range(iMin - 1, iMax + 2):
        for j in range(jMin - 1, jMax + 2):
            for k in range(kMin - 1, kMax + 2):
                n = (Ni * i) + (Nj * j) + (Nk * k) + N0
                V[n] = v0 + (f * V[n])

# 稜線上の電圧を補間する
@jit(cache=True, nopython=True)
def edge(V, idVolt,
    Nx, Ny, Nz, iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0):

    for i in range(iMin, iMax + 1):
        for j in range(jMin, jMax + 1):
            for k in range(kMin, kMax + 1):
                n = (Ni * i) + (Nj * j) + (Nk * k) + N0
                # 誘電体のみ
                if idVolt[n] == 0:
                    # X方向稜線
                    if   (j ==  0) and (k ==  0):
                        V[n] = V[(Ni * (i + 0)) + (Nj * (j + 1)) + (Nk *(k + 1)) + N0]
                    elif (j == Ny) and (k ==  0):
                        V[n] = V[(Ni * (i + 0)) + (Nj * (j - 1)) + (Nk *(k + 1)) + N0]
                    elif (j ==  0) and (k == Nz):
                        V[n] = V[(Ni * (i + 0)) + (Nj * (j + 1)) + (Nk *(k - 1)) + N0]
                    elif (j == Ny) and (k == Nz):
                        V[n] = V[(Ni * (i + 0)) + (Nj * (j - 1)) + (Nk *(k - 1)) + N0]
                    # Y方向稜線
                    elif (k ==  0) and (i ==  0):
                        V[n] = V[(Ni * (i + 1)) + (Nj * (j + 0)) + (Nk *(k + 1)) + N0]
                    elif (k == Nz) and (i ==  0):
                        V[n] = V[(Ni * (i + 1)) + (Nj * (j + 0)) + (Nk *(k - 1)) + N0]
                    elif (k ==  0) and (i == Nx):
                        V[n] = V[(Ni * (i - 1)) + (Nj * (j + 0)) + (Nk *(k + 1)) + N0]
                    elif (k == Nz) and (i == Nx):
                        V[n] = V[(Ni * (i - 1)) + (Nj * (j + 0)) + (Nk *(k - 1)) + N0]
                    # Z方向稜線
                    elif (i ==  0) and (j ==  0):
                        V[n] = V[(Ni * (i + 1)) + (Nj * (j + 1)) + (Nk *(k + 0)) + N0]
                    elif (i == Nx) and (j ==  0):
                        V[n] = V[(Ni * (i - 1)) + (Nj * (j + 1)) + (Nk *(k + 0)) + N0]
                    elif (i ==  0) and (j == Ny):
                        V[n] = V[(Ni * (i + 1)) + (Nj * (j - 1)) + (Nk *(k + 0)) + N0]
                    elif (i == Nx) and (j == Ny):
                        V[n] = V[(Ni * (i - 1)) + (Nj * (j - 1)) + (Nk *(k + 0)) + N0]
