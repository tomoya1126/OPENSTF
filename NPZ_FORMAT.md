# NPZファイルフォーマット詳細

## 概要

`run_and_export.py`で生成されるnpzファイルには、シミュレーション結果として全点の座標と電位が保存されています。

## 使い方

### 1. 計算実行とnpz出力

```bash
cd python
python run_and_export.py simple_example.ost
# → simple_example.npz が生成される

python run_and_export.py ../data/sample/1st_sample.ost
# → 1st_sample.npz が生成される

# 出力ファイル名を指定
python run_and_export.py input.ost output.npz
```

### 2. npzファイルの読み込み

```bash
# ファイル内容を確認
python read_npz_example.py simple_example.npz

# テキストファイルに変換
python read_npz_example.py simple_example.npz --to-text output.txt
```

## NPZファイルの構造

npzファイルはNumPyの圧縮アーカイブ形式で、以下のキーと配列を含みます：

### メタデータ

| キー | 型 | 説明 |
|------|------|------|
| `title` | str | シミュレーションのタイトル |
| `nx` | int | X方向のグリッド数（セル数） |
| `ny` | int | Y方向のグリッド数（セル数） |
| `nz` | int | Z方向のグリッド数（セル数） |
| `eps0` | float | 真空の誘電率 [F/m] |

**注意**: グリッド点数は `nx+1`, `ny+1`, `nz+1` です。

### 座標配列

| キー | 形状 | 型 | 説明 |
|------|------|------|------|
| `x` | `(nx+1,)` | float | X座標配列 [m] |
| `y` | `(ny+1,)` | float | Y座標配列 [m] |
| `z` | `(nz+1,)` | float | Z座標配列 [m] |

### 電位配列

| キー | 形状 | 型 | 説明 |
|------|------|------|------|
| `potential` | `(nz+1, ny+1, nx+1)` | float | 電位分布 [V] |

**インデックス**:
- `potential[k, j, i]` = 座標 `(x[i], y[j], z[k])` での電位
- 配列の順序: `(Z, Y, X)`

### その他の情報

| キー | 形状 | 型 | 説明 |
|------|------|------|------|
| `voltages` | `(n_volt,)` | float | 電圧リスト [V] |
| `dielectrics` | `(n_epsr,)` | float | 比誘電率リスト |
| `charges` | `(n_volt+1,)` | float | 電荷と総エネルギー |

**charges配列**:
- `charges[0]`: 総静電エネルギー [W]
- `charges[1:]`: 各電極の電荷 [C]

### 収束情報

| キー | 形状 | 型 | 説明 |
|------|------|------|------|
| `iteration_steps` | `(n_iter,)` | int | 反復回数のリスト |
| `residuals` | `(n_iter,)` | float | 残差のリスト |
| `iteration_indices` | `(n_iter,)` | int | 反復インデックス |

## Pythonでの読み込み例

### 基本的な読み込み

```python
import numpy as np

# ファイルを開く
data = np.load('simple_example.npz')

# メタデータを取得
title = str(data['title'])
nx = int(data['nx'])
ny = int(data['ny'])
nz = int(data['nz'])

# 座標配列を取得
x = data['x']  # shape: (nx+1,)
y = data['y']  # shape: (ny+1,)
z = data['z']  # shape: (nz+1,)

# 電位配列を取得
V = data['potential']  # shape: (nz+1, ny+1, nx+1)

print(f'Grid size: {nx} x {ny} x {nz}')
print(f'Potential shape: {V.shape}')
print(f'Potential range: [{V.min():.3e}, {V.max():.3e}] V')
```

### 特定の点の電位を取得

```python
import numpy as np

data = np.load('simple_example.npz')
x = data['x']
y = data['y']
z = data['z']
V = data['potential']

# 中心点の電位
i_center = len(x) // 2
j_center = len(y) // 2
k_center = len(z) // 2

v_center = V[k_center, j_center, i_center]
print(f'Center: ({x[i_center]:.3e}, {y[j_center]:.3e}, {z[k_center]:.3e})')
print(f'Potential: {v_center:.6e} V')

# 特定座標に最も近い点の電位を取得
target_x, target_y, target_z = 1.0, 0.0, 0.0
i = np.argmin(np.abs(x - target_x))
j = np.argmin(np.abs(y - target_y))
k = np.argmin(np.abs(z - target_z))

v_target = V[k, j, i]
print(f'Nearest to ({target_x}, {target_y}, {target_z}):')
print(f'Actual: ({x[i]:.3e}, {y[j]:.3e}, {z[k]:.3e})')
print(f'Potential: {v_target:.6e} V')
```

### 2次元断面を取得

```python
import numpy as np
import matplotlib.pyplot as plt

data = np.load('simple_example.npz')
x = data['x']
y = data['y']
z = data['z']
V = data['potential']

# Z=0平面に最も近い断面
k_z0 = np.argmin(np.abs(z))
V_xy = V[k_z0, :, :]  # shape: (ny+1, nx+1)

# プロット
plt.figure(figsize=(8, 6))
plt.contourf(x, y, V_xy, levels=20, cmap='rainbow')
plt.colorbar(label='Potential [V]')
plt.xlabel('X [m]')
plt.ylabel('Y [m]')
plt.title(f'Potential at Z = {z[k_z0]:.3e} m')
plt.axis('equal')
plt.show()
```

