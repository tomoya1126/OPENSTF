# -*- coding: utf-8 -*-
"""
OpenSTF (Python)
Version 4.2.0
ost.py : solver
"""

import sys, time
import numpy as np
import numba
from mpi4py import MPI
import sol.input_data, sol.setup, sol.chars
import sol.geometry, sol.plot3d_geom, sol.monitor, sol.save_bin, sol.cputime
import sol.solve
import sol.comm
import sol_cuda.solve

def main(argv):
    # ロゴ
    version = 'OpenSTF (Python) Version 4.2.0'

    # 計算モード
    GPU = 0     # 0=CPU/1=GPU
    VECTOR = 0  # VECTOR 0=OFF/1=ON

    # 入力データファイル名(ost.pyからの相対パス)
    ost_in = 'python.ost'
    #ost_in = '../data/sample/1st_sample.ost'
    #ost_in = '../data/benchmark/benchmark100.ost'

    # Numbaスレッド数
    thread = 4

    # MPI領域分割数
    Npx = 1
    Npy = 1
    Npz = 1

    # 型宣言
    f_dtype = 'f4'  # 'f4' or 'f8'  (単精度/倍精度)
    i_dtype = 'u1'  # 'u1' or 'i4'  (属性数256以下/以上)

    # 終了時のプロンプト
    prompt = 0

    # 引数処理(引数があるときは引数優先)
    if len(argv) > 1:
        GPU, VECTOR, thread, Npx, Npy, Npz, f_dtype, prompt, ost_in \
        = _args(argv, version)
    #print(GPU, VECTOR, thread, Npx, Npy, Npz, prompt, ost_in)

    # MPI
    comm = MPI.COMM_WORLD
    comm_size = comm.Get_size()  # 非MPI時は1
    comm_rank = comm.Get_rank()  # 非MPI時は0
    if comm_size == 1:
        Npx = Npy = Npz = 1  # 非MPI時は領域分割なし
    elif Npx * Npy * Npz != comm_size:
        Npx = comm_size  # 分割数が正しくないときはすべてX方向に分割する
        Npy = 1
        Npz = 1

    # io : ON/OFF
    io = (comm_rank == 0)

    # 出力ファイル名
    fn_log = 'ost.log'
    fn_out = 'ost.npz'

    # Numbaスレッド数設定
    numba.set_num_threads(thread)

    # cpu time
    cpu = [0] * 4
    cpu[0] = sol.cputime.t(comm_size, GPU)

    # logファイルを開く
    fp_log = None
    if io:
        fp_log = open(fn_log, 'wt', encoding='utf-8')

    # 経過表示 (1)
    if io:
        # ロゴ
        logo = '<<< %s >>>\n%s, process=%dx%dx%d=%d, thread=%d, vector=%s %s' % \
            (version, ('GPU' if GPU else 'CPU'), Npx, Npy, Npz, comm_size, \
            thread, ('on' if VECTOR else 'off'), ('(single)' if (f_dtype == 'f4') else '(double)'))
        sol.monitor.monitor1(fp_log, logo)

    # [1] データ入力
    Parm = {}
    Nx = Ny = Nz = 0
    Xn = Yn = Zn = fVolt = fEpsr = iGeometry = fGeometry = None
    if io:
        Parm, Nx, Ny, Nz, Xn, Yn, Zn, fVolt, fEpsr, iGeometry, fGeometry \
        = sol.input_data.read(ost_in, Parm)
    #_error_check(ierr, prompt)
    #print(comm_rank, Parm)

    # パラメーター追加
    Parm['f_dtype'] = f_dtype
    Parm['i_dtype'] = i_dtype
    Parm['comm_size'] = comm_size
    Parm['comm_rank'] = comm_rank
    Parm['Npx'] = Npx
    Parm['Npy'] = Npy
    Parm['Npz'] = Npz
    #print(comm_rank, Parm)

    # 物体形状の線分データを用意する(図形表示用)
    if io:
        gline, mline = sol.geometry.lines(iGeometry, fGeometry)

    # 物体形状を3D図形表示する
    if io and (Parm['plot3dgeom'] == 1):
        sol.plot3d_geom.plot(Parm, Nx, Ny, Nz, Xn, Yn, Zn, iGeometry, gline, mline)

    # 経過表示 (2)
    if io:
        sol.monitor.monitor2(fp_log, GPU, VECTOR, Parm, Nx, Ny, Nz, fVolt, fEpsr, iGeometry)

    # [2] 計算の準備作業

    # (MPI) broadcast
    if comm_size > 1:
        Nx, Ny, Nz, Xn, Yn, Zn, fVolt, fEpsr, iGeometry, fGeometry \
        = sol.comm.broadcast(comm_rank,
            Nx, Ny, Nz, Xn, Yn, Zn, fVolt, fEpsr, iGeometry, fGeometry, Parm)

    # 配列計算用の係数
    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0, NN, Ipx, Ipy, Ipz \
    = sol.setup.getIndex(Nx, Ny, Nz, Npx, Npy, Npz, Npx, Npy, Npz, Parm['comm_rank'])
    #print(comm_rank, iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0, NN)
    Parm['Ipx'] = Ipx
    Parm['Ipy'] = Ipy
    Parm['Ipz'] = Ipz

    # 3D配列作成
    V      = np.zeros(NN, Parm['f_dtype'])  # 電圧(0で初期化)
    idVolt = np.zeros(NN, Parm['i_dtype'])  # = 0(誘電体),1,2,3,...(電極電圧番号)
    idEpsr = np.zeros(NN, Parm['i_dtype'])  # = 0(電極),1,2,3,...(誘電率番号)

    # 各種準備
    DXn, DYn, DZn, RXp, RXm, RYp, RYm, RZp, RZm \
    = sol.setup.setData(
        Parm, Nx, Ny, Nz, Xn, Yn, Zn,
        iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0,
        iGeometry, fGeometry, idVolt, idEpsr)


    # [3] 計算の主要部
    cpu[1] = sol.cputime.t(comm_size, GPU)

    SOLVER = sol.solve.sor if GPU == 0 else sol_cuda.solve.sor

    nRes, fRes, iRes \
    = SOLVER(VECTOR, Parm,
        iGeometry, idVolt, idEpsr, fVolt, fEpsr, V,
        Nx, Ny, Nz,
        Npx, Npy, Npz, Ipx, Ipy, Ipz,
        iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0, NN,
        RXp, RXm, RYp, RYm, RZp, RZm, fp_log)

    cpu[2] = sol.cputime.t(comm_size, GPU)

    # [4] 電極電荷と総静電エネルギー
    Echar = sol.chars.calc(
        Xn, Yn, Zn, DXn, DYn, DZn, RXp, RXm, RYp, RYm, RZp, RZm,
        Nx, Ny, Nz, iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0,
        idVolt, idEpsr, fVolt, fEpsr, V, Parm['EPS0'])
    # MPI時 : rootに集める
    if Parm['comm_size'] > 1:
        Echar = sol.comm.sum_vector(Echar)

    # MPI時 : rootに全領域の電圧等を集める
    if Parm['comm_size'] > 1:
        #print(Parm['comm_size'], Parm['comm_rank'], Parm['f_dtype'], Parm['i_dtype'])
        V, idVolt, idEpsr, \
        iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0, NN \
        = sol.comm.gather(Parm, #Parm['comm_size'], Parm['comm_rank'], #Parm['f_dtype'], Parm['i_dtype'],
            V, idVolt, idEpsr,
            Nx, Ny, Nz, iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0, NN)

    # [5] 出力
    if io:
        # 経過表示 (3)
        sol.monitor.monitor3(fp_log, Echar)

        # 経過表示 (4)
        sol.monitor.monitor4(fp_log, fn_log, fn_out)

        # 計算結果をファイルに保存する
        sol.save_bin.save(fn_out,
            Nx, Ny, Nz, Ni, Nj, Nk, N0,
            Xn, Yn, Zn, RXp, RXm, RYp, RYm, RZp, RZm,
            idVolt, idEpsr, fEpsr, V, nRes, fRes, iRes,
            gline, mline, Parm['title'], Parm['EPS0'])

    cpu[3] = sol.cputime.t(comm_size, GPU)

    if io:
        # 経過表示 (5)
        sol.monitor.monitor5(fp_log, cpu)

        # logファイルを閉じる
        fp_log.close()

    # メモリー解放
    V = None
    idVolt = None
    idEpsr = None

    # prompt
    if io and prompt:
        input()

