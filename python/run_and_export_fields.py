# -*- coding: utf-8 -*-
"""
run_and_export_fields.py
入力ファイルを計算して、全点の座標、電位、電場をnpzファイルで出力するプログラム

使い方:
    python run_and_export_fields.py input.ost
    → input.npz が生成される（電位・電場を含む）
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
import sol.vedq
import sol_cuda.solve


def run_simulation_and_export(input_file, output_file=None):
    """
    シミュレーションを実行して、全座標と電位・電場をnpzファイルに出力

    Parameters:
    -----------
    input_file : str
        入力ファイル名（.ostファイル）
    output_file : str, optional
        出力ファイル名（デフォルト: 入力ファイル名.npz）
    """

    # 出力ファイル名を決定
    if output_file is None:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = base_name + '.npz'

    print(f'Input file: {input_file}')
    print(f'Output file: {output_file}')
    print('')

    # 計算モード
    GPU = 0
    VECTOR = 0
    thread = 4

    # MPI領域分割数
    Npx = 1
    Npy = 1
    Npz = 1

    # 型宣言
    f_dtype = 'f4'
    i_dtype = 'u1'

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
    cpu = [0] * 5
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
    V      = np.zeros(NN, Parm['f_dtype'])
    idVolt = np.zeros(NN, Parm['i_dtype'])
    idEpsr = np.zeros(NN, Parm['i_dtype'])

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
        RXp, RXm, RYp, RYm, RZp, RZm, None)

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

    # [5] 電場計算
    if io:
        print('\n=== Calculating electric fields ===')
        _calculate_and_save_fields(
            output_file, Parm['title'],
            Nx, Ny, Nz, Ni, Nj, Nk, N0,
            Xn, Yn, Zn, RXp, RXm, RYp, RYm, RZp, RZm,
            idVolt, idEpsr, fEpsr, V,
            fVolt, Echar, nRes, fRes, iRes, Parm['EPS0'])

    cpu[4] = sol.cputime.t(comm_size, GPU)

    # [6] 経過表示
    if io:
        print('\nVolt#   Q[C]')
        for n in range(1, len(Echar)):
            print('%5d %13.5e' % (n + 1, Echar[n]))
        print('Total energy [W] = %.5e' % Echar[0])

        print('\n=== output file ===')
        print(output_file)

        print('\n=== cpu time [sec] ===')
        print('part-1 (setup)  : %10.3f' % (cpu[1] - cpu[0]))
        print('part-2 (solve)  : %10.3f' % (cpu[2] - cpu[1]))
        print('part-3 (chars)  : %10.3f' % (cpu[3] - cpu[2]))
        print('part-4 (fields) : %10.3f' % (cpu[4] - cpu[3]))
        print('-------------------')
        print('total           : %10.3f' % (cpu[4] - cpu[0]))
        print('\n=== normal end ===')

    return True


def _calculate_and_save_fields(fn, title, Nx, Ny, Nz, Ni, Nj, Nk, N0,
                                Xn, Yn, Zn, RXp, RXm, RYp, RYm, RZp, RZm,
                                idVolt, idEpsr, fEpsr, V,
                                fVolt, Echar, nRes, fRes, iRes, EPS0):
    """
    電場を計算してnpzファイルに保存

    Parameters:
    -----------
    fn : str
        出力ファイル名
    """

    # 配列を確保（3次元）
    V_3d  = np.zeros((Nz+1, Ny+1, Nx+1), dtype=np.float32)
    E_3d  = np.zeros((Nz+1, Ny+1, Nx+1), dtype=np.float32)  # 電場の大きさ
    Ex_3d = np.zeros((Nz+1, Ny+1, Nx+1), dtype=np.float32)  # X成分
    Ey_3d = np.zeros((Nz+1, Ny+1, Nx+1), dtype=np.float32)  # Y成分
    Ez_3d = np.zeros((Nz+1, Ny+1, Nx+1), dtype=np.float32)  # Z成分

    # 全点について電位と電場を計算
    total_points = (Nx+1) * (Ny+1) * (Nz+1)
    progress_interval = max(total_points // 20, 1)

    count = 0
    for k in range(Nz + 1):
        for j in range(Ny + 1):
            for i in range(Nx + 1):
                # vedq.calcで V/E/Ex/Ey/Ez などを計算
                vedq = sol.vedq.calc(
                    i, j, k, Nx, Ny, Nz, Ni, Nj, Nk, N0,
                    Xn, Yn, Zn, RXp, RXm, RYp, RYm, RZp, RZm,
                    idVolt, idEpsr, fEpsr, V, EPS0)

                # 配列に格納
                V_3d[k, j, i]  = vedq[0]  # V
                E_3d[k, j, i]  = vedq[1]  # E (magnitude)
                Ex_3d[k, j, i] = vedq[2]  # Ex
                Ey_3d[k, j, i] = vedq[3]  # Ey
                Ez_3d[k, j, i] = vedq[4]  # Ez

                count += 1
                if count % progress_interval == 0:
                    progress = 100 * count / total_points
                    print(f'Progress: {progress:.1f}% ({count}/{total_points})', end='\r')

    print(f'\nCompleted: {count} points')

    # npzファイルに保存
    print(f'Saving to {fn}...')
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
        # 電位配列
        potential=V_3d,
        # 電場配列
        electric_field=E_3d,     # 電場の大きさ [V/m]
        electric_field_x=Ex_3d,  # X方向電場 [V/m]
        electric_field_y=Ey_3d,  # Y方向電場 [V/m]
        electric_field_z=Ez_3d,  # Z方向電場 [V/m]
        # その他の情報
        voltages=fVolt,
        dielectrics=fEpsr,
        charges=Echar,
        # 収束情報
        iteration_steps=nRes,
        residuals=fRes,
        iteration_indices=iRes
    )

    file_size = os.path.getsize(fn) / 1024**2
    print(f'Data saved successfully')
    print(f'  Grid: {Nx} x {Ny} x {Nz}')
    print(f'  Points: {Nx+1} x {Ny+1} x {Nz+1} = {(Nx+1)*(Ny+1)*(Nz+1)}')
    print(f'  File size: {file_size:.2f} MB')
    print(f'  Electric field range: [{E_3d.min():.6e}, {E_3d.max():.6e}] V/m')


def main(argv):
    """
    メイン関数

    使い方:
        python run_and_export_fields.py input.ost [output.npz]
    """

    if len(argv) < 2:
        print('Usage: python run_and_export_fields.py <input.ost> [output.npz]')
        print('')
        print('Examples:')
        print('  python run_and_export_fields.py simple_example.ost')
        print('  python run_and_export_fields.py sample.ost sample_result.npz')
        print('  python run_and_export_fields.py yoko.ost')
        print('')
        print('Output includes:')
        print('  - Coordinates (x, y, z)')
        print('  - Electric potential (V)')
        print('  - Electric field magnitude (E)')
        print('  - Electric field components (Ex, Ey, Ez)')
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
