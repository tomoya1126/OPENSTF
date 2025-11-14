# すべての座標の電位を出力する方法

## 概要

このプログラムは、OpenSTFの計算結果（`ost.npz`）から、すべての3次元グリッド座標とその電位を出力します。

## 出力される情報

- **インデックス**: (i, j, k) - グリッド上の点のインデックス
- **座標**: (X, Y, Z) - 実際の物理座標 [m]
- **電位**: V - 各点での電位 [V]

## 使用方法

### 方法1: コマンドラインから直接実行

```bash
cd python
python -m post.export_all_potential [npz_file] [output_file] [format]
```

**引数**:
- `npz_file`: 入力ファイル（デフォルト: `ost.npz`）
- `output_file`: 出力ファイル（デフォルト: `all_potential.txt`）
- `format`: 出力形式 `txt` または `csv`（デフォルト: `txt`）

**例**:
```bash
# デフォルト設定で実行
python -m post.export_all_potential

# CSV形式で出力
python -m post.export_all_potential ost.npz all_potential.csv csv

# カスタムファイル名で出力
python -m post.export_all_potential my_result.npz my_output.txt txt
```

### 方法2: Pythonスクリプトから呼び出し

サンプルスクリプト `export_potential_example.py` を参照してください。

```python
import sys
sys.path.insert(0, 'python')
from post.export_all_potential import export_all_potential

# テキスト形式で出力
export_all_potential('ost.npz', 'all_potential.txt', 'txt')

# CSV形式で出力
export_all_potential('ost.npz', 'all_potential.csv', 'csv')
```

または、リポジトリのルートディレクトリから：

```bash
python export_potential_example.py
```

## 出力フォーマット

### テキスト形式 (`txt`)

```
# Title: サンプルタイトル
# Grid: 10 x 10 x 10 = 1000 cells
# Points: 1331
#
#    i    j    k            X[m]            Y[m]            Z[m]            V[V]
     0     0     0   0.0000000e+00   0.0000000e+00   0.0000000e+00   1.2345678e+00
     1     0     0   1.0000000e-03   0.0000000e+00   0.0000000e+00   1.2340000e+00
     ...
```

- フィールドは空白で区切られ、整列されている
- 座標と電位は指数表記（16桁幅、小数点以下7桁）
- インデックスは整数（6桁幅）

### CSV形式 (`csv`)

```csv
i,j,k,X[m],Y[m],Z[m],V[V]
0,0,0,0.000000000000000e+00,0.000000000000000e+00,0.000000000000000e+00,1.234567890123450e+00
1,0,0,1.000000000000000e-03,0.000000000000000e+00,0.000000000000000e+00,1.234000000000000e+00
...
```

- カンマ区切り
- 座標と電位は指数表記（小数点以下15桁）
- ExcelやPandasで読み込みやすい

## 数値フォーマットのカスタマイズ

出力フォーマットを変更したい場合は、`python/post/export_all_potential.py` の以下の行を編集してください：

**テキスト形式**（60-61行目付近）:
```python
data_format = '%6d%6d%6d%16.7e%16.7e%16.7e%16.7e\n'
```

**CSV形式**（56-57行目付近）:
```python
data_format = '%d,%d,%d,%.15e,%.15e,%.15e,%.15e\n'
```

### フォーマット指定子の意味

- `%6d`: 6桁幅の整数
- `%16.7e`: 16桁幅、指数表記、小数点以下7桁
- `%.15e`: 指数表記、小数点以下15桁
- `%16.7f`: 16桁幅、固定小数点、小数点以下7桁（指数表記なし）

### 例: より高精度な出力

```python
# 小数点以下15桁、20桁幅に変更
data_format = '%6d%6d%6d%20.15e%20.15e%20.15e%20.15e\n'
```

### 例: 固定小数点表記に変更

```python
# 指数表記（e）を使わない固定小数点表記
data_format = '%6d%6d%6d%16.7f%16.7f%16.7f%16.7f\n'
```

## 実行例

### 1. シミュレーション実行

```bash
cd python
python ost.py python.ost
```

これにより `ost.npz` と `ost.log` が生成されます。

### 2. 電位データを出力

```bash
# python ディレクトリにいる場合
python -m post.export_all_potential

# ルートディレクトリにいる場合
python export_potential_example.py
```

### 3. 結果の確認

```bash
# 最初の50行を表示
head -n 50 all_potential.txt

# ファイルサイズを確認
ls -lh all_potential.txt

# 行数を確認（グリッドポイント数+ヘッダー）
wc -l all_potential.txt
```

## 注意事項

- 大きなグリッド（例: 100×100×100 = 1,030,301点）の場合、出力ファイルサイズが大きくなります（数十〜数百MB）
- メモリ不足にならないよう、システムの空きメモリを確認してください
- 非常に大きなデータセットの場合は、HDF5やバイナリ形式での出力を検討してください

## トラブルシューティング

### エラー: `ModuleNotFoundError: No module named 'post'`

```bash
# python ディレクトリから実行してください
cd python
python -m post.export_all_potential
```

または

```bash
# PYTHONPATH を設定
export PYTHONPATH=/path/to/OPENSTF/python:$PYTHONPATH
python -m post.export_all_potential
```

### エラー: `FileNotFoundError: ost.npz`

先にシミュレーションを実行して `ost.npz` を生成してください：

```bash
python ost.py python.ost
```
