# -*- coding: utf-8 -*-
"""
OpenSTF (Python)
ost_post.py : post
"""

import matplotlib.pyplot as plt
import post.load_bin, post.post_data, post.plotiter, post.plot1d, post.plot2d

def main():

    # [0-1] read post data
    ost_in = 'python.ost'
    Post = post.post_data.data(ost_in)

    # [0-2] load
    fn_out = 'ost.npz'
    Nx, Ny, Nz, Ni, Nj, Nk, N0, \
    Xn, Yn, Zn, RXp, RXm, RYp, RYm, RZp, RZm, \
    idVolt, idEpsr, fEpsr, V, nRes, fRes, iRes, \
    gline, mline, Title, EPS0 \
    = post.load_bin.load(fn_out)
    Post['title'] = Title
    Post['EPS0'] = EPS0

    # [0-3] ウィンドウの大きさ他
    Post['w2d'] = [6.0, 4.0]  # width, height [inch]
    # フォント
    plt.rcParams['font.family'] = ['sans-serif', 'serif', 'monospace', 'MS gothic', 'MS mincho'][0]  # 0/1/2/3/4
    plt.rcParams['font.size'] = 10  # fontsize [pixel]

    # [1] 収束状況 (2D)
    if Post['iter'] > 0:
        post.plotiter.plot(Post, nRes, fRes, iRes)

    # [2] 線上分布図 (2D)
    if len(Post['p1ddir']) > 0:
        post.plot1d.plot(Post, Nx, Ny, Nz, Ni, Nj, Nk, N0,
            Xn, Yn, Zn, RXp, RXm, RYp, RYm, RZp, RZm,
            idVolt, idEpsr, fEpsr, V)

    # [3] 面上分布図 (2D)
    if len(Post['p2ddir']) > 0:
        post.plot2d.plot(Post, Nx, Ny, Nz, Ni, Nj, Nk, N0,
            Xn, Yn, Zn, RXp, RXm, RYp, RYm, RZp, RZm,
            idVolt, idEpsr, fEpsr, V, gline, mline)

# entry point
if __name__ == "__main__":
    main()
