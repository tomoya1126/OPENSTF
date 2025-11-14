# -*- coding: utf-8 -*-
"""
run_and_export.py
入力ファイルを計算して、全点の座標と電位をnpzファイルで出力するプログラム

使い方:
    python run_and_export.py input.ost
    → input.npz が生成される
"""

import sys
import os
import time
import numpy as np
import numba
from mpi4py import MPI

# モジュールのインポート
import sol.input_data, sol.setup, sol.chars
import sol.geometry, sol.plot3d_geom, sol.monitor, sol.save_bin, sol.cputime
import sol.solve
import sol.comm
import sol_cuda.solve


def run_simulation_and_export(input_file, output_file=None):
    """
    シミュレーションを実行して、全座標と電位をnpzファイルに出力

    Parameters:
    -----------
    input_file : str
        入力ファイル名（.ostファイル）
    output_file : str, optional
        出力ファイル名（デフォルト: 入力ファイル名.npz）
    """

    # 出力ファイル名を決定
    if output_file is None:
        # 入力ファイル名から拡張子を除いて.npzを付ける
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = base_name + '.npz'

    print(f'Input file: {input_file}')
    print(f'Output file: {output_file}')
    print('')

    # 計算モード
    GPU = 0     # 0=CPU/1=GPU
    VECTOR = 0  # VECTOR 0=OFF/1=ON
    thread = 4  # Numbaスレッド数

    # MPI領域分割数
    Npx = 1
    Npy = 1
    Npz = 1

    # 型宣言
    f_dtype = 'f4'  # 'f4' or 'f8'  (単精度/倍精度)
    i_dtype = 'u1'  # 'u1' or 'i4'  (属性数256以下/以上)

    # MPI
    comm = MPI.COMM_WORLD
    comm_size = comm.Get_size()
    comm_rank = comm.Get_rank()
    if comm_size == 1:
        Npx = Npy = Npz = 1
    elif Npx * Npy * Npz != comm_size:
        Npx = comm_size
        Npy = 1
        Npz = 1

    # io : ON/OFF
    io = (comm_rank == 0)

    # Numbaスレッド数設定
    numba.set_num_threads(thread)

    # cpu time
    cpu = [0] * 4
    cpu[0] = sol.cputime.t(comm_size, GPU)

    # 経過表示 (1)
    if io:
        version = 'OpenSTF (Python) Version 4.2.0'
        logo = '<<< %s >>>\n%s, process=%dx%dx%d=%d, thread=%d' % \
            (version, ('GPU' if GPU else 'CPU'), Npx, Npy, Npz, comm_size, thread)
        print(logo)
        print('')

    # [1] データ入力
    Parm = {}
    Nx = Ny = Nz = 0
    Xn = Yn = Zn = fVolt = fEpsr = iGeometry = fGeometry = None
    if io:
        Parm, Nx, Ny, Nz, Xn, Yn, Zn, fVolt, fEpsr, iGeometry, fGeometry \
        = sol.input_data.read(input_file, Parm)
        if Parm is None:
            print('*** Error reading input file')
            return False

    # パラメーター追加
    Parm['f_dtype'] = f_dtype
    Parm['i_dtype'] = i_dtype
    Parm['comm_size'] = comm_size
    Parm['comm_rank'] = comm_rank
    Parm['Npx'] = Npx
    Parm['Npy'] = Npy
    Parm['Npz'] = Npz

    # 経過表示 (2)
    if io:
        nvolt = (iGeometry[:, 0] < 0).sum()
        nepsr = (iGeometry[:, 0] > 0).sum()
        print('Title = %s' % Parm['title'])
        print('Cells = %d x %d x %d = %d' % (Nx, Ny, Nz, Nx * Ny * Nz))
        print('Points = %d x %d x %d = %d' % (Nx+1, Ny+1, Nz+1, (Nx+1) * (Ny+1) * (Nz+1)))
        print('No. of voltages    = %d' % (len(fVolt) - 1))
        print('No. of dielectrics = %d' % (len(fEpsr) - 1))
        print('No. of geometries  = %d + %d = %d' % (nvolt, nepsr, iGeometry.shape[0]))
        print('Omega              = %g' % Parm['solver'][0])
        print('Max iterations     = %d' % Parm['solver'][1])
        print('Convergence        = %.7f' % Parm['solver'][3])
        print('=== iteration start ===')
        print('      step    residual')

    # [2] 計算の準備作業

    # (MPI) broadcast
    if comm_size > 1:
        Nx, Ny, Nz, Xn, Yn, Zn, fVolt, fEpsr, iGeometry, fGeometry \
        = sol.comm.broadcast(comm_rank,
            Nx, Ny, Nz, Xn, Yn, Zn, fVolt, fEpsr, iGeometry, fGeometry, Parm)

    # 配列計算用の係数
    iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0, NN, Ipx, Ipy, Ipz \
    = sol.setup.getIndex(Nx, Ny, Nz, Npx, Npy, Npz, Npx, Npy, Npz, Parm['comm_rank'])
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
        RXp, RXm, RYp, RYm, RZp, RZm, None)  # fp_log=None

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
        V, idVolt, idEpsr, \
        iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0, NN \
        = sol.comm.gather(Parm,
            V, idVolt, idEpsr,
            Nx, Ny, Nz, iMin, iMax, jMin, jMax, kMin, kMax, Ni, Nj, Nk, N0, NN)

    cpu[3] = sol.cputime.t(comm_size, GPU)

    # [5] 出力
    if io:
        # 経過表示 (3)
        print('\nVolt#   Q[C]')
        for n in range(1, len(Echar)):
            print('%5d %13.5e' % (n + 1, Echar[n]))
        print('Total energy [W] = %.5e' % Echar[0])

        # 経過表示 (4)
        print('\n=== output file ===')
        print(output_file)

        # 計算結果をnpzファイルに保存する
        # 全座標と電位を含む
        print('\nSaving data...')
        _save_coordinates_and_potential(
            output_file, Parm['title'],
            Nx, Ny, Nz, Xn, Yn, Zn, V,
            fVolt, fEpsr, Echar, nRes, fRes, iRes, Parm['EPS0'])

        # 経過表示 (5)
        print('\n=== cpu time [sec] ===')
        print('part-1 : %10.3f' % (cpu[1] - cpu[0]))
        print('part-2 : %10.3f' % (cpu[2] - cpu[1]))
        print('part-3 : %10.3f' % (cpu[3] - cpu[2]))
        print('-------------------')
        print('total  : %10.3f' % (cpu[3] - cpu[0]))
        print('\n=== normal end ===')

    return True


