# -*- coding: utf-8 -*-
"""
すべての座標の電位を出力するサンプルスクリプト

使用例：
1. シミュレーション実行後、ost.npzが生成されている状態で実行
2. このスクリプトを実行すると、all_potential.txt が生成される
"""

import sys
sys.path.insert(0, 'python')

from post.export_all_potential import export_all_potential

# 例1: デフォルト設定で出力（テキスト形式）
# ost.npz を読み込み、all_potential.txt に出力
export_all_potential('ost.npz', 'all_potential.txt', 'txt')

# 例2: CSV形式で出力
# export_all_potential('ost.npz', 'all_potential.csv', 'csv')

# 例3: 異なるファイル名で出力
# export_all_potential('my_result.npz', 'my_potential.txt', 'txt')

print("電位データの出力が完了しました。")
