# -*- coding: utf-8 -*-
"""
read_fields_example.py
run_and_export_fields.pyで生成したnpzファイル（電場含む）を読み込むサンプルプログラム
"""

import sys
import numpy as np


def read_and_display_fields(npz_file):
    """
    電場データを含むnpzファイルを読み込んで内容を表示

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
    x = data['x']
    y = data['y']
    z = data['z']

    print('=== Coordinate arrays ===')
    print(f'X: shape={x.shape}, min={x.min():.3e}, max={x.max():.3e}')
    print(f'Y: shape={y.shape}, min={y.min():.3e}, max={y.max():.3e}')
    print(f'Z: shape={z.shape}, min={z.min():.3e}, max={z.max():.3e}')
    print('')

    # 電位配列を読み込む
    V = data['potential']

    print('=== Potential (V) ===')
    print(f'Shape: {V.shape}')
    print(f'Min: {V.min():.6e} V')
    print(f'Max: {V.max():.6e} V')
    print(f'Mean: {V.mean():.6e} V')
    print('')

    # 電場配列を読み込む
    E = data['electric_field']       # 電場の大きさ
    Ex = data['electric_field_x']    # X成分
    Ey = data['electric_field_y']    # Y成分
    Ez = data['electric_field_z']    # Z成分

    print('=== Electric Field (E) ===')
    print(f'Shape: {E.shape}')
    print(f'Min: {E.min():.6e} V/m')
    print(f'Max: {E.max():.6e} V/m')
    print(f'Mean: {E.mean():.6e} V/m')
    print('')

    print('=== Electric Field Components ===')
    print(f'Ex: min={Ex.min():.6e}, max={Ex.max():.6e} V/m')
    print(f'Ey: min={Ey.min():.6e}, max={Ey.max():.6e} V/m')
    print(f'Ez: min={Ez.min():.6e}, max={Ez.max():.6e} V/m')
    print('')

    # その他の情報
    voltages = data['voltages']
    charges = data['charges']

    print('=== Other information ===')
    print(f'Voltages: {voltages}')
    print(f'Total energy: {charges[0]:.6e} W')
    for n in range(1, len(charges)):
        print(f'  Electrode {n}: {charges[n]:.6e} C')
    print('')

    # 使用例: 特定の点の電位と電場を取得
    print('=== Example: Values at specific points ===')

    # 中心点
    i_center = nx // 2
    j_center = ny // 2
    k_center = nz // 2

    print(f'Center point ({i_center}, {j_center}, {k_center}):')
    print(f'  Position: ({x[i_center]:.3e}, {y[j_center]:.3e}, {z[k_center]:.3e})')
    print(f'  Potential: {V[k_center, j_center, i_center]:.6e} V')
    print(f'  E-field: {E[k_center, j_center, i_center]:.6e} V/m')
    print(f'  Ex: {Ex[k_center, j_center, i_center]:.6e} V/m')
    print(f'  Ey: {Ey[k_center, j_center, i_center]:.6e} V/m')
    print(f'  Ez: {Ez[k_center, j_center, i_center]:.6e} V/m')
    print('')

    # 電場が最大の点を探す
    max_idx = np.unravel_index(np.argmax(E), E.shape)
    k_max, j_max, i_max = max_idx

    print(f'Maximum E-field point ({i_max}, {j_max}, {k_max}):')
    print(f'  Position: ({x[i_max]:.3e}, {y[j_max]:.3e}, {z[k_max]:.3e})')
    print(f'  Potential: {V[k_max, j_max, i_max]:.6e} V')
    print(f'  E-field: {E[k_max, j_max, i_max]:.6e} V/m')
    print('')

    return data


def export_fields_to_text(npz_file, txt_file):
    """
    電場データをテキストファイルに変換

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
    V = data['potential']
    E = data['electric_field']
    Ex = data['electric_field_x']
    Ey = data['electric_field_y']
    Ez = data['electric_field_z']

    # テキストファイルに出力
    with open(txt_file, 'w', encoding='utf-8') as fp:
        fp.write(f'# Title: {data["title"]}\n')
        fp.write(f'# Grid: {nx} x {ny} x {nz}\n')
        fp.write(f'# Points: {nx+1} x {ny+1} x {nz+1}\n')
        fp.write('#\n')
        fp.write('#    i    j    k            X[m]            Y[m]            Z[m]')
        fp.write('            V[V]         E[V/m]        Ex[V/m]        Ey[V/m]        Ez[V/m]\n')

        count = 0
        for k in range(nz + 1):
            for j in range(ny + 1):
                for i in range(nx + 1):
                    fp.write('%6d%6d%6d%16.7e%16.7e%16.7e%16.7e%14.6e%14.6e%14.6e%14.6e\n' %
                             (i, j, k, x[i], y[j], z[k],
                              V[k, j, i], E[k, j, i],
                              Ex[k, j, i], Ey[k, j, i], Ez[k, j, i]))
                    count += 1

    print(f'Successfully wrote {count} points to {txt_file}')


