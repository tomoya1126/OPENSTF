# yoko.ostファイルを計算して電場を出力する方法

## Windowsのファイルをこの環境で使う手順

### 方法1: ファイルをアップロード

1. Windowsからyoko.ostファイルをこの環境にアップロード/コピー
2. `python`ディレクトリに配置

### 方法2: 内容をコピー＆ペースト

1. Windowsでyoko.ostファイルをテキストエディタで開く
2. 内容をすべてコピー
3. この環境で新しいファイルを作成してペースト

```bash
# python ディレクトリに移動
cd /home/user/OPENSTF/python

# ファイルを作成（エディタで開く、または以下のコマンド）
# 内容をペースト
```

## 電場を含めて計算・出力

### ステップ1: 計算実行

```bash
cd /home/user/OPENSTF/python
python run_and_export_fields.py yoko.ost
```

これで **`yoko.npz`** が生成されます。中には：
- 全グリッド点の座標 (X, Y, Z)
- 各点の電位 V
- **各点の電場 E, Ex, Ey, Ez**  ← これが追加されました！
- その他の計算結果

が含まれています。

### ステップ2: 結果を確認

```bash
python read_fields_example.py yoko.npz
```

出力例：
```
=== Metadata ===
Title: yoko
Grid size: 50 x 50 x 50
Points: 51 x 51 x 51 = 132651

=== Potential (V) ===
Min: 0.000000e+00 V
Max: 1.000000e+00 V

=== Electric Field (E) ===
Min: 0.000000e+00 V/m
Max: 1.234567e+05 V/m
Mean: 5.678900e+04 V/m

=== Electric Field Components ===
Ex: min=-5.000e+04, max=5.000e+04 V/m
Ey: min=-3.000e+04, max=3.000e+04 V/m
Ez: min=-8.000e+04, max=8.000e+04 V/m
```

### ステップ3: テキストファイルに変換（オプション）

```bash
python read_fields_example.py yoko.npz --to-text yoko_fields.txt
```

出力される`yoko_fields.txt`の形式：
```
#    i    j    k            X[m]            Y[m]            Z[m]            V[V]         E[V/m]        Ex[V/m]        Ey[V/m]        Ez[V/m]
     0     0     0   0.0000000e+00   0.0000000e+00   0.0000000e+00   1.0000000e+00  1.2345e+05  5.0000e+04  3.0000e+04  8.0000e+04
     1     0     0   1.0000000e-03   0.0000000e+00   0.0000000e+00   9.9500000e-01  1.2300e+05  4.9000e+04  2.9000e+04  7.9000e+04
     ...
```

各列の意味：
- `i, j, k`: グリッドインデックス
- `X, Y, Z`: 座標 [m]
- `V`: 電位 [V]
- `E`: 電場の大きさ [V/m]
- `Ex, Ey, Ez`: 電場の各成分 [V/m]

### ステップ4: グラフ表示（オプション）

```bash
python read_fields_example.py yoko.npz --plot
```

電位分布と電場分布のグラフが表示されます。

## Pythonで電場データを使う

### 基本的な読み込み

```python
import numpy as np

# ファイルを開く
data = np.load('yoko.npz')

# 座標配列
x = data['x']
y = data['y']
z = data['z']

# 電位配列
V = data['potential']  # shape: (nz+1, ny+1, nx+1)

# 電場配列
E  = data['electric_field']    # 電場の大きさ [V/m]
Ex = data['electric_field_x']  # X方向成分 [V/m]
Ey = data['electric_field_y']  # Y方向成分 [V/m]
Ez = data['electric_field_z']  # Z方向成分 [V/m]

print(f'電場の最大値: {E.max():.6e} V/m')
print(f'電場の最小値: {E.min():.6e} V/m')
```

### 特定の点の電場を取得

```python
import numpy as np

data = np.load('yoko.npz')
x = data['x']
y = data['y']
z = data['z']
E = data['electric_field']
Ex = data['electric_field_x']
Ey = data['electric_field_y']
Ez = data['electric_field_z']

# 中心点の電場
i_center = len(x) // 2
j_center = len(y) // 2
k_center = len(z) // 2

e_mag = E[k_center, j_center, i_center]
e_x = Ex[k_center, j_center, i_center]
e_y = Ey[k_center, j_center, i_center]
e_z = Ez[k_center, j_center, i_center]

print(f'中心点の座標: ({x[i_center]:.3e}, {y[j_center]:.3e}, {z[k_center]:.3e})')
print(f'電場の大きさ: {e_mag:.6e} V/m')
print(f'電場ベクトル: ({e_x:.6e}, {e_y:.6e}, {e_z:.6e}) V/m')
```

### 電場が最大の点を探す

```python
import numpy as np

data = np.load('yoko.npz')
x = data['x']
y = data['y']
z = data['z']
E = data['electric_field']

# 最大値のインデックスを取得
max_idx = np.unravel_index(np.argmax(E), E.shape)
k_max, j_max, i_max = max_idx

print(f'電場最大点のインデックス: ({i_max}, {j_max}, {k_max})')
print(f'座標: ({x[i_max]:.3e}, {y[j_max]:.3e}, {z[k_max]:.3e})')
print(f'電場の大きさ: {E[k_max, j_max, i_max]:.6e} V/m')
```

