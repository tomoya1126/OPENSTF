# -*- coding: utf-8 -*-
"""
export_all_potential.py
すべての座標の電位を出力するプログラム
"""

import sys
import os
import numpy as np

# パスを追加（このスクリプトの親ディレクトリをパスに追加）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from post.load_bin import load

def export_all_potential(npz_file='ost.npz', output_file='all_potential.txt', output_format='txt'):
    """
    計算したすべての座標の電位を出力する

    Parameters:
    -----------
    npz_file : str
        入力ファイル名（デフォルト: 'ost.npz'）
    output_file : str
        出力ファイル名（デフォルト: 'all_potential.txt'）
    output_format : str
        出力フォーマット 'txt' または 'csv'（デフォルト: 'txt'）
    """

    print(f'Reading data from {npz_file}...')

    # データ読み込み
    Nx, Ny, Nz, Ni, Nj, Nk, N0, \
    Xn, Yn, Zn, RXp, RXm, RYp, RYm, RZp, RZm, \
    idVolt, idEpsr, fEpsr, V, nRes, fRes, iRes, \
    gline, mline, Title, EPS0 = load(npz_file)

    print(f'Grid size: Nx={Nx}, Ny={Ny}, Nz={Nz}')
    print(f'Total points: {(Nx+1) * (Ny+1) * (Nz+1)}')
    print(f'Writing to {output_file}...')

    # ファイルに出力
    with open(output_file, 'w', encoding='utf-8') as fp:

        # ヘッダー
        fp.write(f'# Title: {Title}\n')
        fp.write(f'# Grid: {Nx} x {Ny} x {Nz} = {Nx*Ny*Nz} cells\n')
        fp.write(f'# Points: {(Nx+1) * (Ny+1) * (Nz+1)}\n')
        fp.write('#\n')

        if output_format == 'csv':
            # CSVフォーマット
            fp.write('i,j,k,X[m],Y[m],Z[m],V[V]\n')
            delimiter = ','
            data_format = '%d,%d,%d,%.15e,%.15e,%.15e,%.15e\n'
        else:
            # テキストフォーマット（整列）
            fp.write('#    i    j    k            X[m]            Y[m]            Z[m]            V[V]\n')
            delimiter = ' '
            data_format = '%6d%6d%6d%16.7e%16.7e%16.7e%16.7e\n'

        # すべての座標について出力
        count = 0
        for k in range(Nz + 1):
            for j in range(Ny + 1):
                for i in range(Nx + 1):
                    # インデックスから配列インデックスを計算
                    idx = k * Ni * Nj + j * Ni + i

                    # 座標と電位を出力
                    fp.write(data_format % (i, j, k, Xn[i], Yn[j], Zn[k], V[idx]))
                    count += 1

        print(f'Successfully wrote {count} points')

def main(argv):
    """
    メイン関数

    使い方:
    python export_all_potential.py [npz_file] [output_file] [format]

    例:
    python export_all_potential.py ost.npz all_potential.txt txt
    python export_all_potential.py ost.npz all_potential.csv csv
    """

    # デフォルト値
    npz_file = 'ost.npz'
    output_file = 'all_potential.txt'
    output_format = 'txt'

    # 引数処理
    if len(argv) > 1:
        npz_file = argv[1]
    if len(argv) > 2:
        output_file = argv[2]
    if len(argv) > 3:
        output_format = argv[3]
        if output_format not in ['txt', 'csv']:
            print('Error: format must be "txt" or "csv"')
            print('Usage: python export_all_potential.py [npz_file] [output_file] [format]')
            sys.exit(1)

    # 実行
    try:
        export_all_potential(npz_file, output_file, output_format)
        print('Done!')
    except FileNotFoundError as e:
        print(f'Error: File not found - {e}')
        sys.exit(1)
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main(sys.argv)