# (private) 引数処理
def _args(argv, version):

    usage = 'Usage : python ost.py [-cpu|-gpu] [-n <thread>] [-p <x> <y> <z>] [-no-vector|-vector] [-single|-double] <datafile>'
    GPU = 0
    VECTOR = 0
    thread = 1
    Npx = Npy = Npz = 1
    f_dtype = 'f4'
    prompt = 0
    ost_in = ''

    i = 1
    while i < len(argv):
        arg = argv[i].lower()
        if   arg == '-gpu':
            GPU = 1
            i += 1
        elif arg == '-cpu':
            GPU = 0
            i += 1
        elif arg == '-n':
            thread = int(argv[i + 1])
            i += 2
        elif arg == '-p':
            Npx = int(argv[i + 1])
            Npy = int(argv[i + 2])
            Npz = int(argv[i + 3])
            i += 4
        elif arg == '-vector':
            VECTOR = 1
            i += 1
        elif arg == '-no-vector':
            VECTOR = 0
            i += 1
        elif arg == '-single':
            f_dtype = 'f4'
            i += 1
        elif arg == '-double':
            f_dtype = 'f8'
            i += 1
        elif arg == '-prompt':
            prompt = 1
            i += 1
        elif arg == '--help':
            print(usage)
            sys.exit()
        elif arg == '--version':
            print(version)
            sys.exit()
        else:
            ost_in = argv[i]
            i += 1

    return GPU, VECTOR, thread, Npx, Npy, Npz, f_dtype, prompt, ost_in

# entry point
if __name__ == "__main__":
    main(sys.argv)
