# @auto-fold regex /^\s*if/ /^\s*else/ /^\s*def/
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# version 1.0.0
# date 21 aug  2022

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


class importer:
	def	__init__(self):
		self.c = 1
	def add_path(self, x):
		sys.path.insert(self.c, x)
		self.c += 1
	def restore_priority(self):
		self.c = 1





#
