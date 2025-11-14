# -*- coding: utf-8 -*-
# input_data.py

import numpy as np

def read(fn, Parm):

    # 計算パラメーター(辞書型)
    Parm['title']      = ''
    Parm['solver']     = [1.95, 1000, 50, 1e-5]
    Parm['plot3dgeom'] = 0

    # 変数初期化
    #ierr = 0
    Nx = Ny = Nz = 0
    Xn = Yn = Zn = None

    # ファイルを読み込む
    with open(fn, encoding='utf-8') as fp:
        header = fp.readline()
        lines = fp.readlines()

    # 配列の大きさを調べる
    # 誘電体の電圧と電極の誘電率のために+1しておく
    nvolt = 1
    nepsr = 1
    ngeometry = 0
    for tline in lines:
        if tline.strip().startswith('volt = '):
            nvolt += 1
        if tline.strip().startswith('epsr = '):
            nepsr += 1
        if tline.strip().startswith('geometry = '):
            ngeometry += 1
    if ngeometry < 2:
        print('*** number of geometry data < 2')
        return

    # 配列を確保する
    fVolt = np.zeros(nvolt, 'f8')
    fEpsr = np.zeros(nepsr, 'f8')
    iGeometry = np.zeros((ngeometry, 2), 'i4')
    fGeometry = np.zeros((ngeometry, 8), 'f8')
    
    # 誘電体の電圧と電極の比誘電率
    fVolt[0] = 0
    fEpsr[0] = 1   # 静電エネルギー計算のために必要

    # ヘッダー
    d = header.strip().split()
    if (len(d) < 3) or (d[0] != 'OpenSTF'):
        print('*** Not OpenSTF data : %s' % fn)
        return
    version = (100 * int(d[1])) + int(d[2])
    if version < 301:
        print('*** version of data is old : %s.%s < 3.1' % (d[1], d[2]))
        return

    # 本体
    nvolt = 1
    nepsr = 1
    ngeometry = 0
    for tline in lines:
        # token
        d = tline.strip().split()  #;print(d)
        
        # check
        if d[0].startswith('#'):
            continue
        elif (d[0] == 'end'):
            break
        elif (len(d) < 3):
            continue
        elif (d[1] != "="):
            continue

        # parameter array
        p = d[2:]  #;print(p)
        
        # input
        key = d[0]
        if   key == 'title':
            Parm['title'] = tline[len('title = '):].strip()
        elif key == 'xmesh':
            Nx, Xn = _makemesh(p)
        elif key == 'ymesh':
            Ny, Yn = _makemesh(p)
        elif key == 'zmesh':
            Nz, Zn = _makemesh(p)
        elif key == 'volt':
            fVolt[nvolt] = float(p[0])
            nvolt += 1
        elif key == 'epsr':
            fEpsr[nepsr] = float(p[0])
            nepsr += 1
        elif key == 'geometry':
            if len(p) > 8:
                # p[0]=1/2 : 電極/誘電体
                # p[1]=1,2,3,... : 属性番号
                index = int(p[1])
                shape = int(p[2])
                # 電極のとき: ID=-1,-2,-3,...(属性番号に負号をつける)
                # 誘電体のとき; ID=1,2,3,...
                iGeometry[ngeometry, 0] = -index if p[0] == '1' else index
                # 形状番号=1,2,11,...
                iGeometry[ngeometry, 1] = shape
                # 座標値(6個または8個)
                #ndata = 6 if shape in [1, 2, 11, 12, 13] else 8
                ndata = 0
                if shape in [1, 2, 11, 12, 13]:
                    ndata = 6
                elif shape in [31, 32, 33, 41, 42, 43, 51, 52, 53]:
                    ndata = 8
                fGeometry[ngeometry, 0:ndata] = [float(g) for g in p[3:3+ndata]]
                ngeometry += 1
        elif key == 'solver':
            if len(p) > 3:
                Parm['solver'] = [float(p[0]), int(p[1]), int(p[2]), float(p[3])]
        elif key == 'plot3dgeom':
            Parm['plot3dgeom'] = int(p[0])  # new

    # error check

    if Nx <= 0:
        print('*** no X mesh')
        #ierr = 1
    if Ny <= 0:
        print('*** no Y mesh')
        #ierr = 1
    if Nz <= 0:
        print('*** no Z mesh')
        #ierr = 1

    if nvolt < 1 + 2:
        # 電圧は最低2個必要
        print('*** number of volt.s < 2')
        #ierr = 1

    for n in range(iGeometry.shape[0]):
        if (iGeometry[n, 0] < 0) and (-iGeometry[n, 0] > nvolt):
            print('*** invalid geometry (volt) index')
            #ierr = 1
        if (iGeometry[n, 0] > 0) and (+iGeometry[n, 0] > nepsr):
            print('*** invalid geometry (epsr) index')
            #ierr = 1
        if not iGeometry[n, 1] in [1, 2, 11, 12, 13, 31, 32, 33, 41, 42, 43, 51, 52, 53]:
            print('*** invalid geometry index')
            #ierr = 1

    if (Parm['solver'][1] <= 0) or (Parm['solver'][2] <= 0):
        print('*** invalid solver data')
        #ierr = 1

    # 厚さのない物体形状を節点に寄せる
    _fit_geometry(Xn, Yn, Zn, iGeometry, fGeometry)

    #print(Parm)
    #print(Nx, Ny, Nz)
    #print(Xn, Yn, Zn)
    #print(fVolt)
    #print(fEpsr)
    #print(iGeometry)
    #print(fGeometry)
    return Parm, Nx, Ny, Nz, Xn, Yn, Zn, fVolt, fEpsr, iGeometry, fGeometry

