# -*- coding: utf-8 -*-
# plotiter.py

import datetime
import matplotlib.pyplot as plt

# plot iteration (2D)
def plot(Post, nRes, fRes, iRes):

    # figure
    strfig = 'OpenSTF - iteration - %s' % datetime.datetime.now().ctime()
    fig = plt.figure(strfig, figsize=(Post['w2d'][0], Post['w2d'][1]))
    ax = fig.add_subplot()

    # plot
    n = nRes
    x = iRes[0: n]
    y = fRes[0: n]
    ax.semilogy(x, y, color='k', marker='o', markersize=3)
    ax.grid(True)

    # X軸
    ax.set_xlabel('iteration')
    ax.set_xlim(x[0], x[-1])

    # Y軸
    ax.set_ylabel('residual')

    # title
    ax.set_title(Post['title'])

    # show
    plt.show()
