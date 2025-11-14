# -*- coding: utf-8 -*-
# setup.py

import math
import numpy as np
from numba import jit
import sol.geometry

# 配列計算用の係数
# 領域分割しないときは npx=npy=npz=1
#@jit(cache=True, nopython=True)
def getIndex(Nx, Ny, Nz, Npx, Npy, Npz, npx, npy, npz, comm_rank):

    Ipx = Ipy = Ipz = 0

    # MPI : 領域番号(Ipx, Ipy, Ipz)を取得する
    ip = 0
    for i in range(npx):
        for j in range(npy):
            for k in range(npz):
                if comm_rank == ip:
                    Ipx = i
                    Ipy = j
                    Ipz = k
                ip += 1
    #print(comm_rank, Ipx, Ipy, Ipz)

    """
    if comm_size == 1:
        iMin = 0
        iMax = Nx
    else:
        lx = max(Nx // comm_size, 1)
        iMin = (comm_rank + 0) * lx
        iMax = (comm_rank + 1) * lx
        if comm_rank == comm_size - 1:
            iMax = Nx

    jMin = 0
    jMax = Ny
    kMin = 0
    kMax = Nz
    """

    # min, max
    iMin, iMax = _idminmax(Nx, npx, Npx, Ipx)
    jMin, jMax = _idminmax(Ny, npy, Npy, Ipy)
    kMin, kMax = _idminmax(Nz, npz, Npz, Ipz)

    Ni = (jMax - jMin + 3) * (kMax - kMin + 3)
    Nj = (kMax - kMin + 3)
    Nk = 1
    N0 = -((iMin - 1) * Ni + (jMin - 1) * Nj + (kMin - 1) * Nk)
    NN = Ni * (iMax + 1) + Nj * (jMax + 1) + Nk * (kMax + 1) + N0 + 1

    #print(comm_rank, iMin, iMax, jMin, jMax, kMin, kMax)
    #print(comm_rank, Ni, Nj, Nk, N0, NN)
    #print(comm_rank, (Ni * (iMin - 1)) + (Nj * (jMin - 1)) + (Nk * (kMin - 1)) + N0)
    #print(comm_rank, (Ni * (iMax + 1)) + (Nj * (jMax + 1)) + (Nk * (kMax + 1)) + N0 + 1)
    assert((Ni * (iMin - 1)) + (Nj * (jMin - 1)) + (Nk * (kMin - 1)) + N0 == 0)
    assert((Ni * (iMax + 1)) + (Nj * (jMax + 1)) + (Nk * (kMax + 1)) + N0 == NN - 1)

    return iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0, NN, Ipx, Ipy, Ipz

