# -*- coding: utf-8 -*-
"""
read_npz_example.py
run_and_export.pyで生成したnpzファイルを読み込むサンプルプログラム
"""

import sys
import numpy as np


def read_and_display_npz(npz_file):
    """
    npzファイルを読み込んで内容を表示

    Parameters:
    -----------
    npz_file : str
        npzファイル名
    """

    print(f'Reading: {npz_file}')
    print('')

    # npzファイルを読み込む
    data = np.load(npz_file)

    # ファイルに含まれるキーを表示
    print('=== Available keys ===')
    for key in data.files:
        print(f'  {key}')
    print('')

    # メタデータを読み込む
    title = str(data['title'])
    nx = int(data['nx'])
    ny = int(data['ny'])
    nz = int(data['nz'])
    eps0 = float(data['eps0'])

    print('=== Metadata ===')
    print(f'Title: {title}')
    print(f'Grid size: {nx} x {ny} x {nz}')
    print(f'Points: {nx+1} x {ny+1} x {nz+1} = {(nx+1)*(ny+1)*(nz+1)}')
    print(f'EPS0: {eps0}')
    print('')

    # 座標配列を読み込む
    x = data['x']  # X座標配列（1次元、長さ nx+1）
    y = data['y']  # Y座標配列（1次元、長さ ny+1）
    z = data['z']  # Z座標配列（1次元、長さ nz+1）

    print('=== Coordinate arrays ===')
    print(f'X: shape={x.shape}, min={x.min():.3e}, max={x.max():.3e}')
    print(f'Y: shape={y.shape}, min={y.min():.3e}, max={y.max():.3e}')
    print(f'Z: shape={z.shape}, min={z.min():.3e}, max={z.max():.3e}')
    print('')

    # 電位配列を読み込む
    potential = data['potential']  # 3次元配列 (nz+1, ny+1, nx+1)

    print('=== Potential array ===')
    print(f'Shape: {potential.shape}')
    print(f'Min: {potential.min():.6e} V')
    print(f'Max: {potential.max():.6e} V')
    print(f'Mean: {potential.mean():.6e} V')
    print('')

    # その他の情報
    voltages = data['voltages']
    dielectrics = data['dielectrics']
    charges = data['charges']

    print('=== Other information ===')
    print(f'Voltages: {voltages}')
    print(f'Dielectrics: {dielectrics}')
    print(f'Total energy: {charges[0]:.6e} W')
    print('')

    # 収束情報
    iteration_steps = data['iteration_steps']
    residuals = data['residuals']

    print('=== Convergence information ===')
    print(f'Total iterations: {len(iteration_steps)}')
    if len(residuals) > 0:
        print(f'Final residual: {residuals[-1]:.6e}')
    print('')

    # 使用例: 特定の点の電位を取得
    print('=== Example: Get potential at specific points ===')

    # 中心点の電位
    i_center = nx // 2
    j_center = ny // 2
    k_center = nz // 2
    v_center = potential[k_center, j_center, i_center]
    print(f'Center point ({i_center}, {j_center}, {k_center}):')
    print(f'  Position: ({x[i_center]:.3e}, {y[j_center]:.3e}, {z[k_center]:.3e})')
    print(f'  Potential: {v_center:.6e} V')
    print('')

    # Z=0平面の電位分布（最も近い点）
    k_z0 = np.argmin(np.abs(z))
    print(f'Z≈0 plane (k={k_z0}, Z={z[k_z0]:.3e}):')
    print(f'  Potential distribution shape: {potential[k_z0, :, :].shape}')
    print(f'  Min: {potential[k_z0, :, :].min():.6e} V')
    print(f'  Max: {potential[k_z0, :, :].max():.6e} V')
    print('')

    return data


def export_to_text(npz_file, txt_file):
    """
    npzファイルをテキストファイルに変換

    Parameters:
    -----------
    npz_file : str
        入力npzファイル名
    txt_file : str
        出力テキストファイル名
    """

    print(f'Converting {npz_file} to {txt_file}...')

    # データ読み込み
    data = np.load(npz_file)

    nx = int(data['nx'])
    ny = int(data['ny'])
    nz = int(data['nz'])
    x = data['x']
    y = data['y']
    z = data['z']
    potential = data['potential']

    # テキストファイルに出力
    with open(txt_file, 'w', encoding='utf-8') as fp:
        fp.write(f'# Title: {data["title"]}\n')
        fp.write(f'# Grid: {nx} x {ny} x {nz}\n')
        fp.write(f'# Points: {nx+1} x {ny+1} x {nz+1}\n')
        fp.write('#\n')
        fp.write('#    i    j    k            X[m]            Y[m]            Z[m]            V[V]\n')

        count = 0
        for k in range(nz + 1):
            for j in range(ny + 1):
                for i in range(nx + 1):
                    fp.write('%6d%6d%6d%16.7e%16.7e%16.7e%16.7e\n' %
                             (i, j, k, x[i], y[j], z[k], potential[k, j, i]))
                    count += 1

    print(f'Successfully wrote {count} points to {txt_file}')


def main(argv):
    """
    メイン関数

    使い方:
        python read_npz_example.py <file.npz>
        python read_npz_example.py <file.npz> --to-text <output.txt>
    """

    if len(argv) < 2:
        print('Usage: python read_npz_example.py <file.npz> [--to-text output.txt]')
        print('')
        print('Examples:')
        print('  python read_npz_example.py simple_example.npz')
        print('  python read_npz_example.py sample.npz --to-text sample.txt')
        sys.exit(1)

    npz_file = argv[1]

    # テキスト変換オプション
    if len(argv) > 2 and argv[2] == '--to-text':
        if len(argv) < 4:
            print('Error: --to-text requires output file name')
            sys.exit(1)
        txt_file = argv[3]
        export_to_text(npz_file, txt_file)
    else:
        # 読み込んで表示
        read_and_display_npz(npz_file)


if __name__ == "__main__":
    main(sys.argv)
