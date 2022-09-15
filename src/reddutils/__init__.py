# @auto-fold regex /^\s*if/ /^\s*else/ /^\s*def/
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# version 1.0.2
# date 15 sept  2022

__all__ = ['correlator', 'exodus', 'fourier', 'owoifier', 'periodogram']

import numpy as np
import os, sys


def fold(x, y, yerr=None, per=None):
    if per == None:
        per = 2. * np.pi
    x_f = x % per
    order = np.argsort(x_f)
    if yerr is None:
        return x_f[order], y[order]
    else:
        return x_f[order], y[order], yerr[order]
    pass


def minmax(x):
    return np.amin(x), np.amax(x)


def flatten(t):
    return [item for sublist in t for item in sublist]


def cps(pers, amps, eccs, starmass):
    #sma, minmass = np.zeros(kplanets), np.zeros(kplanets)
    G = 6.674e-11  # m3 / (kg * s2)
    m2au = 6.685e-12  # au
    kg2sm = 5.03e-31  # solar masses
    s2d = 1.157e-5  # days
    G_ = G * m2au**3 / (kg2sm*s2d)  # au3 / (sm * d2)

    consts = 4*np.pi**2/(G*1.99e30)

    sma = ((pers*24*3600)**2 * starmass / consts)**(1./3) / 1.49598e11
    minmass = amps / ( (28.4329/np.sqrt(1. - eccs**2.)) * (starmass**(-0.5)) * (sma**(-0.5)) )

    return sma, minmass


def hill_check(p, a, e, sm=0.33):
    #kp = len(p)

    sma, minmass = cps(p, a, e, sm)
    o = np.argsort(sma)

    sma, minmass = sma[o], minmass[o]
    p, a, e = p[o], a[o], e[o]

    gamma = np.sqrt(1 - e**2)
    LHS, RHS = [], []
    for k in np.arange(kp):
        mm = np.array([minmass[k], minmass[k+1]])
        M = sm * 1047.56 + np.sum(mm)
        mu = mm / M
        alpha = np.sum(mu)
        delta = np.sqrt(sma[k+1] / sma[k])
        LHS.append(alpha**-3 * (mu[k] + (mu[k+1] / (delta**2))) * (mu[k] * gamma[k] + mu[k+1] * gamma[k+1] * delta)**2)
        RHS.append(1 + (3./alpha)**(4./3) * mu[k] * mu[k+1])

    return LHS, RHS


def delinearize(x, y):
    A = x**2 + y**2
    B = np.arccos(y / (A ** 0.5))
    if x < 0:
        B = 2 * np.pi - B
    return np.array([A, B])


def adelinearize(s, c):
    A = s**2 + c**2
    B = np.arccos(c / (A ** 0.5))
    B[s<0] = 2 * np.pi - B[s<0]

    return np.array([A, B])