def plot_field_distribution(npz_file):
    """
    電場分布をプロット

    Parameters:
    -----------
    npz_file : str
        npzファイル名
    """

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print('Error: matplotlib is required for plotting')
        print('Install with: pip install matplotlib')
        return

    # データ読み込み
    data = np.load(npz_file)
    x = data['x']
    y = data['y']
    z = data['z']
    V = data['potential']
    E = data['electric_field']

    nz = int(data['nz'])

    # Z=0平面に最も近い断面
    k_z0 = np.argmin(np.abs(z))
    V_xy = V[k_z0, :, :]
    E_xy = E[k_z0, :, :]

    # プロット
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # 電位分布
    im1 = axes[0].contourf(x, y, V_xy, levels=20, cmap='rainbow')
    fig.colorbar(im1, ax=axes[0], label='Potential [V]')
    axes[0].set_xlabel('X [m]')
    axes[0].set_ylabel('Y [m]')
    axes[0].set_title(f'Potential at Z = {z[k_z0]:.3e} m')
    axes[0].set_aspect('equal')

    # 電場分布
    im2 = axes[1].contourf(x, y, E_xy, levels=20, cmap='hot')
    fig.colorbar(im2, ax=axes[1], label='Electric Field [V/m]')
    axes[1].set_xlabel('X [m]')
    axes[1].set_ylabel('Y [m]')
    axes[1].set_title(f'Electric Field at Z = {z[k_z0]:.3e} m')
    axes[1].set_aspect('equal')

    plt.tight_layout()
    plt.show()


def main(argv):
    """
    メイン関数

    使い方:
        python read_fields_example.py <file.npz>
        python read_fields_example.py <file.npz> --to-text <output.txt>
        python read_fields_example.py <file.npz> --plot
    """

    if len(argv) < 2:
        print('Usage: python read_fields_example.py <file.npz> [options]')
        print('')
        print('Options:')
        print('  --to-text <output.txt>  : Convert to text file')
        print('  --plot                  : Plot field distribution')
        print('')
        print('Examples:')
        print('  python read_fields_example.py yoko.npz')
        print('  python read_fields_example.py yoko.npz --to-text yoko_fields.txt')
        print('  python read_fields_example.py yoko.npz --plot')
        sys.exit(1)

    npz_file = argv[1]

    # オプション処理
    if len(argv) > 2:
        if argv[2] == '--to-text':
            if len(argv) < 4:
                print('Error: --to-text requires output file name')
                sys.exit(1)
            txt_file = argv[3]
            export_fields_to_text(npz_file, txt_file)
        elif argv[2] == '--plot':
            plot_field_distribution(npz_file)
        else:
            print(f'Unknown option: {argv[2]}')
            sys.exit(1)
    else:
        # 読み込んで表示
        read_and_display_fields(npz_file)


if __name__ == "__main__":
    main(sys.argv)
