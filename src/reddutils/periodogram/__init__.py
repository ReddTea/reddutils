# @auto-fold regex /^\s*if/ /^\s*else/ /^\s*def/
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# version 0.0.1
# date 18 aug 2022

# dependencies
import numpy as np
import pandas as pd
from scipy.signal import lombscargle, get_window
from astropy.timeseries import LombScargle as lomb_scargle

from gatspy.periodic import LombScargle
from gatspy.periodic import LombScargleFast
import matplotlib.pyplot as pl
from tabulate import tabulate

import ipywidgets
from ipywidgets import interactive, interact, HBox, VBox

from IPython.display import display

# body

method_dict = {'Scipy':0, 'AstroML':1, 'Gatspy LS':2, 'Gatspy LSF':3}

class LSP:
    def __init__(self):


        # STYLES
        self.style_list = ['default', 'classic'] + sorted(
                        style for style in pl.style.available
                        if style != 'classic' and
                        style != 'fast' and not style.startswith('_'))

        self.marker_styles = {'Circle':'o',
                              'Triangle Down':'v',
                              'Triangle Up':'^',
                              'Square':'s',
                              'Pentagon':'p',
                              'Hexagon':'h',
                              'Octagon':'8',
                              'Star':'*',
                              'Diamond':'D',
                              'Plus':'P',
                              'X':'X'}

        self.marker_keys = [*self.marker_styles]

        self.line_styles = {'Solid': '-',
                            'Dashed': '--',
                            'Dash-dotted': '-.',
                            'Dotted':':'}

        self.line_keys = [*self.line_styles]

        self.cn_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']


        ##############
        #self.t = np.ascontiguousarray(x)
        #self.mag = np.ascontiguousarray(y)
        #self.dmag = np.ascontiguousarray(yerr)

        self.tab_header = ['Rank', 'Period', 'Power']
        ###
        self.out = ipywidgets.Output()
        self.out_text = ipywidgets.Output()
        pass


    def getExtremePoints(self, data, typeOfExtreme = None):
        #data = np.array([self.t, self.mag])
        mp = self.maxpoints_textbox.value

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

        if 0 in idx:
            idx = np.delete(idx, 0)
        if (len(data) - 1) in idx:
            idx = np.delete(idx, len(data)-1)

        idx = idx[np.argsort(data[idx])]
        if mp is not None:
            idx = idx[-mp:]
            if len(idx) < mp:
                return (np.arange(mp) + 1) * (len(data)//(mp + 1))
        return idx


    def deploy_lsp(self):
        pl.close('all')
        # data
        x = self.xinit
        y = self.yaxis.value
        yerr = self.rinit

        # other params
        Nfreq = self.nfreq.value
        min_per = self.permin.value
        max_per = self.permax.value
        periods = np.linspace(min_per, max_per, Nfreq)
        ang_freqs = 2 * np.pi / periods

        # mark how many
        maxpoints = self.maxpoints_textbox.value
        ide = np.arange(maxpoints)+1

        method = method_dict[self.method_drop.value]
        # PLOT
        XAXIS_LABEL = self.xaxis_label.value
        YAXIS_LABEL = self.yaxis_label.value
        TITLE = self.title_textbox.value

        xlog = self.xlog_button.value
        ylog = self.ylog_button.value

        pl.style.use(self.style_drop.value)
        #######################################################
        t = self.data[x].values
        mag = self.data[y].values
        dmag = self.data[yerr].values

        t = np.ascontiguousarray(t)
        mag = np.ascontiguousarray(mag)
        dmag = np.ascontiguousarray(dmag)

        for i in range(1):
            if method==0:
                power = lombscargle(t, mag - np.mean(mag), ang_freqs)
                N = len(t)
                power *= 2 / (N * np.std(mag) ** 2)
                periods = periods

            if method==1:
                periods = periods
                power = lomb_scargle(t, mag, dmag).power(ang_freqs)

            if method==2:
                periods = periods
                model = LombScargle(fit_offset=True).fit(t, mag, dmag)
                power = model.score(periods)

            if method==3:
                fmin = 1. / periods.max()
                fmax = 1. / periods.min()
                N = Nfreq
                df = (fmax - fmin) / Nfreq

                model = LombScargleFast().fit(t, mag, dmag)
                periods, power = model.periodogram_auto(nyquist_factor=200)

                freqs = fmin + df * np.arange(N)

        #pl.savefig('periodogram.png')
        self.fig, ax = pl.subplots(figsize=(self.hsize_slider.value, self.vsize_slider.value), dpi=80)
        pl.title(TITLE, fontsize=self.title_fontsize.value)

        idx = self.getExtremePoints(power, typeOfExtreme='max')
        #idx = idx[-2:]

        pl.plot(periods, power, ls=self.line_styles[self.line_style.value],
                c=self.line_color.value)
        # fap line
        ax.annotate('0.1% significance level', (3, 0.13))
        pl.plot(periods, np.ones_like(periods)*0.12, 'k--')
        pl.scatter(periods[idx], power[idx],
                    marker=self.marker_styles[self.scatter_marker.value],
                    s=self.scatter_size.value, c=self.scatter_color.value,
                    alpha=self.scatter_alpha.value)

        for i in idx:
            ax.annotate(f' Max = {np.round(periods[i], 2)}', (periods[i]+10, power[i]))

        ax.set_title(TITLE, fontsize=self.title_fontsize.value)
        ax.set_xlabel(XAXIS_LABEL, fontsize=self.xaxis_fontsize.value)
        ax.set_ylabel(YAXIS_LABEL, fontsize=self.yaxis_fontsize.value)

        if xlog:
            ax.set_xscale('log')
        if ylog:
            ax.set_yscale('log')

        tabable = np.array([periods[idx][::-1], power[idx][::-1]])


        taball = np.vstack([ide, tabable])
        self.display_text = tabulate(taball.T, headers=self.tab_header)

        #return taball.T
        pass


    def set_data(self, data=None, headers=None):
        if type(data) == np.ndarray:
            self.data = pd.DataFrame(data, columns = headers)
            self.headers=headers
        if type(data) == pd.DataFrame:
            self.data = data
            self.headers = self.data.columns

        self.keys = self.data.columns

        self.xinit = 'Time'
        self.yinit = 'RV'
        self.rinit = 'RVe'


    def set_buttons(self):
        # TAB 1
        if True:
            self.upload_file = ipywidgets.FileUpload(
                        accept='',  # Accepted file extension e.g. '.txt', '.pdf', 'image/*', 'image/*,.pdf'
                        multiple=False  # True to accept multiple files upload else False
                        )

            self.yaxis = ipywidgets.Dropdown(options=self.keys,
                    value=self.yinit, description='Column:',
                    disabled=False)

            self.maxpoints_textbox = ipywidgets.IntText(value=3, description='Maxpoints', disabled=False)


            self.button = ipywidgets.Button(description='Refresh')

            self.nfreq = ipywidgets.IntText(value=10000, description='Frequencies',disabled=False)

            self.permin = ipywidgets.FloatText(value=1, description='Period min.:',disabled=False)
            self.permax = ipywidgets.FloatText(value=10000, description='Period max.:',disabled=False)

        #TAB 3
        self.method_drop = ipywidgets.Dropdown(options=method_dict.keys(),
                value='Scipy', description='Method:')
        ##############################

        # TAB 2
        if True:
            # general

            self.title_textbox = ipywidgets.Text(
                value=self.method_drop.value,
                description='Title: ')

            self.title_fontsize = ipywidgets.FloatText(value=16,
                description='Title Fontsize: ',disabled=False)
                # figsize option
            self.hsize_slider = ipywidgets.IntSlider(
                value=8, min=2, max=20,
                description='Plot hsize:')

            self.vsize_slider = ipywidgets.IntSlider(
                value=4, min=2, max=20,
                description='Plot vsize:')

            self.style_drop = ipywidgets.Dropdown(
                options=self.style_list,
                value=self.style_list[0],
                description='Plot Style:')

            self.grid_checkbox = ipywidgets.Checkbox(
                        value=False, description='Grid')

            # axis
            self.xaxis_label = ipywidgets.Text(
                value='Period (days)',
                description='x-axis label: ')

            self.yaxis_label = ipywidgets.Text(
                value='Lomb-Scargle Power',
                description='y-axis label: ')

            self.xaxis_fontsize = ipywidgets.FloatText(value=22,
                description='x-label fontsize: ')

            self.yaxis_fontsize = ipywidgets.FloatText(value=22,
                description='y-label fontsize: ')


            self.xlog_button = ipywidgets.Checkbox(
                        value=True, description='x log')

            self.ylog_button = ipywidgets.Checkbox(
                    value=False, description='y log')

            # markers
            self.scatter_marker = ipywidgets.Dropdown(options=self.marker_keys,
                    value=self.marker_keys[0], description='Shape: ')

            self.scatter_color = ipywidgets.ColorPicker(
                concise=True,
                description='Color: ',
                value='#FF0000')

            self.scatter_size = ipywidgets.IntSlider(
                        value=40, min=1, max=100,
                        description='Size: ')

            self.scatter_alpha = ipywidgets.FloatSlider(
                value=1., min=0., max=1., step=0.01,
                description='Transparency:', readout_format='.2f')

            # line
            self.line_style = ipywidgets.Dropdown(options=self.line_keys,
                    value=self.line_keys[0], description='Style: ')

            self.line_color = ipywidgets.ColorPicker(
                concise=True,
                description='Color: ',
                value='#000000')

            self.line_width = ipywidgets.FloatSlider(
                        value=2, min=1, max=5,
                        description='Width: ')

            self.line_alpha = ipywidgets.FloatSlider(
                value=1., min=0., max=1., step=0.01,
                description='Transparency:', readout_format='.2f')

        ##############################

        #TAB 4
        if True:
            self.plot_save_button = ipywidgets.Button(
                    description='Save plot')

            self.plot_fmt = ipywidgets.RadioButtons(options=['png', 'pdf', 'svg'],
                                value='pdf', description='Plot format:', disabled=False)

            self.savefile_name = ipywidgets.Text(
                    value='current_plot',
                    description='File Name')
        pass


    def set_methods(self):
        @self.button.on_click
        def plot_on_click(b):
            self.out.clear_output(wait=True)
            self.out_text.clear_output(wait=True)
            with self.out:
                self.deploy_lsp()
                pl.show()
            with self.out_text:
                print(self.display_text)

        @self.plot_save_button.on_click
        def save_plot_on_click(b):
            pl.tight_layout()
            self.fig.savefig(self.savefile_name.value+'.'+self.plot_fmt.value, bbox_inches='tight')


        def on_value_change(change):
            with open('input.temp', 'w+b') as file:
                file.write(self.upload_file.data[0])
            try:
                data = np.loadtxt('input.temp')
                temp_headers = self.headers
                temp_data = pd.DataFrame(data, columns=temp_headers)
            except ValueError:
                temp_data = pd.read_csv('input.temp')
                temp_headers = temp_data.columns
            except:
                print('FAILED TO UNPACK THE FILE. SORRY :(')
            self.set_data(data=temp_data, headers=temp_headers)

        self.upload_file.observe(on_value_change, names='value')


    def set_tabs(self):
        t1r0 = [self.upload_file]
        t1r1 = [self.yaxis, self.maxpoints_textbox]
        t1r2 = [self.nfreq, self.permin, self.permax]

        tab1_ = [t1r0, t1r1, t1r2]

        # general
        tab2_acc1_row1 = [self.title_textbox, self.title_fontsize]
        tab2_acc1_row2 = [self.hsize_slider, self.vsize_slider]
        tab2_acc1_row3 = [self.style_drop, self.grid_checkbox]
        tab2_acc1 = [tab2_acc1_row1, tab2_acc1_row2, tab2_acc1_row3]

        # axis
        tab2_acc2_row1 = [self.xaxis_label, self.xaxis_fontsize, self.xlog_button]
        tab2_acc2_row2 = [self.yaxis_label, self.yaxis_fontsize, self.ylog_button]
        tab2_acc2 = [tab2_acc2_row1, tab2_acc2_row2]

        # markers
        tab2_acc3_row1 = [self.scatter_marker, self.scatter_color, self.scatter_size]
        tab2_acc3_row2 = [self.scatter_alpha]
        tab2_acc3 = [tab2_acc3_row1, tab2_acc3_row2]
        # line
        tab2_acc4_row1 = [self.line_style, self.line_color]
        tab2_acc4_row2 = [self.line_width, self.line_alpha]
        tab2_acc4 = [tab2_acc4_row1, tab2_acc4_row2]

        tab2_acc = [tab2_acc1, tab2_acc2, tab2_acc3, tab2_acc4]
        acc_titles = ['General', 'Axis', 'Markers', 'Line']

        accordion = ipywidgets.Accordion(children=[VBox(children=[HBox(children=[wid for wid in row]) for row in rows]) for rows in tab2_acc])

        for i in range(len(acc_titles)):
            accordion.set_title(i, acc_titles[i])

        t3r1 = [self.method_drop]
        tab3_ = [t3r1]

        t4_row1 = [self.savefile_name, self.plot_fmt]
        t4_row2 = [self.plot_save_button]
        tab4_ = [t4_row1, t4_row2]


        tab1 = VBox(children=[HBox(children=row) for row in tab1_])
        tab2 = accordion
        tab3 = VBox(children=[HBox(children=row) for row in tab3_])
        tab4 = VBox(children=[HBox(children=row) for row in tab4_])

        tab_names = ['Plot', 'Styling', 'Method', 'Export']

        self.tab = ipywidgets.Tab(children=[tab1, tab2, tab3, tab4])

        for i in range(len(tab_names)):
            self.tab.set_title(i, tab_names[i])
        pass


    def setup(self):
        self.set_buttons()
        self.set_methods()
        self.set_tabs()
        pass


    def display(self, data=None, headers=['Time', 'RV', 'RVe']):
        self.set_data(data=data, headers=headers)
        self.setup()
        return VBox(children=[self.tab, self.button, HBox(children=[self.out, self.out_text])])















#
