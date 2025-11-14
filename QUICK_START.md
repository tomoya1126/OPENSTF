# クイックスタートガイド

OpenSTF Python版の簡単な使い方を説明します。

## 最も簡単な使い方

### 1. シミュレーション実行 → npz出力（ワンステップ）

```bash
cd python
python run_and_export.py simple_example.ost
```

これで **`simple_example.npz`** が生成されます。中には：
- 全グリッド点の座標 (X, Y, Z)
- 各点の電位 V
- その他の計算結果

が含まれています。

### 2. npzファイルの中身を確認

```bash
python read_npz_example.py simple_example.npz
```

出力例：
```
=== Metadata ===
Title: 簡単なサンプル - 平行平板コンデンサ
Grid size: 20 x 20 x 20
Points: 21 x 21 x 21 = 9261

=== Potential array ===
Shape: (21, 21, 21)
Min: 0.000000e+00 V
Max: 1.000000e+00 V
```

### 3. テキストファイルに変換（必要に応じて）

```bash
python read_npz_example.py simple_example.npz --to-text output.txt
```

## 3つの使い方パターン

### パターン1: ワンステップ実行（推奨）

**入力 → 計算 → npz出力**を一度に実行

```bash
cd python
python run_and_export.py input.ost
# → input.npz が生成される
```

**特徴**:
- 最も簡単
- 入力ファイル名から自動的に出力ファイル名を決定
- 座標と電位をnpz形式で保存

### パターン2: 従来の方法

**計算**と**出力**を分けて実行

```bash
# 1. 計算実行
python ost.py input.ost
# → ost.npz が生成される

# 2. ポストプロセス（グラフ表示）
python ost_post.py

# 3. 全電位をテキスト出力（オプション）
python -m post.export_all_potential
# → all_potential.txt が生成される
```

**特徴**:
- 従来の標準的な使い方
- グラフ表示が可能
- テキスト出力も可能

### パターン3: カスタマイズ

Pythonスクリプトから直接呼び出し

```python
import numpy as np

# npzファイルを読み込む
data = np.load('simple_example.npz')

# 座標と電位を取得
x = data['x']
y = data['y']
z = data['z']
V = data['potential']  # 3次元配列 (nz+1, ny+1, nx+1)

# 特定点の電位を取得
i, j, k = 10, 10, 10
print(f'Position: ({x[i]}, {y[j]}, {z[k]})')
print(f'Potential: {V[k, j, i]} V')
```

## 主なファイル

### 入力ファイル

| ファイル | 説明 |
|----------|------|
| `*.ost` | 入力ファイル（計算条件を記述） |

### プログラム

| ファイル | 説明 |
|----------|------|
| `run_and_export.py` | **新**: 入力→計算→npz出力（ワンステップ） |
| `ost.py` | 計算実行（従来の方法） |
| `ost_post.py` | グラフ表示（従来の方法） |
| `read_npz_example.py` | **新**: npzファイルの読み込み例 |

### 出力ファイル

| ファイル | 説明 |
|----------|------|
| `*.npz` | **新**: 座標と電位（NumPy圧縮形式） |
| `ost.npz` | 計算結果（従来形式、内部データ含む） |
| `ost.log` | 計算ログ |
| `all_potential.txt` | 全電位のテキスト出力（オプション） |

## サンプルファイル

```bash
# サンプル一覧
ls data/sample/

# 実行例
cd python
python run_and_export.py simple_example.ost
python run_and_export.py ../data/sample/1st_sample.ost
python run_and_export.py ../data/sample/coax.ost
```

主なサンプル：
- `simple_example.ost` - 平行平板コンデンサ（最も簡単）
- `1st_sample.ost` - 基本サンプル
- `coax.ost` - 同軸ケーブル
- `sphere_c.ost` - 球体（導体）
- `cylinder.ost` - 円柱

## 入力ファイルの書き方（最小限）

```
OpenSTF 4 2
title = タイトル
xmesh = -10 20 10
ymesh = -10 20 10
zmesh = -10 20 10
volt = 1.0 電極1
volt = 0.0 電極2
geometry = 1 1 1 -8 8 -8 8 5 5
geometry = 1 2 1 -8 8 -8 8 -5 -5
solver = 1.95 1000 50 1e-5
end
```

詳細は **`INPUT_GUIDE.md`** を参照してください。

## NPZファイルの使い方

### 基本的な読み込み

```python
import numpy as np

data = np.load('file.npz')

# メタデータ
nx = int(data['nx'])
ny = int(data['ny'])
nz = int(data['nz'])

# 座標配列
x = data['x']  # shape: (nx+1,)
y = data['y']  # shape: (ny+1,)
z = data['z']  # shape: (nz+1,)

# 電位配列
V = data['potential']  # shape: (nz+1, ny+1, nx+1)

# 特定点の電位
v = V[k, j, i]  # (x[i], y[j], z[k]) の電位
```

詳細は **`NPZ_FORMAT.md`** を参照してください。

## よくある質問

### Q1. 一番簡単な方法は？

```bash
cd python
python run_and_export.py simple_example.ost
```

これで `simple_example.npz` が生成されます。

### Q2. npzファイルの中身を見るには？

```bash
python read_npz_example.py simple_example.npz
```

### Q3. テキストファイルが欲しい

```bash
python read_npz_example.py simple_example.npz --to-text output.txt
```

### Q4. グラフを表示したい

従来の方法を使います：

```bash
python ost.py input.ost
python ost_post.py
```

### Q5. カスタム処理をしたい

Pythonスクリプトで直接npzファイルを読み込みます：

```python
import numpy as np
data = np.load('file.npz')
# ... 処理 ...
```

## 詳細ドキュメント

- **`INPUT_GUIDE.md`**: 入力ファイルの詳しい書き方
- **`NPZ_FORMAT.md`**: npzファイルフォーマットの詳細
- **`EXPORT_POTENTIAL_README.md`**: テキスト出力の詳細

## トラブルシューティング

### ファイルが見つからない

```bash
# 現在のディレクトリを確認
pwd

# python ディレクトリにいることを確認
cd /path/to/OPENSTF/python
```

### モジュールが見つからない

```bash
# python ディレクトリから実行してください
cd python
python run_and_export.py input.ost
```

### 計算が終わらない

- グリッド数を減らす（メッシュ定義の分割数を減らす）
- 収束判定値を緩くする（`solver`の4番目の値を大きくする）

## 次のステップ

1. サンプルファイルで試す
   ```bash
   cd python
   python run_and_export.py simple_example.ost
   ```

2. 結果を確認
   ```bash
   python read_npz_example.py simple_example.npz
   ```

3. 自分の入力ファイルを作成（`INPUT_GUIDE.md`参照）

4. カスタム処理を実装（`NPZ_FORMAT.md`参照）
