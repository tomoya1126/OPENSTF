# -*- coding: utf-8 -*-
# plot3d_geom.py

import matplotlib.pyplot as plt

# 物体形状を3D表示する
def plot(Parm, Nx, Ny, Nz, Xn, Yn, Zn, iGeometry, gline, mline):

    # figure
    strfig = 'OpenSTF - geometry (3D)'
    fig = plt.figure(strfig, figsize=(5, 5))  # 5 inches
    ax = fig.add_subplot(projection='3d')

    # X-const mesh
    for i in range(Nx + 1):
        x = [Xn[i]] * 3
        y = [Yn[0], Yn[0], Yn[-1]]
        z = [Zn[-1], Zn[0], Zn[0]]
        ax.plot(x, y, z, color='lightgray')

    # Y-const mesh
    for j in range(Ny + 1):
        y = [Yn[j]] * 3
        z = [Zn[0], Zn[0], Zn[-1]]
        x = [Xn[-1], Xn[0], Xn[0]]
        ax.plot(x, y, z, color='lightgray')

    # Z-const mesh
    for k in range(Nz + 1):
        z = [Zn[k]] * 3
        x = [Xn[0], Xn[0], Xn[-1]]
        y = [Yn[-1], Yn[0], Yn[0]]
        ax.plot(x, y, z, color='lightgray')

    # 物体形状
    for n in range(len(mline)):
        # 電極は黒、誘電体はマゼンタ
        color = 'k' if mline[n] < 0 else 'm'
        ax.plot([gline[n, 0, 0], gline[n, 1, 0]], \
                [gline[n, 0, 1], gline[n, 1, 1]], \
                [gline[n, 0, 2], gline[n, 1, 2]], color=color)

    # layout
    ax.grid(False)
    ax.set_aspect('equal')
    ax.view_init(elev = 30, azim = 30, roll = 0)

    # XYZ軸
    ax.set_xlim(Xn[0], Xn[-1])
    ax.set_ylim(Yn[0], Yn[-1])
    ax.set_zlim(Zn[0], Zn[-1])
    ax.set_xticks([Xn[0], Xn[-1]])
    ax.set_yticks([Yn[0], Yn[-1]])
    ax.set_zticks([Zn[0], Zn[-1]])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # タイトル
    nvolt = (iGeometry[:, 0] < 0).sum()
    nepsr = (iGeometry[:, 0] > 0).sum()
    ax.set_title('%s\nelectrodes = %d, dielectrics = %d, cells = %d x %d x %d' \
        % (Parm['title'], nvolt, nepsr, Nx, Ny, Nz))

    # show
    plt.show()
