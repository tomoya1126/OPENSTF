# -*- coding: utf-8 -*-
# plot2d.py

import numpy as np
import matplotlib.pyplot as plt
import datetime
import sol.vedq

# plot V/E/D/Q on planes (2D)
def plot(Post, Nx, Ny, Nz, Ni, Nj, Nk, N0,
    Xn, Yn, Zn, RXp, RXm, RYp, RYm, RZp, RZm,
    idVolt, idEpsr, fEpsr, V, gline, mline):

    EPS = 1e-15

    # component, unit
    compolabel = ['V', 'E', 'Ex', 'Ey', 'Ez', 'D', 'Dx', 'Dy', 'Dz', 'Q']
    compounit = [
        ['[V]', '[V/m]',   '[V/m]',   '[V/m]',   '[V/m]',   r'$[C/m^2]$',   r'$[C/m^2]$',   r'$[C/m^2]$',   r'$[C/m^2]$',   r'$[C/m^3]$'], \
        ['[V]', '[dBV/m]', '[dBV/m]', '[dBV/m]', '[dBV/m]', r'$[dBC/m^2]$', r'$[dBC/m^2]$', r'$[dBC/m^2]$', r'$[dBC/m^2]$', r'$[dBC/m^3]$']]

    # 2d.log
    if Post['p2dlog'] == 1:
        fn = '2d.log'
        fp = open(fn, 'wt', encoding='utf-8')
    
    nplane = len(Post['p2ddir'])
    idb = Post['p2ddb']

    for iplane in range(nplane):
        compo  = Post['p2dcompo'][iplane]
        cdir   = Post['p2ddir'][iplane]
        pos    = Post['p2dpos'][iplane]
        icompo = compolabel.index(compo)
        sunit  = compounit[idb][icompo]

        # X, Y data
        if   cdir == 'X':
            pos = max(Xn[0], min(Xn[-1], pos))
            i = np.argmin(abs(pos - Xn))
            x = Yn
            y = Zn
            z = np.zeros((Nz + 1, Ny + 1), float)
            zall = np.zeros((Nz + 1, Ny + 1, 10), float)
            for j in range(Ny + 1):
                for k in range(Nz + 1):
                    zall[k, j] = sol.vedq.calc(
                        i, j, k, Nx, Ny, Nz, Ni, Nj, Nk, N0,
                        Xn, Yn, Zn, RXp, RXm, RYp, RYm, RZp, RZm,
                        idVolt, idEpsr, fEpsr, V, Post['EPS0'])
                    z[k, j] = zall[k, j, icompo]
            xlabel = 'Y [m]'
            ylabel = 'Z [m]'
            strplane = 'X = %g[m]' % pos
        elif cdir == 'Y':
            pos = max(Yn[0], min(Yn[-1], pos))
            j = np.argmin(abs(pos - Yn))
            x = Xn
            y = Zn
            z = np.zeros((Nz + 1, Nx + 1), float)
            zall = np.zeros((Nz +1, Nx + 1, 10), float)
            for i in range(Nx + 1):
                for k in range(Nz + 1):
                    zall[k, i] = sol.vedq.calc(
                        i, j, k, Nx, Ny, Nz, Ni, Nj, Nk, N0,
                        Xn, Yn, Zn, RXp, RXm, RYp, RYm, RZp, RZm,
                        idVolt, idEpsr, fEpsr, V, Post['EPS0'])
                    z[k, i] = zall[k, i, icompo]
            xlabel= 'X [m]'
            ylabel = 'Z [m]'
            strplane = 'Y = %g[m]' % pos
        elif cdir == 'Z':
            pos = max(Zn[0], min(Zn[-1], pos))
            k = np.argmin(abs(pos - Zn))
            x = Xn
            y = Yn
            z = np.zeros((Ny + 1, Nx + 1), float)
            zall = np.zeros((Ny + 1, Nx + 1, 10), float)
            for i in range(Nx + 1):
                for j in range(Ny + 1):
                    zall[j, i] = sol.vedq.calc(
                        i, j, k, Nx, Ny, Nz, Ni, Nj, Nk, N0,
                        Xn, Yn, Zn, RXp, RXm, RYp, RYm, RZp, RZm,
                        idVolt, idEpsr, fEpsr, V, Post['EPS0'])
                    z[j, i] = zall[j, i, icompo]
            xlabel = 'X [m]'
            ylabel = 'Y [m]'
            strplane = 'Z = %g[m]' % pos

        # dBに変換する (V = z[:, :, 0] は除く)
        if Post['p2ddb'] == 1:
            if icompo > 0:
                z = 20 * np.log10(np.maximum(np.abs(z), EPS))
            zall[:, :, 1:] = 20 * np.log10(np.maximum(np.abs(zall[:, :, 1:]), EPS))

        # log
        if Post['p2dlog'] == 1:
            _log_2d(fp, Post, x, y, zall, xlabel, ylabel)

        # Z-limit
        fmin = np.min(z)
        fmax = np.max(z)
        #print(fmin, fmax)
        if fmin == fmax:
            print('*** plot2d : min = max')
            return
        if Post['p2dscale'][0] == 1:
            # 指定スケール
            cmin = Post['p2dscale'][1]
            cmax = Post['p2dscale'][2]
        elif (Post['p2ddb'] == 1) and (icompo > 0):
            # dB幅は自動では40dB(V以外)
            cmin = fmax - 40
            cmax = fmax
        else:
            cmin = fmin
            cmax = fmax
        #print(cmin, cmax)
        # 足切り
        z = np.maximum(cmin, np.minimum(z, cmax))

        # figure
        strfig = 'OpenSTF - %s on %s-plane (%d/%d) - %s' % (compo, cdir, iplane + 1, nplane, datetime.datetime.now().ctime())
        fig = plt.figure(strfig, figsize=(Post['w2d'][0], Post['w2d'][1]))
        ax = fig.add_subplot()

        # plot
        contour = Post['p2dcontour']
        levels = np.linspace(cmin, cmax, Post['p2dscale'][3] + 1)
        cmap = 'rainbow' if (contour == 0 or contour == 1) else 'gray'
        if   (contour == 0) or (contour == 2):
            CS = ax.contourf(x, y, z, levels, cmap=cmap)
        elif (contour == 1) or (contour == 3):
            CS = ax.contour(x, y, z, levels, cmap=cmap)
        fig.colorbar(CS)

        # zoom
        if Post['p2dzoom'][0] == 1:
            ax.set_xlim(Post['p2dzoom'][1], Post['p2dzoom'][2])
            ax.set_ylim(Post['p2dzoom'][3], Post['p2dzoom'][4])
        
        # label
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        # layout
        ax.set_aspect('equal')

        # title
        ax.set_title('%s\n%s%s, %s, max = %.4g%s, min = %.4g%s'
            % (Post['title'], compo, sunit, strplane, fmax, sunit, fmin, sunit))

        # plot geometry lines
        if Post['p2dobject'][0] == 1:
            _geom_lines(ax, gline, mline, cdir, Post['p2dobject'][1:3])

        # show
        plt.show()