### 特定の条件を満たす点を抽出

```python
import numpy as np

data = np.load('yoko.npz')
x = data['x']
y = data['y']
z = data['z']
E = data['electric_field']

nx = int(data['nx'])
ny = int(data['ny'])
nz = int(data['nz'])

# 電場が1e5 V/m以上の点を抽出
threshold = 1e5
high_field_points = []

for k in range(nz + 1):
    for j in range(ny + 1):
        for i in range(nx + 1):
            if E[k, j, i] >= threshold:
                high_field_points.append({
                    'index': (i, j, k),
                    'position': (x[i], y[j], z[k]),
                    'field': E[k, j, i]
                })

print(f'電場が {threshold:.0e} V/m 以上の点: {len(high_field_points)}個')

# 上位10点を表示
sorted_points = sorted(high_field_points, key=lambda p: p['field'], reverse=True)
for n, point in enumerate(sorted_points[:10], 1):
    print(f'{n}. 座標: {point["position"]}, 電場: {point["field"]:.6e} V/m')
```

### 2次元断面の電場分布をプロット

```python
import numpy as np
import matplotlib.pyplot as plt

data = np.load('yoko.npz')
x = data['x']
y = data['y']
z = data['z']
E = data['electric_field']

# Z=0平面に最も近い断面
k_z0 = np.argmin(np.abs(z))
E_xy = E[k_z0, :, :]  # この平面の電場分布

# プロット
plt.figure(figsize=(10, 8))
plt.contourf(x, y, E_xy, levels=20, cmap='hot')
plt.colorbar(label='Electric Field [V/m]')
plt.xlabel('X [m]')
plt.ylabel('Y [m]')
plt.title(f'Electric Field at Z = {z[k_z0]:.3e} m')
plt.axis('equal')
plt.show()
```

### 電場ベクトルを矢印でプロット

```python
import numpy as np
import matplotlib.pyplot as plt

data = np.load('yoko.npz')
x = data['x']
y = data['y']
z = data['z']
Ex = data['electric_field_x']
Ey = data['electric_field_y']

# Z=0平面
k_z0 = np.argmin(np.abs(z))
Ex_xy = Ex[k_z0, :, :]
Ey_xy = Ey[k_z0, :, :]

# 矢印の間隔（すべての点を表示すると密集するため間引く）
skip = 5

plt.figure(figsize=(10, 8))
plt.quiver(x[::skip], y[::skip],
           Ex_xy[::skip, ::skip], Ey_xy[::skip, ::skip],
           scale=1e6)
plt.xlabel('X [m]')
plt.ylabel('Y [m]')
plt.title(f'Electric Field Vectors at Z = {z[k_z0]:.3e} m')
plt.axis('equal')
plt.show()
```

### CSVファイルに変換

```python
import numpy as np
import csv

data = np.load('yoko.npz')
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

# CSVファイルに出力
with open('yoko_fields.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)

    # ヘッダー
    writer.writerow(['i', 'j', 'k', 'X[m]', 'Y[m]', 'Z[m]',
                     'V[V]', 'E[V/m]', 'Ex[V/m]', 'Ey[V/m]', 'Ez[V/m]'])

    # データ
    for k in range(nz + 1):
        for j in range(ny + 1):
            for i in range(nx + 1):
                writer.writerow([
                    i, j, k,
                    x[i], y[j], z[k],
                    V[k, j, i],
                    E[k, j, i],
                    Ex[k, j, i],
                    Ey[k, j, i],
                    Ez[k, j, i]
                ])

print('Exported to yoko_fields.csv')
```

## 完全な実行手順（まとめ）

```bash
# 1. python ディレクトリに移動
cd /home/user/OPENSTF/python

# 2. yoko.ostファイルを配置（アップロードまたはコピー）

# 3. 計算実行（電場も含めて出力）
python run_and_export_fields.py yoko.ost

# 4. 結果を確認
python read_fields_example.py yoko.npz

# 5. テキストファイルに変換（オプション）
python read_fields_example.py yoko.npz --to-text yoko_fields.txt

# 6. グラフ表示（オプション）
python read_fields_example.py yoko.npz --plot
```

## 2つのプログラムの違い

| プログラム | 出力内容 | 計算時間 | 用途 |
|------------|----------|----------|------|
| `run_and_export.py` | 電位のみ | 速い | 電位分布だけが必要な場合 |
| `run_and_export_fields.py` | 電位＋電場 | やや遅い | **電場が必要な場合（推奨）** |

**yoko.ostで電場を出すには `run_and_export_fields.py` を使ってください。**

## トラブルシューティング

### yoko.ostが見つからない

```bash
# ファイルの存在確認
ls -la yoko.ost

# ない場合はアップロード/コピーしてください
```

### 計算に時間がかかる

- グリッド数が大きい場合、電場計算に時間がかかります
- プログラムが進行状況を表示します: `Progress: 50.0%`

### メモリ不足

- グリッド数を減らす（入力ファイルのメッシュ定義を調整）

## 関連ドキュメント

- **`INPUT_GUIDE.md`**: 入力ファイルの書き方
- **`NPZ_FORMAT.md`**: npzファイルフォーマット
- **`QUICK_START.md`**: クイックスタート
