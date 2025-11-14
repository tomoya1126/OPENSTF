# -*- coding: utf-8 -*-
"""
plot_slice.py
NPZファイルから特定の位置での断面の電位分布をプロット

使い方:
    python plot_slice.py yoko.npz --z 430e-6
    python plot_slice.py yoko.npz --x 0.001
    python plot_slice.py yoko.npz --y 0
"""

import sys
import numpy as np
import matplotlib.pyplot as plt


def plot_slice(npz_file, axis='z', position=0.0, save_fig=None):
    """
    特定の位置での断面の電位分布をプロット

    Parameters:
    -----------
    npz_file : str
        npzファイル名
    axis : str
        'x', 'y', または 'z'
    position : float
        位置 [m]
    save_fig : str, optional
        図を保存するファイル名
    """

    print(f'Reading: {npz_file}')

    # データ読み込み
    data = np.load(npz_file)

    x = data['x']
    y = data['y']
    z = data['z']
    V = data['potential']

    nx = int(data['nx'])
    ny = int(data['ny'])
    nz = int(data['nz'])

    title = str(data['title'])

    print(f'Title: {title}')
    print(f'Grid: {nx} x {ny} x {nz}')
    print(f'X range: [{x.min():.6e}, {x.max():.6e}] m')
    print(f'Y range: [{y.min():.6e}, {y.max():.6e}] m')
    print(f'Z range: [{z.min():.6e}, {z.max():.6e}] m')
    print('')

    # 指定位置に最も近いインデックスを見つける
    if axis.lower() == 'x':
        idx = np.argmin(np.abs(x - position))
        actual_pos = x[idx]
        V_slice = V[:, :, idx]  # shape: (nz+1, ny+1)
        x_axis = y
        y_axis = z
        x_label = 'Y [m]'
        y_label = 'Z [m]'
        slice_label = f'X = {actual_pos:.6e} m'

    elif axis.lower() == 'y':
        idx = np.argmin(np.abs(y - position))
        actual_pos = y[idx]
        V_slice = V[:, idx, :]  # shape: (nz+1, nx+1)
        x_axis = x
        y_axis = z
        x_label = 'X [m]'
        y_label = 'Z [m]'
        slice_label = f'Y = {actual_pos:.6e} m'

    elif axis.lower() == 'z':
        idx = np.argmin(np.abs(z - position))
        actual_pos = z[idx]
        V_slice = V[idx, :, :]  # shape: (ny+1, nx+1)
        x_axis = x
        y_axis = y
        x_label = 'X [m]'
        y_label = 'Y [m]'
        slice_label = f'Z = {actual_pos:.6e} m'

    else:
        print(f'Error: Invalid axis "{axis}". Use "x", "y", or "z".')
        return

    print(f'Requested position: {position:.6e} m')
    print(f'Actual position: {actual_pos:.6e} m')
    print(f'Index: {idx}')
    print(f'Slice shape: {V_slice.shape}')
    print(f'Potential range: [{V_slice.min():.6e}, {V_slice.max():.6e}] V')
    print('')

    # プロット
    fig, ax = plt.subplots(figsize=(10, 8))

    # コンター図
    levels = 20
    contour = ax.contourf(x_axis, y_axis, V_slice, levels=levels, cmap='rainbow')
    cbar = fig.colorbar(contour, ax=ax, label='Potential [V]')

    # ラベルとタイトル
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.set_title(f'{title}\nPotential Distribution at {slice_label}', fontsize=14)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    # 保存または表示
    if save_fig:
        plt.savefig(save_fig, dpi=150, bbox_inches='tight')
        print(f'Figure saved to {save_fig}')
    else:
        plt.show()