# (private) 節点データ作成
def _makemesh(p):
    EPS = 1e-12

    # error check
    if len(p) < 3:  # データ数は最低3個
        print('*** number of mesh data < 3')
        return None
    if (len(p) % 2 == 1) and (float(p[0]) > float(p[-1])):
        p = p[::-1]  # 座標が降順なら昇順に変換する

    # 区間配列作成
    pos = np.zeros(0, 'f8')
    div = np.zeros(0, 'i4')
    for i, d in enumerate(p):
        if i % 2 == 0:
            # 区間座標
            if (i > 0) and (abs(float(d) - pos[-1]) < EPS):
                # 区間幅が0ならその区間を削除する
                div = np.delete(div, i // 2 - 1)
                continue
            pos = np.append(pos, float(d))
        else:
            # 区間分割数
            if int(d) <= 0:
                # 区間分割数は正
                print('*** division of mesh <= 0')
                return None
            div = np.append(div, int(d))

    # error check
    if (len(pos) < 2) or (len(div) < 1):
        # 区間座標は最低2個、区間分割数は最低1個必要
        print('*** no valid mesh data')
        return None

    # 節点データ作成
    node = np.array(pos[0], float)  # 最初
    for i in range(len(div)):
        dl = (pos[i + 1] - pos[i]) / div[i]
        node = np.append(node, np.linspace(pos[i] + dl, pos[i + 1], div[i]))
    #print(node)
    
    return len(node) - 1, node

# 厚さのない物体形状を節点に寄せる
def _fit_geometry(Xn, Yn, Zn, iGeometry, fGeometry):

    if (Xn is None) or (Yn is None) or (Zn is None):
        return

    # 長さ次元の微小量
    eps = 1e-6 * (
        abs(Xn[0] - Xn[-1]) +
        abs(Yn[0] - Yn[-1]) +
        abs(Zn[0] - Zn[-1]))

    for n in range(iGeometry.shape[0]):
        s = iGeometry[n, 1]
        p = fGeometry[n, :]
        x1, x2, y1, y2, z1, z2 = p[0:6]

        if   (s == 1) or (s == 2):
            # rectangle, ellipsoid
            if abs(x1 - x2) < eps:
                i = np.argmin(abs(Xn - x1))
                p[0:2] = Xn[i]
            if abs(y1 - y2) < eps:
                j = np.argmin(abs(Yn - y1))
                p[2:4] = Yn[j]
            if abs(z1 - z2) < eps:
                k = np.argmin(abs(Zn - z1))
                p[4:6] = Zn[k]
        elif s == 11:
            # X cylinder
            if abs(x1 - x2) < eps:
                i = np.argmin(abs(Xn - x1))
                p[0:2] = Xn[i]
        elif s == 12:
            # Y cylinder
            if abs(y1 - y2) < eps:
                j = np.argmin(abs(Yn - y1))
                p[2:4] = Yn[j]
        elif s == 13:
            # Z cylinder
            if abs(z1 - z2) < eps:
                k = np.argmin(abs(Zn - z1))
                p[4:6] = Zn[k]
