# -*- coding: utf-8 -*-
"""
comm.py (MPI)
"""

import numpy as np
from mpi4py import MPI
from numba import jit, prange
import sol.setup

# 入力データを全プロセスで共有する
def broadcast(comm_rank,
    Nx, Ny, Nz, Xn, Yn, Zn, fVolt, fEpsr, iGeometry, fGeometry, Parm):

    i_buf = None
    f_buf = None
    i_num = np.zeros(1, 'i4')
    f_num = np.zeros(1, 'i4')

    # 変数をバッファに格納する (root)
    if comm_rank == 0:
        # 配列の大きさ
        nvolt = len(fVolt)
        nepsr = len(fEpsr)
        ngeometry = iGeometry.shape[0]

        # データ数
        i_num[0] = 8 + (2 * ngeometry)
        f_num[0] = 2 + (Nx + 1) + (Ny + 1) + (Nz + 1) + nvolt + nepsr + (8 * ngeometry)

        # alloc
        i_buf = np.zeros(i_num[0], 'i4')
        f_buf = np.zeros(f_num[0], 'f8')

        i_id = 0
        f_id = 0

        i_buf[i_id] = Nx; i_id += 1
        i_buf[i_id] = Ny; i_id += 1
        i_buf[i_id] = Nz; i_id += 1

        i_buf[i_id] = nvolt; i_id += 1
        i_buf[i_id] = nepsr; i_id += 1
        i_buf[i_id] = ngeometry; i_id += 1

        f_buf[f_id] = Parm['solver'][0]; f_id += 1
        i_buf[i_id] = Parm['solver'][1]; i_id += 1
        i_buf[i_id] = Parm['solver'][2]; i_id += 1
        f_buf[f_id] = Parm['solver'][3]; f_id += 1

        for i in range(Nx + 1):
            f_buf[f_id] = Xn[i]; f_id += 1

        for j in range(Ny + 1):
            f_buf[f_id] = Yn[j]; f_id += 1

        for k in range(Nz + 1):
            f_buf[f_id] = Zn[k]; f_id += 1

        for n in range(nvolt):
            f_buf[f_id] = fVolt[n]; f_id += 1

        for n in range(nepsr):
            f_buf[f_id] = fEpsr[n]; f_id += 1

        for n in range(ngeometry):
            for m in range(2):
                i_buf[i_id] = iGeometry[n, m]; i_id += 1
            for m in range(8):
                f_buf[f_id] = fGeometry[n, m]; f_id += 1

        # check
        assert(i_id == i_num[0])
        assert(f_id == f_num[0])

    # broadcast (データ数、rootから非rootへ)
    MPI.COMM_WORLD.Bcast(i_num)
    MPI.COMM_WORLD.Bcast(f_num)
    #print(i_num, f_num)

    # alloc (非root)
    if comm_rank > 0:
        i_buf = np.zeros(i_num[0], 'i4')
        f_buf = np.zeros(f_num[0], 'f8')

    # broadcast (データ、rootから非rootへ)
    MPI.COMM_WORLD.Bcast(i_buf)
    MPI.COMM_WORLD.Bcast(f_buf)

    # 受信処理: 非root
    if comm_rank > 0:
        i_id = 0
        f_id = 0

        Nx        = i_buf[i_id]; i_id += 1
        Ny        = i_buf[i_id]; i_id += 1
        Nz        = i_buf[i_id]; i_id += 1
        nvolt     = i_buf[i_id]; i_id += 1
        nepsr     = i_buf[i_id]; i_id += 1
        ngeometry = i_buf[i_id]; i_id += 1
        #print(comm_rank, nvolt, nepsr, ngeometry)

        Parm['solver'] = [0] * 4
        Parm['solver'][0] = f_buf[f_id]; f_id += 1
        Parm['solver'][1] = i_buf[i_id]; i_id += 1
        Parm['solver'][2] = i_buf[i_id]; i_id += 1
        Parm['solver'][3] = f_buf[f_id]; f_id += 1

        Xn = np.zeros(Nx + 1, 'f8')
        for i in range(Nx + 1):
            Xn[i] = f_buf[f_id]; f_id += 1

        Yn = np.zeros(Ny + 1, 'f8')
        for j in range(Ny + 1):
            Yn[j] = f_buf[f_id]; f_id += 1

        Zn = np.zeros(Nz + 1, 'f8')
        for k in range(Nz + 1):
            Zn[k] = f_buf[f_id]; f_id += 1

        fVolt = np.zeros(nvolt, 'f8')
        for n in range(nvolt):
            fVolt[n] = f_buf[f_id]; f_id += 1

        fEpsr = np.zeros(nepsr, 'f8')
        for n in range(nepsr):
            fEpsr[n] = f_buf[f_id]; f_id += 1

        iGeometry = np.zeros((ngeometry, 2), 'i4')
        fGeometry = np.zeros((ngeometry, 8), 'f8')
        for n in range(ngeometry):
            for m in range(2):
                iGeometry[n, m] = i_buf[i_id]; i_id += 1
            for m in range(8):
                fGeometry[n, m] = f_buf[f_id]; f_id += 1

        # check
        assert(i_id == i_num[0])
        assert(f_id == f_num[0])

    # free
    i_buf = None
    f_buf = None

    #print(comm_rank, Nx, Ny, Nz)
    #print(comm_rank, Xn)
    #print(comm_rank, fVolt, fEpsr)
    #print(comm_rank, iGeometry, fGeometry)
    #print(comm_rank, Parm)

    return Nx, Ny, Nz, Xn, Yn, Zn, fVolt, fEpsr, iGeometry, fGeometry

