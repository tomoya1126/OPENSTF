# OpenSTF Python版 - 入力ファイルの使い方

## 基本的な使い方

### 1. 入力ファイルの準備

OpenSTFは **`.ost`** 形式の入力ファイルを使います。

### 2. シミュレーションの実行

```bash
cd python
python ost.py [入力ファイル名]
```

**例**:
```bash
# デフォルトの入力ファイル（python.ost）を使用
python ost.py

# サンプルファイルを使用
python ost.py ../data/sample/1st_sample.ost

# カスタムファイルを使用
python ost.py my_input.ost
```

### 3. 出力ファイル

実行すると以下のファイルが生成されます：
- **`ost.npz`**: 計算結果（電位分布など）
- **`ost.log`**: 計算ログ

## 入力ファイル（.ost）の書き方

### 基本構造

```
OpenSTF 4 2
title = タイトル
xmesh = x座標定義
ymesh = y座標定義
zmesh = z座標定義
volt = 電圧定義
epsr = 比誘電率定義
geometry = 物体形状定義
solver = ソルバー設定
plotiter = 反復計算のプロット設定
plot1d = 1次元プロット設定
plot2d = 2次元プロット設定
end
```

### 詳細な入力項目

#### 1. ヘッダー（必須）
```
OpenSTF 4 2
```
- バージョン情報（4.2を意味する）

#### 2. タイトル
```
title = サンプル計算
```

#### 3. メッシュ定義（必須）

**書式**: `xmesh = 開始座標 分割数 終了座標 [分割数 終了座標 ...]`

```
xmesh = -5 50 5
ymesh = -5 50 5
zmesh = -5 50 5
```

これは：
- X方向: -5から5まで50分割（グリッド数51）
- Y方向: -5から5まで50分割
- Z方向: -5から5まで50分割

**可変メッシュの例**:
```
xmesh = 0 10 1 20 2 30 5
```
- 0から1まで10分割
- 1から2まで20分割
- 2から30まで5分割

#### 4. 電圧定義（必須、最低2個）

**書式**: `volt = 電圧値 ラベル`

```
volt = -1 -V
volt = +1 +V
volt = 0 GND
volt = 100 High
```

- 電圧番号は自動的に1, 2, 3, ... と割り当てられる

#### 5. 比誘電率定義

**書式**: `epsr = 比誘電率 ラベル`

```
epsr = 2.0 誘電体1
epsr = 4.0 誘電体2
```

#### 6. 物体形状定義（必須、最低2個）

**書式**: `geometry = タイプ 番号 形状 座標パラメータ`

- **タイプ**: `1`=電極、`2`=誘電体
- **番号**: 電圧番号または誘電率番号（1から始まる）
- **形状**: 形状コード
- **座標**: 形状に応じて6個または8個

**形状コード**:
- `1`: 直方体（6パラメータ: x1 x2 y1 y2 z1 z2）
- `2`: 楕円体（6パラメータ: x1 x2 y1 y2 z1 z2）
- `11`: X軸円柱（6パラメータ: x1 x2 y1 y2 z1 z2）
- `12`: Y軸円柱（6パラメータ: x1 x2 y1 y2 z1 z2）
- `13`: Z軸円柱（6パラメータ: x1 x2 y1 y2 z1 z2）
- `31`, `32`, `33`: 円錐（8パラメータ）
- `41`, `42`, `43`: 四角錐（8パラメータ）
- `51`, `52`, `53`: その他（8パラメータ）

**例**:
```
# 電極1（電圧番号1）を直方体で定義
geometry = 1 1 1 -2 2 -2 2 -2 2

# 誘電体1（誘電率番号1）を直方体で定義
geometry = 2 1 1 -1 1 -1 1 -1 1

# 電極2（電圧番号2）を楕円体で定義
geometry = 1 2 2 -3 3 -3 3 -3 3
```

#### 7. ソルバー設定

**書式**: `solver = omega 最大反復回数 表示間隔 収束判定値`

```
solver = 1.95 1000 50 1e-5
```

- **omega**: 加速係数（SOR法、1.0〜2.0、通常1.8〜1.95）
- **最大反復回数**: 1000など
- **表示間隔**: 50反復ごとに経過を表示
- **収束判定値**: 1e-5など（残差がこの値以下で収束）

#### 8. プロット設定

##### 3D形状プロット
```
plot3dgeom = 1
```
- `1`で有効、`0`または省略で無効

##### 反復計算プロット
```
plotiter = 1
```

##### 1次元プロット
```
plot1d = 成分 方向 位置1 位置2
1ddb = 0/1          # dB表示 0=OFF/1=ON
1dscale = min max 分割数  # スケール指定
1dlog = 0/1         # ログ出力 0=OFF/1=ON
```

**例**:
```
plot1d = V Z 0 0    # Z方向の電位分布（X=0, Y=0）
plot1d = E X 0 0    # X方向の電界分布（Y=0, Z=0）
1ddb = 0
1dlog = 1
```