### 1次元プロットを作成

```python
import numpy as np
import matplotlib.pyplot as plt

data = np.load('simple_example.npz')
x = data['x']
y = data['y']
z = data['z']
V = data['potential']

# X=0, Y=0 のZ方向プロット
i_x0 = np.argmin(np.abs(x))
j_y0 = np.argmin(np.abs(y))
V_z = V[:, j_y0, i_x0]  # Z方向の電位分布

plt.figure(figsize=(8, 6))
plt.plot(z, V_z, 'b-', linewidth=2)
plt.xlabel('Z [m]')
plt.ylabel('Potential [V]')
plt.title(f'Potential along Z-axis (X={x[i_x0]:.3e}, Y={y[j_y0]:.3e})')
plt.grid(True)
plt.show()
```

### 全データをループで処理

```python
import numpy as np

data = np.load('simple_example.npz')
nx = int(data['nx'])
ny = int(data['ny'])
nz = int(data['nz'])
x = data['x']
y = data['y']
z = data['z']
V = data['potential']

# 全点をループ
for k in range(nz + 1):
    for j in range(ny + 1):
        for i in range(nx + 1):
            pos_x = x[i]
            pos_y = y[j]
            pos_z = z[k]
            potential = V[k, j, i]

            # 何か処理をする
            # 例: 電位が特定範囲内の点を抽出
            if 0.5 <= potential <= 1.0:
                print(f'({pos_x:.3e}, {pos_y:.3e}, {pos_z:.3e}): {potential:.6e} V')
```

### CSVファイルに変換

```python
import numpy as np
import csv

data = np.load('simple_example.npz')
nx = int(data['nx'])
ny = int(data['ny'])
nz = int(data['nz'])
x = data['x']
y = data['y']
z = data['z']
V = data['potential']

# CSVファイルに出力
with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)

    # ヘッダー
    writer.writerow(['i', 'j', 'k', 'X[m]', 'Y[m]', 'Z[m]', 'V[V]'])

    # データ
    for k in range(nz + 1):
        for j in range(ny + 1):
            for i in range(nx + 1):
                writer.writerow([i, j, k, x[i], y[j], z[k], V[k, j, i]])

print('Exported to output.csv')
```

### Pandasを使った処理

```python
import numpy as np
import pandas as pd

data = np.load('simple_example.npz')
nx = int(data['nx'])
ny = int(data['ny'])
nz = int(data['nz'])
x = data['x']
y = data['y']
z = data['z']
V = data['potential']

# DataFrameを作成
records = []
for k in range(nz + 1):
    for j in range(ny + 1):
        for i in range(nx + 1):
            records.append({
                'i': i,
                'j': j,
                'k': k,
                'X': x[i],
                'Y': y[j],
                'Z': z[k],
                'V': V[k, j, i]
            })

df = pd.DataFrame(records)

# データ分析
print(df.describe())

# 条件抽出
high_potential = df[df['V'] > 0.5]
print(high_potential)

# CSV出力
df.to_csv('output.csv', index=False)
```

## ファイルサイズの目安

グリッドサイズとファイルサイズの関係（単精度の場合）：

| グリッド | 点数 | ファイルサイズ（概算） |
|----------|------|------------------------|
| 10×10×10 | 1,331 | ~5 KB |
| 50×50×50 | 132,651 | ~0.5 MB |
| 100×100×100 | 1,030,301 | ~4 MB |
| 200×200×200 | 8,120,601 | ~32 MB |

倍精度の場合は約2倍のサイズになります。

## 注意事項

1. **配列の順序**: `potential[k, j, i]` の順序は `(Z, Y, X)` です
2. **インデックス範囲**: `i`は`0`から`nx`、`j`は`0`から`ny`、`k`は`0`から`nz`
3. **座標取得**: `(x[i], y[j], z[k])` で実際の物理座標を取得
4. **メモリ**: 大きなグリッドの場合、メモリ使用量に注意

## トラブルシューティング

### エラー: `KeyError: 'potential'`

古いフォーマットのnpzファイルの可能性があります。`run_and_export.py`で再度生成してください。

### メモリ不足

非常に大きなグリッド（例: 500×500×500）の場合、メモリ不足になる可能性があります。部分的に読み込むか、より小さなグリッドで計算してください。

### 配列の形状が合わない

```python
# 形状を確認
print(f'x: {x.shape}')
print(f'y: {y.shape}')
print(f'z: {z.shape}')
print(f'V: {V.shape}')

# V の形状は (nz+1, ny+1, nx+1) であるべき
assert V.shape == (nz+1, ny+1, nx+1)
```

## サンプルプログラム

- **`read_npz_example.py`**: npzファイルを読み込んで内容を表示
- **`python read_npz_example.py file.npz --to-text output.txt`**: テキストに変換

## 関連ドキュメント

- **`INPUT_GUIDE.md`**: 入力ファイルの書き方
- **`EXPORT_POTENTIAL_README.md`**: 既存の電位出力プログラム