def _save_coordinates_and_potential(fn, title, Nx, Ny, Nz, Xn, Yn, Zn, V,
                                     fVolt, fEpsr, Echar, nRes, fRes, iRes, EPS0):
    """
    全座標と電位をnpzファイルに保存

    Parameters:
    -----------
    fn : str
        出力ファイル名
    title : str
        タイトル
    Nx, Ny, Nz : int
        グリッド数
    Xn, Yn, Zn : ndarray
        座標配列
    V : ndarray
        電位配列（1次元）
    fVolt : ndarray
        電圧リスト
    fEpsr : ndarray
        比誘電率リスト
    Echar : ndarray
        電荷と総エネルギー
    nRes, fRes, iRes : ndarray
        収束情報
    EPS0 : float
        真空の誘電率
    """

    # Vを3次元配列に変換
    V_3d = np.zeros((Nz+1, Ny+1, Nx+1), dtype=V.dtype)
    for k in range(Nz + 1):
        for j in range(Ny + 1):
            for i in range(Nx + 1):
                idx = k * (Nx+1) * (Ny+1) + j * (Nx+1) + i
                V_3d[k, j, i] = V[idx]

    # メタデータ
    metadata = {
        'title': title,
        'nx': Nx,
        'ny': Ny,
        'nz': Nz,
        'eps0': EPS0,
        'total_energy': Echar[0] if len(Echar) > 0 else 0.0,
    }

    # npzファイルに保存
    np.savez(fn,
        # メタデータ
        title=title,
        nx=Nx,
        ny=Ny,
        nz=Nz,
        eps0=EPS0,
        # 座標配列
        x=Xn,
        y=Yn,
        z=Zn,
        # 電位配列（3次元）
        potential=V_3d,
        # その他の情報
        voltages=fVolt,
        dielectrics=fEpsr,
        charges=Echar,
        # 収束情報
        iteration_steps=nRes,
        residuals=fRes,
        iteration_indices=iRes
    )

    print(f'Data saved to {fn}')
    print(f'  Grid: {Nx} x {Ny} x {Nz}')
    print(f'  Points: {Nx+1} x {Ny+1} x {Nz+1} = {(Nx+1)*(Ny+1)*(Nz+1)}')
    print(f'  File size: {os.path.getsize(fn) / 1024**2:.2f} MB')


def main(argv):
    """
    メイン関数

    使い方:
        python run_and_export.py input.ost [output.npz]
    """

    if len(argv) < 2:
        print('Usage: python run_and_export.py <input.ost> [output.npz]')
        print('')
        print('Examples:')
        print('  python run_and_export.py simple_example.ost')
        print('  python run_and_export.py sample.ost sample_result.npz')
        print('  python run_and_export.py ../data/sample/1st_sample.ost')
        sys.exit(1)

    input_file = argv[1]
    output_file = argv[2] if len(argv) > 2 else None

    # 入力ファイルの存在確認
    if not os.path.exists(input_file):
        print(f'*** Error: Input file not found: {input_file}')
        sys.exit(1)

    # シミュレーション実行
    success = run_simulation_and_export(input_file, output_file)

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)