def getExtremePoints(data, typeOfExtreme = None, maxPoints = None):
    """
    from https://towardsdatascience.com/modality-tests-and-kernel-density-estimations-3f349bb9e595
    """
    a = np.diff(data)
    asign = np.sign(a)
    signchange = ((np.roll(asign, 1) - asign) != 0).astype(int)
    idx = np.where(signchange == 1)[0]

    if typeOfExtreme == 'max' and data[idx[0]] < data[idx[1]]:
        idx = idx[1:][::2]

    elif typeOfExtreme == 'min' and data[idx[0]] > data[idx[1]]:
        idx = idx[1:][::2]

    elif typeOfExtreme is not None:
        idx = idx[::2]

    # sort ids by min value
    if 0 in idx:
        idx = np.delete(idx, 0)
    if (len(data) - 1) in idx:
        idx = np.delete(idx, len(data)-1)

    idx = idx[np.argsort(data[idx])]
    # If we have maxpoints we want to make sure the timeseries has a cutpoint
    # in each segment, not all on a small interval
    if maxPoints is not None:
        idx = idx[:maxPoints]
        if len(idx) < maxPoints:
            return (np.arange(maxPoints) + 1) * (len(data)//(maxPoints + 1))

    return idx


def plot_extreme(data, n=10):
    import matplotlib.pyplot as pl
    x, y = data

    idx = getExtremePoints(y, typeOfExtreme='max')
    pl.plot(x,y)
    ax = pl.gca()
    pl.scatter(x[idx], y[idx], s=40, c='red')

    for i in idx[:n]:
        ax.annotate(f' Max = {np.round(x[i], 2)}', (x[i], y[i]))
    pl.show()


def ensure_dir(name, loc=''):
    dr = loc+'datalogs/%s/run_1' % name
    while os.path.exists(dr):
        aux = int(dr.split('_')[-1]) + 1
        dr = dr.split('_')[0] + '_' + str(aux)

    os.makedirs(dr)
    os.makedirs(dr+'/histograms')
    os.makedirs(dr+'/posteriors')
    os.makedirs(dr+'/traces')
    return dr


def votable_to_pandas(votable_file):
    votable = parse(votable_file)
    table = votable.get_first_table().to_table(use_names_over_ids=True)
    return table.to_pandas()


def imscatter(x, y, image, ax=None, zoom=1, fmt=None):
    import matplotlib.pyplot as pl
    from matplotlib.offsetbox import OffsetImage, AnnotationBbox
    if ax is None:
        ax = pl.gca()
    try:
        image = pl.imread(image, format=fmt)
    except TypeError:
        # Likely already an array...
        pass
    im = OffsetImage(image, zoom=zoom)
    x, y = np.atleast_1d(x, y)
    artists = []
    for x0, y0 in zip(x, y):
        ab = AnnotationBbox(im, (x0, y0), xycoords='data', frameon=False)
        artists.append(ax.add_artist(ab))
    ax.update_datalim(np.column_stack([x, y]))
    ax.autoscale()
    return artists


def reddplot(plots, fs=(6, 4.5), dpi=100, **kwargs):
    '''
    usage ex.
    things_to_plot = [[x1, y1, 'C0', {'label':'$\hat{\mu_1}$'}],
                     [x2, y2, 'r--', {'label':'Model $\mu_1$'}]
                     ]

    plot_options = {'set_xlabel': ['N samples', {'fontsize':18}],
                    'set_ylabel': ['$\hat{\mu_1}(N)$', {'fontsize':18}],
                    'set_title': ['Means of $\hat{\mu_1}$', {'fontsize':22}]
                    }
    reddplot(things_to_plot, **plot_options)
    '''
    import matplotlib.pyplot as pl
    fig, ax = pl.subplots(figsize=fs, dpi=dpi)

    for x, y, style, opts in plots:
        ax.plot(x, y, style, **opts)
        for k in kwargs:
            getattr(ax, k)(kwargs[k][0], **kwargs[k][1])

    ax.legend()


def reddhist(samples, bins=60, fit=[0, 1], fs=(6, 4.5), dpi=100, **kwargs):
    '''
    usage ex.
    plot_options = {'myfit':[True, 'C2--', {'linewidth':2, 'label':'Model'}],
                    'autofit':[True, 'C3--', {'linewidth':2, 'label':'Auto Fit'}],
                    'set_xlabel': ['$\hat{\mu_1}$', {'fontsize':18}],
                    'set_ylabel': ['Density', {'fontsize':18}],
                    'set_title': ['Histogram for $\hat{\mu_1}(N=%i)$' % (N0), {'fontsize':22}]}
    '''
    import matplotlib.pyplot as pl
    fig, ax = pl.subplots(figsize=fs, dpi=dpi)

    n_, bins_, patches_ = ax.hist(samples, bins=bins, density=True, stacked=True,
                          facecolor='C1', alpha=0.75)

    if kwargs['myfit'][0]:
        my_y = norm.pdf(bins_, fit[0], fit[1])
        ax.plot(bins_, my_y, kwargs['myfit'][1], **kwargs['myfit'][2])

    if kwargs['autofit'][0]:
        auto_mu, auto_sigma = norm.fit(samples)
        auto_y = norm.pdf(bins_, auto_mu, auto_sigma)
        ax.plot(bins_, auto_y, kwargs['autofit'][1], **kwargs['autofit'][2])

    for key in [*kwargs][2:]:
        getattr(ax, key)(kwargs[key][0], **kwargs[key][1])

    ax.legend()


class importer:
	def	__init__(self):
		self.c = 1
	def add_path(self, x):
		sys.path.insert(self.c, x)
		self.c += 1
	def restore_priority(self):
		self.c = 1





#
