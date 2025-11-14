# -*- coding: utf-8 -*-
# solve.py (CUDA)

import math
import numpy as np
from numba import cuda
import sol_cuda.update, sol_cuda.comm_X, sol_cuda.comm_Y, sol_cuda.comm_Z
import sol.vmisc, sol.monitor, sol.setup_mpi

# SOR法により電圧分布を計算する(GPU)
def sor(VECTOR, Parm,
    iGeometry, idVolt, idEpsr, fVolt, fEpsr, V,
    Nx, Ny, Nz,
    Npx, Npy, Npz, Ipx, Ipy, Ipz,
    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0, NN,
    RXp, RXm, RYp, RYm, RZp, RZm, fp):

    #print(Nx, Ny, Nz)
    #print(Npx, Npy, Npz, Ipx, Ipy, Ipz)
    #print(iMin, iMax, jMin, jMax, kMin, kMax)
    #print(Ni, Nj, Nk, N0, NN)

    # 反復計算パラメーター
    omega   = Parm['solver'][0]
    maxiter = Parm['solver'][1]
    nout    = Parm['solver'][2]
    converg = Parm['solver'][3]

    # block, grid (tuple)
    block = (32, 4, 1)
    grid = (math.ceil((kMax - kMin + 1) / block[0]),
            math.ceil((jMax - jMin + 1) / block[1]),
            math.ceil((iMax - iMin + 1) / block[2]))
    #print(grid)

    # 残差出力用配列
    fRes = np.zeros(maxiter // nout + 1, float)
    iRes = np.zeros(maxiter // nout + 1, int)

    # MPI用配列
    SendBuf_x, SendBuf_y, SendBuf_z, RecvBuf_x, RecvBuf_y, RecvBuf_z \
    = sol.setup_mpi.alloc_buffer(Parm, Npx, Npy, Npz, iMin, iMax, jMin, jMax, kMin, kMax)

    # vectorモード用配列(host+device)
    if VECTOR:
        fEpsr_v = np.zeros(NN, Parm['f_dtype'])
        fEpsr_v[:] = fEpsr[idEpsr[:]]
        d_fEpsr_v = cuda.to_device(fEpsr_v)

    # 残差計算用device配列
    #d_res2 = cuda.device_array(NN, Parm['f_dtype'])  # MPI時にNG
    res2 = np.zeros(NN, Parm['f_dtype'])
    d_res2 = cuda.to_device(res2)

    # 電極に電圧を代入する
    sol.vmisc.electrode(V, idVolt, fVolt,
        iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0)

    # 電圧の最小・最大を求める
    vmin, vmax = sol.vmisc.getscale(iGeometry, fVolt)
    #print(vmin, vmax)

    # 電圧スケーリング
    sol.vmisc.scaling(V, idVolt, vmin, vmax,
        iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0)

    # host memory -> device memory
    # 電圧Vをコピーすることに注意
    d_RXp, d_RXm, d_RYp, d_RYm, d_RZp, d_RZm, \
    d_idVolt, d_idEpsr, d_fEpsr, d_V, \
    d_SendBuf_x, d_SendBuf_y, d_SendBuf_z, d_RecvBuf_x, d_RecvBuf_y, d_RecvBuf_z \
    = _copy_to_device(
        RXp, RXm, RYp, RYm, RZp, RZm,
        idVolt, idEpsr, fEpsr, V,
        SendBuf_x, SendBuf_y, SendBuf_z, RecvBuf_x, RecvBuf_y, RecvBuf_z)

    # 反復計算の変数を初期化する
    converged = False
    nRes = 0

    # 反復計算
    for iiter in range(maxiter + 1):
        # V更新(red-black法)
        for oe in range(2):
            if VECTOR:
                sol_cuda.update.vector[grid, block](oe,
                    d_V, d_res2, d_idVolt, d_fEpsr_v,
                    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0,
                    d_RXp, d_RXm, d_RYp, d_RYm, d_RZp, d_RZm, omega)
            else:
                sol_cuda.update.no_vector[grid, block](oe,
                    d_V, d_res2, d_idVolt, d_idEpsr, d_fEpsr,
                    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0,
                    d_RXp, d_RXm, d_RYp, d_RYm, d_RZp, d_RZm, omega)

            # 領域境界のVを共有する
            if Npx > 1:
                sol_cuda.comm_X.share(Parm, d_V,
                    SendBuf_x, RecvBuf_x, d_SendBuf_x, d_RecvBuf_x,
                    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0)
            if Npy > 1:
                sol_cuda.comm_Y.share(Parm, d_V,
                    SendBuf_y, RecvBuf_y, d_SendBuf_y, d_RecvBuf_y,
                    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0)
            if Npz > 1:
                sol_cuda.comm_Z.share(Parm, d_V,
                    SendBuf_z, RecvBuf_z, d_SendBuf_z, d_RecvBuf_z,
                    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0)

        # 収束判定
        if (iiter % nout == 0) or (iiter == maxiter):
            # 残差(収束判定のため全プロセス必要)
            #res2_sum = sum_reduce(d_res2)  # warning
            d_res2.copy_to_host(res2); res2_sum = np.sum(res2)
            if Parm['comm_size'] > 1:
                res2_sum = sol.comm.sum_scalar(res2_sum)
            res = math.sqrt(res2_sum / ((Nx + 1) * (Ny + 1) * (Nz + 1)))

            # 平均電磁界を保存する (ポスト処理用)
            fRes[nRes] = res
            iRes[nRes] = iiter
            nRes += 1

            # 経過確認
            if Parm['comm_rank'] == 0:
                msg = '    %6d    %.7f' % (iiter, res)
                sol.monitor.monitor1(fp, msg)

            # 収束判定
            if res < converg:
                converged = True
                break

    # 収束結果をlogに出力する
    if Parm['comm_rank'] == 0:
        msg = "    --- %s ---" % ("converged" if converged else "max steps")
        sol.monitor.monitor1(fp, msg)

    # device memory -> host memory
    _copy_to_host(d_V, V)

    # スケーリングを戻す
    sol.vmisc.rescaling(V, vmin, vmax,
        iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0)

    # 稜線上の電圧を補間する
    sol.vmisc.edge(V, idVolt,
        Nx, Ny, Nz, iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0)

    # nRes : 残差を計算した回数
    # fRes : 残差配列
    # iRes : 残差配列の反復回数
    #print(nRes, fRes[0:nRes], iRes[0:nRes])
    return nRes, fRes, iRes

# reduction sum
@cuda.reduce
def sum_reduce(a, b):
    return a + b

# host memory -> device memory
def _copy_to_device(
    RXp, RXm, RYp, RYm, RZp, RZm,
    idVolt, idEpsr, fEpsr, V,
    SendBuf_x, SendBuf_y, SendBuf_z, RecvBuf_x, RecvBuf_y, RecvBuf_z):

    d_RXp = cuda.to_device(RXp)
    d_RXm = cuda.to_device(RXm)
    d_RYp = cuda.to_device(RYp)
    d_RYm = cuda.to_device(RYm)
    d_RZp = cuda.to_device(RZp)
    d_RZm = cuda.to_device(RZm)

    d_idVolt = cuda.to_device(idVolt)
    d_idEpsr = cuda.to_device(idEpsr)
    d_fEpsr  = cuda.to_device(fEpsr)
    d_V      = cuda.to_device(V)

    d_SendBuf_x = cuda.to_device(SendBuf_x)
    d_SendBuf_y = cuda.to_device(SendBuf_y)
    d_SendBuf_z = cuda.to_device(SendBuf_z)
    d_RecvBuf_x = cuda.to_device(RecvBuf_x)
    d_RecvBuf_y = cuda.to_device(RecvBuf_y)
    d_RecvBuf_z = cuda.to_device(RecvBuf_z)

    return \
    d_RXp, d_RXm, d_RYp, d_RYm, d_RZp, d_RZm, \
    d_idVolt, d_idEpsr, d_fEpsr, d_V, \
    d_SendBuf_x, d_SendBuf_y, d_SendBuf_z, d_RecvBuf_x, d_RecvBuf_y, d_RecvBuf_z

# device memory -> host memory
def _copy_to_host(d_V, V):

    d_V.copy_to_host(V)