def plot_slice_with_field(npz_file, axis='z', position=0.0, save_fig=None):
    """
    電場データも含む場合のプロット（2つのサブプロット）

    Parameters:
    -----------
    npz_file : str
        npzファイル名
    axis : str
        'x', 'y', または 'z'
    position : float
        位置 [m]
    save_fig : str, optional
        図を保存するファイル名
    """

    print(f'Reading: {npz_file}')

    # データ読み込み
    data = np.load(npz_file)

    # 電場データがあるかチェック
    has_field = 'electric_field' in data.files

    x = data['x']
    y = data['y']
    z = data['z']
    V = data['potential']

    if has_field:
        E = data['electric_field']

    nx = int(data['nx'])
    ny = int(data['ny'])
    nz = int(data['nz'])
    title = str(data['title'])

    print(f'Title: {title}')
    print(f'Grid: {nx} x {ny} x {nz}')
    print(f'Has electric field data: {has_field}')
    print('')

    # 指定位置に最も近いインデックスを見つける
    if axis.lower() == 'x':
        idx = np.argmin(np.abs(x - position))
        actual_pos = x[idx]
        V_slice = V[:, :, idx]
        if has_field:
            E_slice = E[:, :, idx]
        x_axis = y
        y_axis = z
        x_label = 'Y [m]'
        y_label = 'Z [m]'
        slice_label = f'X = {actual_pos:.6e} m'

    elif axis.lower() == 'y':
        idx = np.argmin(np.abs(y - position))
        actual_pos = y[idx]
        V_slice = V[:, idx, :]
        if has_field:
            E_slice = E[:, idx, :]
        x_axis = x
        y_axis = z
        x_label = 'X [m]'
        y_label = 'Z [m]'
        slice_label = f'Y = {actual_pos:.6e} m'

    elif axis.lower() == 'z':
        idx = np.argmin(np.abs(z - position))
        actual_pos = z[idx]
        V_slice = V[idx, :, :]
        if has_field:
            E_slice = E[idx, :, :]
        x_axis = x
        y_axis = y
        x_label = 'X [m]'
        y_label = 'Y [m]'
        slice_label = f'Z = {actual_pos:.6e} m'

    print(f'Requested: {axis.upper()} = {position:.6e} m')
    print(f'Actual: {axis.upper()} = {actual_pos:.6e} m (index {idx})')
    print('')

    # プロット
    if has_field:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    else:
        fig, ax1 = plt.subplots(1, 1, figsize=(10, 8))

    # 電位分布
    levels = 20
    c1 = ax1.contourf(x_axis, y_axis, V_slice, levels=levels, cmap='rainbow')
    fig.colorbar(c1, ax=ax1, label='Potential [V]')
    ax1.set_xlabel(x_label, fontsize=12)
    ax1.set_ylabel(y_label, fontsize=12)
    ax1.set_title(f'Potential at {slice_label}', fontsize=12)
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3)

    # 電場分布
    if has_field:
        c2 = ax2.contourf(x_axis, y_axis, E_slice, levels=levels, cmap='hot')
        fig.colorbar(c2, ax=ax2, label='Electric Field [V/m]')
        ax2.set_xlabel(x_label, fontsize=12)
        ax2.set_ylabel(y_label, fontsize=12)
        ax2.set_title(f'Electric Field at {slice_label}', fontsize=12)
        ax2.set_aspect('equal')
        ax2.grid(True, alpha=0.3)

    plt.suptitle(title, fontsize=14, y=0.98)
    plt.tight_layout()

    # 保存または表示
    if save_fig:
        plt.savefig(save_fig, dpi=150, bbox_inches='tight')
        print(f'Figure saved to {save_fig}')
    else:
        plt.show()


def main(argv):
    """
    メイン関数

    使い方:
        python plot_slice.py file.npz --z 430e-6
        python plot_slice.py file.npz --x 0.001
        python plot_slice.py file.npz --y 0
        python plot_slice.py file.npz --z 430e-6 --save figure.png
        python plot_slice.py file.npz --z 430e-6 --with-field
    """

    if len(argv) < 2:
        print('Usage: python plot_slice.py <file.npz> --<axis> <position> [options]')
        print('')
        print('Arguments:')
        print('  file.npz          : NPZ file to read')
        print('  --x <position>    : X position in meters')
        print('  --y <position>    : Y position in meters')
        print('  --z <position>    : Z position in meters')
        print('')
        print('Options:')
        print('  --save <filename> : Save figure to file')
        print('  --with-field      : Plot electric field (if available)')
        print('')
        print('Examples:')
        print('  python plot_slice.py yoko.npz --z 430e-6')
        print('  python plot_slice.py yoko.npz --z 0.00043')
        print('  python plot_slice.py yoko.npz --x 0.001 --save output.png')
        print('  python plot_slice.py yoko.npz --z 430e-6 --with-field')
        sys.exit(1)

    npz_file = argv[1]

    # デフォルト値
    axis = 'z'
    position = 0.0
    save_fig = None
    with_field = False

    # 引数解析
    i = 2
    while i < len(argv):
        arg = argv[i].lower()

        if arg == '--x':
            axis = 'x'
            position = float(argv[i + 1])
            i += 2
        elif arg == '--y':
            axis = 'y'
            position = float(argv[i + 1])
            i += 2
        elif arg == '--z':
            axis = 'z'
            position = float(argv[i + 1])
            i += 2
        elif arg == '--save':
            save_fig = argv[i + 1]
            i += 2
        elif arg == '--with-field':
            with_field = True
            i += 1
        else:
            print(f'Unknown argument: {arg}')
            sys.exit(1)

    # プロット実行
    if with_field:
        plot_slice_with_field(npz_file, axis, position, save_fig)
    else:
        plot_slice(npz_file, axis, position, save_fig)


if __name__ == "__main__":
    main(sys.argv)
