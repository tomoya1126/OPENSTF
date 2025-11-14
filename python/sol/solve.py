# -*- coding: utf-8 -*-
# solve.py

import math
import numpy as np
import sol.update, sol.vmisc, sol.monitor
import sol.setup_mpi, sol.comm_X, sol.comm_Y, sol.comm_Z

# SOR法により電圧分布を計算する(CPU)
def sor(VECTOR, Parm,
    iGeometry, idVolt, idEpsr, fVolt, fEpsr, V,
    Nx, Ny, Nz,
    Npx, Npy, Npz, Ipx, Ipy, Ipz,
    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0, NN,
    RXp, RXm, RYp, RYm, RZp, RZm, fp):

    # 反復計算パラメーター
    omega   = Parm['solver'][0]
    maxiter = Parm['solver'][1]
    nout    = Parm['solver'][2]
    converg = Parm['solver'][3]

    # vectorモード用配列
    if VECTOR:
        fEpsr_v = np.zeros(NN, Parm['f_dtype'])
        fEpsr_v[:] = fEpsr[idEpsr[:]]

    # 残差配列
    fRes = np.zeros(maxiter // nout + 1, float)
    iRes = np.zeros(maxiter // nout + 1, int)

    # MPI用配列
    SendBuf_x, SendBuf_y, SendBuf_z, RecvBuf_x, RecvBuf_y, RecvBuf_z \
    = sol.setup_mpi.alloc_buffer(Parm, Npx, Npy, Npz, iMin, iMax, jMin, jMax, kMin, kMax)

    # 電極に電圧を代入する
    sol.vmisc.electrode(V, idVolt, fVolt,
        iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0)

    # 電圧の最小・最大を求める
    vmin, vmax = sol.vmisc.getscale(iGeometry, fVolt)

    # 電圧スケーリング
    sol.vmisc.scaling(V, idVolt, vmin, vmax,
        iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0)

    # 反復計算の変数を初期化する
    converged = False
    nRes = 0

    # 反復計算
    for iiter in range(maxiter + 1):
        # V更新(red-black法)
        res2_sum = 0
        for oe in range(2):
            if VECTOR:
                res2_sum += sol.update.vector(oe,
                    V, idVolt, fEpsr_v,
                    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0,
                    RXp, RXm, RYp, RYm, RZp, RZm, omega)
            else:
                res2_sum += sol.update.no_vector(oe,
                    V, idVolt, idEpsr, fEpsr,
                    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0,
                    RXp, RXm, RYp, RYm, RZp, RZm, omega)

            # MPI : 境界のVを共有する (2回必要)
            if Npx > 1:
                sol.comm_X.share(Parm, V, SendBuf_x, RecvBuf_x,
                    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0)
            if Npy > 1:
                sol.comm_Y.share(Parm, V, SendBuf_y, RecvBuf_y,
                    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0)
            if Npz > 1:
                sol.comm_Z.share(Parm, V, SendBuf_z, RecvBuf_z,
                    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0)

        # 収束判定
        if (iiter % nout == 0) or (iiter == maxiter):
            # 残差(収束判定のため全プロセス必要)
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

    # 収束結果をlogに出力する(rootのみ)
    if Parm['comm_rank'] == 0:
        msg = "    --- %s ---" % ("converged" if converged else "max steps")
        sol.monitor.monitor1(fp, msg)

    # 電圧スケーリングを戻す
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
