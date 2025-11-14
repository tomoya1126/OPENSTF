# -*- coding: utf-8 -*-
# plot1d.py

import datetime
import numpy as np
import matplotlib.pyplot as plt
import sol.vedq

# plot V/E/D/Q along lines (2D)
def plot(Post, Nx, Ny, Nz, Ni, Nj, Nk, N0,
    Xn, Yn, Zn, RXp, RXm, RYp, RYm, RZp, RZm,
    idVolt, idEpsr, fEpsr, V):

    EPS = 1e-15

    # component, unit, color
    compolabel = ['V', 'E', 'Ex', 'Ey', 'Ez', 'D', 'Dx', 'Dy', 'Dz', 'Q']
    compocolor = ['k', 'k', 'r', 'g', 'b', 'k', 'r', 'g', 'b', 'k']
    compodict = { \
        'V' : [[0],          ['[V]',     '[V]']],             \
        'E' : [[1, 2, 3, 4], ['[V/m]',   '[dBV/m]']],         \
        'D' : [[5, 6, 7, 8], [r'$[C/m^2]$', r'$[dBC/m^2]$']], \
        'Q' : [[9],          [r'$[C/m^3]$', r'$[dBC/m^3]$']]}

    # 1d.log
    if Post['p1dlog'] == 1:
        fn = '1d.log'
        fp = open(fn, 'wt', encoding='utf-8')

    nline = len(Post['p1ddir'])
    idb = Post['p1ddb']

    for iline in range(nline):
        compo = Post['p1dcompo'][iline]
        cdir  = Post['p1ddir'][iline]
        pos   = Post['p1dpos'][iline]

        # X, Y data
        if   cdir == 'X':
            pos[0] = max(Yn[0], min(Yn[-1], pos[0]))
            pos[1] = max(Zn[0], min(Zn[-1], pos[1]))
            j = np.argmin(abs(pos[0] - Yn))
            k = np.argmin(abs(pos[1] - Zn))
            x = Xn
            y = np.zeros((Nx + 1, 10), float)
            for i in range(Nx + 1):
                y[i] = sol.vedq.calc(
                    i, j, k, Nx, Ny, Nz, Ni, Nj, Nk, N0,
                    Xn, Yn, Zn, RXp, RXm, RYp, RYm, RZp, RZm,
                    idVolt, idEpsr, fEpsr, V, Post['EPS0'])
            strline = 'Y = %g[m], Z = %g[m]' % (pos[0], pos[1])
        elif cdir == 'Y':
            pos[0] = max(Zn[0], min(Zn[-1], pos[0]))
            pos[1] = max(Xn[0], min(Xn[-1], pos[1]))
            k = np.argmin(abs(pos[0] - Zn))
            i = np.argmin(abs(pos[1] - Xn))
            x = Yn
            y = np.zeros((Ny + 1, 10), float)
            for j in range(Ny + 1):
                y[j] = sol.vedq.calc(
                    i, j, k, Nx, Ny, Nz, Ni, Nj, Nk, N0,
                    Xn, Yn, Zn, RXp, RXm, RYp, RYm, RZp, RZm,
                    idVolt, idEpsr, fEpsr, V, Post['EPS0'])
            strline = 'Z = %g[m], X = %g[m]' % (pos[0], pos[1])
        elif cdir == 'Z':
            pos[0] = max(Xn[0], min(Xn[-1], pos[0]))
            pos[1] = max(Yn[0], min(Yn[-1], pos[1]))
            i = np.argmin(abs(pos[0] - Xn))
            j = np.argmin(abs(pos[1] - Yn))
            x = Zn
            y = np.zeros((Nz + 1, 10), float)
            for k in range(Nz + 1):
                y[k] = sol.vedq.calc(
                    i, j, k, Nx, Ny, Nz, Ni, Nj, Nk, N0,
                    Xn, Yn, Zn, RXp, RXm, RYp, RYm, RZp, RZm,
                    idVolt, idEpsr, fEpsr, V, Post['EPS0'])
            strline = 'X = %g[m], Y = %g[m]' % (pos[0], pos[1])

        # dBに変換する (V = y[:, 0] は除く)
        if Post['p1ddb'] == 1:
            y[:, 1:] = 20 * np.log10(np.maximum(np.abs(y[:, 1:]), EPS))

        # log出力
        if Post['p1dlog'] == 1:
            _log_1d(fp, Post, iline, x, y)

        # figure
        strfig = 'OpenSTF - %s along %s-line (%d/%d) - %s' % (compo, cdir, iline + 1, nline, datetime.datetime.now().ctime())
        fig = plt.figure(strfig, figsize=(Post['w2d'][0], Post['w2d'][1]))
        ax = fig.add_subplot()
        
        # layout
        ax.grid(True)
    
        # plot (1 or 4 lines)
        for ic in compodict[compo][0]:
            #print(ic)
            ax.plot(x, y[:, ic], color=compocolor[ic], label=compolabel[ic])

        # 最小・最大
        #fmax = np.max(y[:, compodict[compo][0][0]])
        #fmin = np.min(y[:, compodict[compo][0][0]])
        fmin = +float('inf')
        fmax = -float('inf')
        for ic in compodict[compo][0]:
            fmax = max(fmax, max(y[:, ic]))
            fmin = min(fmin, min(y[:, ic]))
        #print(iline, compo, fmin, fmax)

        # Y-axis
        ax.set_ylabel(compo + ' ' + compodict[compo][1][idb])
        if Post['p1dscale'][0] == 1:
            # 指定スケール
            ymin = Post['p1dscale'][1]
            ymax = Post['p1dscale'][2]
            ydiv = Post['p1dscale'][3]
            ax.set_ylim(ymin, ymax)
            ax.set_yticks(np.linspace(ymin, ymax, ydiv + 1))
        else:
            # 自動スケール
            ymax = fmax
            if (Post['p1ddb'] == 1) and (compo != 'V'):
                # dB幅は自動では40dB(V以外)
                ymin = ymax - 40
            else:
                ymin = fmin
            ax.set_ylim(ymin, ymax)

        # X-axis
        ax.set_xlabel(cdir + ' [m] (' + strline + ')')
        ax.set_xlim(x[0], x[-1])

        # legend
        if len(compodict[compo][0]) > 1:
            ax.legend(loc='best')

        # title
        strunit = compodict[compo][1][idb]
        ax.set_title('%s\nmax = %.4g%s, min = %.4g%s'
            % (Post['title'], fmax, strunit, fmin, strunit))

        # show
        plt.show()

# log (private)
def _log_1d(fp, Post, iline, x, y):

    # header
    fp.write('   No.          %c[m]          V[V]' % Post['p1ddir'][iline])
    if Post['p1ddb'] == 0:
        fp.write('        E[V/m]       Ex[V/m]       Ey[V/m]       Ez[V/m]      D[C/m^2]     Dx[C/m^2]     Dy[C/m^2]     Dz[C/m^2]      Q[C/m^3]\n')
        fmt = '%14.5e'
    else:
        fp.write('     E[dBV/m]    Ex[dBV/m]    Ey[dBV/m]    Ez[dBV/m]   D[dBC/m^2]  Dx[dBC/m^2]  Dy[dBC/m^2]  Dz[dBC/m^2]   Q[dBC/m^3]\n')
        fmt = '%13.5f'

    # data
    for n in range(len(x)):
        fp.write('%6d%14.5e%14.5e' % (n, x[n], y[n, 0]))
        for ic in range(1, 10):
            fp.write(fmt % y[n, ic])
        fp.write('\n')