# 全領域のデータをrootに集める
#@jit(cache=True, nopython=True, nogil=True, parallel=True)
def gather(Parm,
    V, idVolt, idEpsr,
    Nx, Ny, Nz, iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0, NN):

    comm_size = Parm['comm_size']
    comm_rank = Parm['comm_rank']
    #print(comm_size, comm_rank)

    # rootの前処理
    if comm_rank == 0:
        # 拡大前のindexを保存する
        imin = iMin
        imax = iMax
        jmin = jMin
        jmax = jMax
        kmin = kMin
        kmax = kMax
        ni = Ni
        nj = Nj
        nk = Nk
        n0 = N0
        #nn = NN

        # 全領域のindexを求める
        iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0, NN, Ipx, Ipy, Ipz \
        = sol.setup.getIndex(Nx, Ny, Nz, 1, 1, 1, 1, 1, 1, 0)
        #print(iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0, NN)

        # 全領域の配列を作成する
        #V      = np.resize(V,      NN)
        #idVolt = np.resize(idVolt, NN)
        #idEpsr = np.resize(idEpsr, NN)
        #print(f_dtype, i_dtype)
        g_V      = np.zeros(NN, Parm['f_dtype'])
        g_idVolt = np.zeros(NN, Parm['i_dtype'])
        g_idEpsr = np.zeros(NN, Parm['i_dtype'])

        # MPI用小領域のデータを全体配列にコピーする
        _copy3d3(g_V, g_idVolt, g_idEpsr, V, idVolt, idEpsr,
            imin, imax, jmin, jmax, kmin, kmax,
            Ni, Nj, Nk, N0,
            ni, nj, nk, n0)
        """
        for i in range(imin, imax + 1):
            for j in range(jmin, jmax + 1):
                for k in range(kmin, kmax + 1):
                    g_n = (Ni * i) + (Nj * j) + (Nk * k) + N0
                    n   = (ni * i) + (nj * j) + (nk * k) + n0
                    g_V[g_n]      = V[n]
                    g_idVolt[g_n] = idVolt[n]
                    g_idEpsr[g_n] = idEpsr[n]
        """

    # 送受信
    if comm_rank == 0:
        # root : 受信
        for rank in range(1, comm_size):
            # indexを受信する
            isize = np.zeros(11, 'i4')
            MPI.COMM_WORLD.Recv(isize, source=rank)
            [imin, imax, jmin, jmax, kmin, kmax, ni, nj, nk, n0, nn] = isize

            # 受信用配列を作成する
            recv_v      = np.zeros(nn, Parm['f_dtype'])
            recv_idvolt = np.zeros(nn, Parm['i_dtype'])
            recv_idepsr = np.zeros(nn, Parm['i_dtype'])

            # データを受信する
            MPI.COMM_WORLD.Recv(recv_v,      source=rank)
            MPI.COMM_WORLD.Recv(recv_idvolt, source=rank)
            MPI.COMM_WORLD.Recv(recv_idepsr, source=rank)
            #start = (Ni * isize[0]) + (Nj * (-1)) + (Nk * (-1)) + N0
            #count = (isize[1] - isize[0] + 1) * (Ny + 3) * (Nz + 3)
            #MPI.COMM_WORLD.Recv(     V[start: start + count], source=rank)
            #MPI.COMM_WORLD.Recv(idVolt[start: start + count], source=rank)
            #MPI.COMM_WORLD.Recv(idEpsr[start: start + count], source=rank)

            # 受信データを全体配列に代入する
            _copy3d3(g_V, g_idVolt, g_idEpsr, recv_v, recv_idvolt, recv_idepsr,
                imin, imax, jmin, jmax, kmin, kmax,
                Ni, Nj, Nk, N0,
                ni, nj, nk, n0)
            """
            for i in range(imin, imax + 1):
                for j in range(jmin, jmax + 1):
                    for k in range(kmin, kmax + 1):
                        g_n = (Ni * i) + (Nj * j) + (Nk * k) + N0
                        n   = (ni * i) + (nj * j) + (nk * k) + n0
                        g_V[g_n]      = recv_v[n]
                        g_idVolt[g_n] = recv_idvolt[n]
                        g_idEpsr[g_n] = recv_idepsr[n]
            """
    else:
        # 非root : 送信
        isize = np.array([iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0, NN], 'i4')
        MPI.COMM_WORLD.Send(isize, 0)
        MPI.COMM_WORLD.Send(     V, 0)
        MPI.COMM_WORLD.Send(idVolt, 0)
        MPI.COMM_WORLD.Send(idEpsr, 0)
        #start = (Ni * iMin) + (Nj * (-1)) + (Nk * (-1)) + N0
        #count = (iMax - iMin + 1) * (Ny + 3) * (Nz + 3)
        #MPI.COMM_WORLD.Send(     V[start: start + count], 0)
        #MPI.COMM_WORLD.Send(idVolt[start: start + count], 0)
        #MPI.COMM_WORLD.Send(idEpsr[start: start + count], 0)

    # 全体配列をrootの配列にコピーする
    if comm_rank == 0:
        V      = g_V.copy()
        idVolt = g_idVolt.copy()
        idEpsr = g_idEpsr.copy()

    return V, idVolt, idEpsr, \
        iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0, NN