# plot geometry lines (private)
def _geom_lines(ax, gline, mline, cdir, ltype):

    for n in range(len(mline)):
        # coordinates
        if   cdir == 'X':
            m1 = 1
            m2 = 2
        elif cdir == 'Y':
            m1 = 0
            m2 = 2
        elif cdir == 'Z':
            m1 = 0
            m2 = 1

        # electrodes
        if (ltype[0] == 1) and (mline[n] < 0):
            ax.plot([gline[n, 0, m1], gline[n, 1, m1]],
                    [gline[n, 0, m2], gline[n, 1, m2]], 'k', lw=1)

        # dielectrics
        if (ltype[1] == 1) and (mline[n] > 0):
            ax.plot([gline[n, 0, m1], gline[n, 1, m1]],
                    [gline[n, 0, m2], gline[n, 1, m2]], 'm', lw=1)

# log (private)
def _log_2d(fp, Post, x, y, z, xlabel, ylabel):

    # header
    fp.write('   No.   No.         %s         %s          V[V]' % (xlabel, ylabel))
    if Post['p2ddb'] == 0:
        fp.write('        E[V/m]       Ex[V/m]       Ey[V/m]       Ez[V/m]      D[C/m^2]     Dx[C/m^2]     Dy[C/m^2]     Dz[C/m^2]      Q[C/m^3]\n')
        fmt = '%14.5e'
    else:
        fp.write('     E[dBV/m]    Ex[dBV/m]    Ey[dBV/m]    Ez[dBV/m]   D[dBC/m^2]  Dx[dBC/m^2]  Dy[dBC/m^2]  Dz[dBC/m^2]   Q[dBC/m^3]\n')
        fmt = '%13.5f'

    # data
    for n1 in range(len(x)):
        for n2 in range(len(y)):
            fp.write('%6d%6d%14.5e%14.5e' % (n1, n2, x[n1], y[n2]))
            fp.write('%14.5e' % z[n2, n1, 0])
            for ic in range(1, 10):
                fp.write(fmt % z[n2, n1, ic])
            fp.write('\n')