##### 2次元プロット
```
plot2d = 成分 方向 位置
2dfigure = 幅 高さ
2ddb = 0/1          # dB表示
2dscale = min max 分割数  # スケール指定
2dcontour = 0/1/2/3 # 0=塗りつぶし、1=等高線、2=塗りつぶしグレー、3=等高線グレー
2dobject = 1 電極表示 誘電体表示  # 1 1 1で両方表示
2dzoom = x1 x2 y1 y2  # ズーム範囲
2dlog = 0/1         # ログ出力 0=OFF/1=ON
```

**例**:
```
plot2d = V X 0      # X=0平面の電位分布
plot2d = E Y 0      # Y=0平面の電界分布
2ddb = 0
2dcontour = 0
2dobject = 1 1
2dlog = 1
```

**成分**:
- `V`: 電位
- `E`: 電界の大きさ
- `Ex`, `Ey`, `Ez`: 電界の各成分
- `D`: 電束密度の大きさ
- `Dx`, `Dy`, `Dz`: 電束密度の各成分
- `Q`: 電荷密度

#### 9. 終了マーク（必須）
```
end
```

## 完全な入力ファイルの例

### 例1: 簡単な立方体電極

```
OpenSTF 4 2
title = 立方体電極のサンプル
xmesh = -5 50 5
ymesh = -5 50 5
zmesh = -5 50 5
volt = -1 -V
volt = +1 +V
epsr = 2.0 誘電体
geometry = 2 1 1 -2 2 -2 2 -2 2
geometry = 1 1 1 -2 2 -2 2 -2 -2
geometry = 1 2 1 -2 2 -2 2 2 2
solver = 1.95 1000 50 1e-5
plotiter = 1
plot1d = V Z 0 0
1dlog = 1
plot2d = V X 0
plot2d = E X 0
2dcontour = 0
2dobject = 1 1
2dlog = 1
end
```

### 例2: 同軸ケーブル

```
OpenSTF 4 2
title = 同軸ケーブル
xmesh = -5 40 5
ymesh = -5 40 5
zmesh = -1 10 1
volt = 1 内部導体
volt = 0 外部導体
epsr = 2.3 ポリエチレン
geometry = 1 1 13 -1 1 -1 1 -1 1
geometry = 2 1 13 -1 1 -3 3 -1 1
geometry = 1 2 13 -1 1 -5 5 -1 1
solver = 1.90 2000 100 1e-6
plotiter = 1
plot2d = V Z 0
2ddb = 0
2dcontour = 0
2dobject = 1 1
2dlog = 1
end
```

## コマンドラインオプション

`ost.py`は以下のオプションを受け付けます：

```bash
python ost.py [オプション] [入力ファイル]
```

**オプション**:
- `-cpu` / `-gpu`: CPU/GPU計算
- `-n <スレッド数>`: Numbaスレッド数（デフォルト: 4）
- `-p <x> <y> <z>`: MPI領域分割数
- `-vector` / `-no-vector`: ベクトル化ON/OFF
- `-single` / `-double`: 単精度/倍精度
- `-prompt`: 終了時にプロンプト表示
- `--help`: ヘルプ表示
- `--version`: バージョン表示

**例**:
```bash
# 8スレッドで実行
python ost.py -n 8 my_input.ost

# 倍精度で実行
python ost.py -double my_input.ost

# MPI並列（2×2×1分割）
mpiexec -n 4 python ost.py -p 2 2 1 my_input.ost
```

## サンプルファイル

`data/sample/` ディレクトリに多数のサンプルがあります：

```bash
ls data/sample/
```

- `1st_sample.ost`: 最初のサンプル
- `coax.ost`: 同軸ケーブル
- `sphere_c.ost`, `sphere_d.ost`: 球体
- `cylinder.ost`: 円柱
- `needle.ost`: 針電極
- その他

**サンプルの実行**:
```bash
cd python
python ost.py ../data/sample/1st_sample.ost
```

## トラブルシューティング

### エラー: "*** no X mesh"
- `xmesh`、`ymesh`、`zmesh`のいずれかが定義されていません

### エラー: "*** number of volt.s < 2"
- `volt`定義が2個未満です。最低2個必要です

### エラー: "*** number of geometry data < 2"
- `geometry`定義が2個未満です。最低2個必要です

### エラー: "*** invalid geometry (volt) index"
- `geometry`で指定した電圧番号が存在しません

### ファイルが見つからない
```bash
# ost.py からの相対パスを確認
pwd  # 現在のディレクトリを確認
ls my_input.ost  # ファイルの存在を確認
```

## 次のステップ

1. **計算実行**: `python ost.py input.ost`
2. **結果確認**: `ost.log`でログを確認
3. **可視化**: `python ost_post.py`でグラフ表示
4. **データ出力**: 全座標の電位を出力する場合は`EXPORT_POTENTIAL_README.md`を参照