# (private) 3個の3D配列のコピー
@jit(cache=True, nopython=True, nogil=True, parallel=True)
def _copy3d3(a1, a2, a3, b1, b2, b3,
    imin, imax, jmin, jmax, kmin, kmax,
    ni_a, nj_a, nk_a, n0_a,
    ni_b, nj_b, nk_b, n0_b):
    for i in prange(imin, imax + 1):
        for j in range(jmin, jmax + 1):
            for k in range(kmin, kmax + 1):
                n_a = (ni_a * i) + (nj_a * j) + (nk_a * k) + n0_a
                n_b = (ni_b * i) + (nj_b * j) + (nk_b * k) + n0_b
                a1[n_a] = b1[n_b]
                a2[n_a] = b2[n_b]
                a3[n_a] = b3[n_b]

# 和(スカラー)
def sum_scalar(var):
    sendbuf = np.array([var], 'f8')
    recvbuf = np.zeros(1, 'f8')
    MPI.COMM_WORLD.Allreduce(sendbuf, recvbuf)

    return recvbuf[0]

# 和(ベクトル, rootのみに返す)
def sum_vector(var):
    #sendbuf = np.array(var, 'f8')
    #recvbuf = np.zeros(len(var), 'f8')
    #MPI.COMM_WORLD.Allreduce(sendbuf, recvbuf)
    #return recvbuf
    result = np.zeros(len(var), 'f8')
    MPI.COMM_WORLD.Reduce(var, result)
    return result