# (private) 領域indexの上下限を求める
#@jit(cache=True, nopython=True)
def _idminmax(n, _np, np, ip):

    idmin = 0
    idmax = n

    if _np > 1:
        # MPI
        nc = max(n // np, 1)
        idmin = (ip + 0) * nc
        idmax = (ip + 1) * nc
        if ip == np - 1:
            idmax = n
    
    return idmin, idmax

# 各種準備
def setData(
    Parm, Nx, Ny, Nz, Xn, Yn, Zn,
    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0,
    iGeometry, fGeometry, idVolt, idEpsr):

    # 節点の電圧番号と比誘電率を計算する
    _idx(Nx, Ny, Nz, Xn, Yn, Zn,
        iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0,
        iGeometry, fGeometry, idVolt, idEpsr)
    #print((idVolt > 0).sum())
    #print((idEpsr > 0).sum())

    # 差分計算用の因子を計算する
    DXn, RXp, RXm = _meshfactor(Parm, Nx, Xn)
    DYn, RYp, RYm = _meshfactor(Parm, Ny, Yn)
    DZn, RZp, RZm = _meshfactor(Parm, Nz, Zn)
    #print(RXp)
    #print(RXm)
    #print(RYp)
    #print(RYm)
    #print(RZp)
    #print(RZm)

    # 定数
    C = 2.99792458e8
    Parm['EPS0'] = 1 / (math.pi * 4e-7 * C**2)

    return DXn, DYn, DZn, RXp, RXm, RYp, RYm, RZp, RZm

# 節点の電圧番号(idVolt=1,2,3,...)と誘電率番号(idEpsr=1,2,3,...)を計算する
# 誘電体の電圧番号: idVolt=0
# 電極の誘電率番号: idEpsr=0
@jit(cache=True, nopython=True)
def _idx(Nx, Ny, Nz, Xn, Yn, Zn,
    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0,
    iGeometry, fGeometry, idVolt, idEpsr):

    #print(iMin, iMax, jMin, jMax, kMin, kMax)

    # 長さの次元を持つ微小量
    eps = 1e-6 * ((max(Xn) - min(Xn)) + (max(Yn) - min(Yn)) + (max(Zn) - min(Zn)))
    #print(eps)

    for igeometry in range(iGeometry.shape[0]):
        gtype = 1 if iGeometry[igeometry, 0] < 0 else 2  # = 1/2
        pid   = abs(iGeometry[igeometry, 0])    # = 1,2,3,...
        shape = iGeometry[igeometry, 1]  # = 1,2,11,...
        pos   = fGeometry[igeometry]    # position (6 or 8)

        if shape == 1:
            # 直方体
            x1 = min(pos[0], pos[1])
            x2 = max(pos[0], pos[1])
            y1 = min(pos[2], pos[3])
            y2 = max(pos[2], pos[3])
            z1 = min(pos[4], pos[5])
            z2 = max(pos[4], pos[5])
            # MPI用に1セル外側の誘電率も必要
            imin = max(iMin - 1, 0)
            imax = min(iMax + 1, Nx)
            jmin = max(jMin - 1, 0)
            jmax = min(jMax + 1, Ny)
            kmin = max(kMin - 1, 0)
            kmax = min(kMax + 1, Nz)
            i1, i2 = _span(Xn, imin, imax, x1, x2, eps)
            j1, j2 = _span(Yn, jmin, jmax, y1, y2, eps)
            k1, k2 = _span(Zn, kmin, kmax, z1, z2, eps)
            #print(gtype, pid, i1, i2, j1, j2, k1, k2)
            for i in range(i1, i2 + 1):
                for j in range(j1, j2 + 1):
                    for k in range(k1, k2 + 1):
                        n = (Ni * i) + (Nj * j) + (Nk * k) + N0
                        #assert(n > 0 and n < NN)
                        if   gtype == 1:
                            idVolt[n] = pid
                            idEpsr[n] = 0
                        elif gtype == 2:
                            idVolt[n] = 0
                            idEpsr[n] = pid
        else:
            # 直方体以外
            for i in range(iMin - 1, iMax + 2):
                for j in range(jMin - 1, jMax + 2):
                    for k in range(kMin - 1, kMax + 2):
                        if sol.geometry.inside(Xn[i], Yn[j], Zn[k], shape, pos, eps):
                            n = (Ni * i) + (Nj * j) + (Nk * k) + N0
                            if   gtype == 1:
                                idVolt[n] = pid
                                idEpsr[n] = 0
                            elif gtype == 2:
                                idVolt[n] = 0
                                idEpsr[n] = pid

# (private) 差分計算用の因子を計算する
def _meshfactor(Parm, nnode, node):

    dc = np.zeros(nnode + 1, Parm['f_dtype'])
    rp = np.zeros(nnode + 1, Parm['f_dtype'])
    rm = np.zeros(nnode + 1, Parm['f_dtype'])

    # dc : 中心差分
    # rp, rm : 1 / +-半シフト差分 / 中心差分
    for n in range(1, nnode):
        dc[n] = (node[n + 1] - node[n - 1]) / 2
        rp[n] = 1 / (node[n + 1] - node[n + 0]) / dc[n]
        rm[n] = 1 / (node[n + 0] - node[n - 1]) / dc[n]

    # 境界点
    dc[ 0] = node[ 1] - node[ 0]
    dc[-1] = node[-1] - node[-2]

    # 境界点(Neumann境界条件のために重要)
    rm[ 0] = 0
    rp[ 0] = rp[ 1]
    rm[-1] = rm[-2]
    rp[-1] = 0

    # 2Dのときはすべて0
    if nnode < 3:
        rp[:] = rm[:] = 0

    return dc, rp, rm

# (private)
# p1 <= p[n1] <= p[n2] <= p2
# p : p[i1...i2]
# output : n1, n2
@jit(cache=True, nopython=True)
def _span(p, i1, i2, p1, p2, eps):
    """
    i1 = max(i1, 0)
    i2 = max(i2, 0)
    i1 = min(i1, len(p) - 1)
    i2 = min(i2, len(p) - 1)
    #print(i1, i2)

    if i1 > i2:
        i1, i2 = i2, i1
    if p1 > p2:
        p1, p2 = p2, p1
    if p[i1] > p[i2]:
        p = p[::-1]
    """
    n1 = i1
    n2 = i2

    if   (p1 < p[i1] - eps) and (p2 < p[i1] - eps):
        # p1, p2 < p[i1] : n1 > n2 とする
        n1 = i1
        n2 = i1 - 1
    elif (p1 > p[i2] + eps) and (p2 > p[i2] + eps):
        # p1, p2 > p[i2] : n1 > n2 とする
        n1 = i2 + 1
        n2 = i2
    else:
        # p[n1] <= p1
        for i in range(i1, i2 + 1):
            #if (p1 > p[i] - eps) and (p1 < p[i + 1] - eps):
            if p[i] > p1 - eps:
                n1 = i
                break
        #if abs(p1 - p[i2]) < eps:
        #    n1 = i2

        # p2 <= p[n2]
        for i in range(i2, i1 - 1, -1):
            #if (p2 < p[i] + eps) and (p2 > p[i - 1] + eps):
            if p[i] < p2 + eps:
                n2 = i
                break
        #if abs(p2 - p[i1]) < eps:
        #    n2 = i1

    return n1, n2

"""
# debug
if __name__ == "__main__":
    p = np.linspace(0, 6, 7)
    print(p)
    n1, n2 = _span(p, 0, 6, 2.1, 4.1, 1e-6)
    print(n1, n2)
"""