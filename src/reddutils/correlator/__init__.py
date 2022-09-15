# @auto-fold regex /^\s*if/ /^\s*else/ /^\s*def/
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# version 1.0.0
# date 15 sept 2022

# dependencies
import numpy as np
import pandas as pd
from tabulate import tabulate
from scipy.stats import pearsonr
from scipy.stats import spearmanr
from scipy.stats import kendalltau
from scipy.stats import linregress

import matplotlib.pyplot as pl
from matplotlib import ticker
import matplotlib.gridspec as gridspec

from matplotlib.colors import Normalize as cnorm
import matplotlib.cm as cm


import ipywidgets
from ipywidgets import interactive, interact, HBox, VBox

from IPython.display import display

# body

class correlator:
    def __init__(self, data=None, headers=None):
        # STYLES
        self.style_list = ['default', 'classic'] + sorted(
                        style for style in pl.style.available
                        if style != 'classic' and
                        style != 'fast' and not style.startswith('_'))

        #self.xx, self.yy = D[x_axis].values, D[y_axis].values
        #self.colors = self.data[self.xinit].values

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

        self.out = ipywidgets.Output()
        self.out_text = ipywidgets.Output()
        pass

    def plot(self):
        # define values from buttons
        self.x = self.data[self.xaxis.value].values
        self.y = self.data[self.yaxis.value].values
        self.yerr = self.data[self.yerraxis.value].values
        colors = self.data[self.color_by.value].values


        scatter_size = self.scatter_size.value
        ##############
        # TAB 2
        TITLE = self.title_textbox.value
        cm_nam = pl.cm.get_cmap(self.cmap_drop.value)

        xlog = self.xlog_button.value
        ylog = self.ylog_button.value

        pl.style.use(self.style_drop.value)




        ##############
        #PLOT

        #self.fig, ax = pl.subplots(figsize=(self.hsize_slider.value, self.vsize_slider.value), dpi=80)
        self.fig, ax = pl.subplots(figsize=(self.hsize_slider.value, self.vsize_slider.value), dpi=80)

        if self.grid_checkbox.value:
            ax.grid()


        if not self.yerr_checkbox.value:
            sc = ax.scatter(self.x, self.y, c=colors,
                            marker=self.marker_styles[self.scatter_marker.value],
                            cmap=cm_nam, lw=self.scatter_lw.value, ec='k',
                            s=scatter_size, alpha=self.scatter_alpha.value)

            pl.colorbar(sc)
        if self.yerr_checkbox.value:
            #sc = ax.errorbar(self.x, self.y, yerr=self.yerr)#,
                                #ecolor=cm,
                                #marker=self.marker_styles[self.scatter_marker.value],
                                #lw=self.scatter_lw.value, ec='k',
                                #s=scatter_size, alpha=self.scatter_alpha.value)

            norm = cnorm(vmin=min(colors), vmax=max(colors), clip=True)
            mapper = cm.ScalarMappable(norm=norm, cmap=cm_nam)
            my_color = np.array([(mapper.to_rgba(v)) for v in colors])

            #for x, y, e, color in zip(self.x, self.y, self.yerr, my_color):
            for x, y, e, color in zip(self.x, self.y, self.yerr, my_color):
                ax.scatter(x, y, color=color,
                            marker=self.marker_styles[self.scatter_marker.value],
                            lw=self.scatter_lw.value, ec='k',
                            s=scatter_size, alpha=self.scatter_alpha.value)

                ax.errorbar(x, y, e, lw=3, capsize=8, color=color)

            sc = ax.scatter(self.x, self.y, s=0, c=colors, cmap=cm_nam)
            pl.colorbar(sc)
            pass

        # model
        slope, intercept, r, p, stderr = linregress(self.x, self.y)
        line = f'Regression line: y={intercept:.2f}+{slope:.2f}x, r={r:.2f}'
        ax.plot(self.x, intercept + slope * self.x,
                ls=self.line_styles[self.line_style.value], c=self.line_color.value,
                lw=self.line_width.value, alpha=self.line_alpha.value)
        #print('slope, intercept, r, p, stderr')

        if xlog:
            ax.set_xscale('log')
        if ylog:
            ax.set_yscale('log')

        ax.set_title(TITLE, fontsize=self.title_fontsize.value)
        ax.set_xlabel(self.xaxis.value, fontsize=self.xaxis_fontsize.value)
        ax.set_ylabel(self.yaxis.value, fontsize=self.yaxis_fontsize.value)

        if xlog:
            ax.set_xscale('log')
        if ylog:
            ax.set_yscale('log')

        pl.minorticks_on()

        #ax = fig.add_axes([0, 0, 1, 1])

        ax.xaxis.set_tick_params(which='major', size=10, width=2, direction='in', top='on')
        ax.xaxis.set_tick_params(which='minor', size=7, width=2, direction='in', top='on')
        ax.yaxis.set_tick_params(which='major', size=10, width=2, direction='in', right='on')
        ax.yaxis.set_tick_params(which='minor', size=7, width=2, direction='in', right='on')


        pass

    def calc_stats(self):
        # STATS
        funcs = [pearsonr, spearmanr, kendalltau]
        names = ['Pearson', 'Spearman', 'Kendall']
        taball = []
        tab_header = ['Correlation', 'Rank', 'p-value', 'Info']
        try:
            for i in range(3):
                coefx, px = funcs[i](self.x, self.y)
                if px > self.sensitivity.value:
                    text = 'Uncorrelated (fail to reject H0) p=%.5f' % px
                else:
                    text = 'Correlated (reject H0) p=%.5f' % px
                taball.append([names[i], coefx, px, text])

            #print(tabulate(taball, headers=tab_header))
        except:
            print('Cant calculate coeficients, figure it out man')
        return tabulate(taball, headers=tab_header)

    def set_data(self, data=None):
        if type(data) == np.ndarray:
            if headers:
                try:
                    self.headers = headers
                    self.data = pd.DataFrame(data, columns=headers)
                except:
                    print('Headers are invalid for data.type ndarray')
                    self.data = pd.DataFrame(data, columns = ['Time','RV','RVe'])
        if type(data) == pd.DataFrame:
            self.data = data

        self.keys = self.data.columns
        self.xinit = self.keys[0]
        self.yinit = self.keys[1]

    def set_buttons(self):
        self.xaxis = ipywidgets.Dropdown(options=self.keys,
                value=self.xinit, description='x-axis:')
        self.yaxis = ipywidgets.Dropdown(options=self.keys,
                value=self.yinit, description='y-axis:')
        self.yerraxis = ipywidgets.Dropdown(options=self.keys,
                value=self.yinit, description='yerr-axis:', disabled=False)


        self.sensitivity = ipywidgets.FloatSlider(value=0.05,
            min=0, max=1, step=0.01,
            description='Sensitivity: ', readout_format='.2f')
        self.color_by = ipywidgets.Dropdown(options=self.keys,
                value=self.xinit, description='Color by:')

        self.yerr_checkbox = ipywidgets.Checkbox(
                    value=False, description='Add yerr')



        # TAB 2
        if True:
            # general
            self.title_textbox = ipywidgets.Text(
                value=self.xaxis.value,
                description='Title: ')

            self.title_fontsize = ipywidgets.FloatText(value=28,
                description='Title Fontsize: ',disabled=False)

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

            # Axis
            self.xaxis_label = ipywidgets.Text(
                value=self.xaxis.value,
                description='x-axis label: ')

            self.yaxis_label = ipywidgets.Text(value=self.yaxis.value,
                description='y-axis label: ')

            self.xaxis_fontsize = ipywidgets.FloatText(value=22,
                description='x-label fontsize: ')

            self.yaxis_fontsize = ipywidgets.FloatText(value=22,
                description='y-label fontsize: ')


            self.xlog_button = ipywidgets.Checkbox(
                        value=False, description='x log',
                        disabled=False)

            self.ylog_button = ipywidgets.Checkbox(
                    value=False, description='y log')

            # markers

            self.scatter_alpha = ipywidgets.FloatSlider(
                value=1., min=0., max=1., step=0.01,
                description='Transparency:', readout_format='.2f')

            self.scatter_marker = ipywidgets.Dropdown(options=self.marker_keys,
                    value=self.marker_keys[0], description='Shape: ')

            self.scatter_bc = ipywidgets.ColorPicker(
                concise=True,
                description='Border color: ',
                value='#000000')

            self.scatter_lw = ipywidgets.FloatSlider(
                value=0.2, min=0., max=1, step=0.1,
                description='Border width:', readout_format='.2f')

            self.scatter_size = ipywidgets.IntSlider(
                        value=100, min=1, max=200,
                        description='Size: ')

            self.cmap_drop = ipywidgets.Dropdown(
                options=pl.colormaps(),
                value='winter',
                description='Colormap:',
                disabled=False)

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

        ######
        self.button = ipywidgets.Button(description='Refresh')
        @self.button.on_click
        def plot_on_click(b):
            self.out.clear_output(wait=True)
            self.out_text.clear_output(wait=True)
            with self.out:
                self.plot()
                pl.show()
            with self.out_text:
                print(self.calc_stats())
        ######
        # TAB 4
        if True:
            self.plot_fmt = ipywidgets.RadioButtons(options=['png', 'pdf', 'svg'],
                            value='pdf', description='Plot format:', disabled=False)

            self.savefile_name = ipywidgets.Text(
                value='current_plot',
                description='File Name')

            self.plot_save_button = ipywidgets.Button(
                    description='Save plot')
            @self.plot_save_button.on_click
            def save_plot_on_click(b):
                self.fig.savefig(self.savefile_name.value, format=self.plot_fmt.value)


        pass

    def set_tabs(self):
        tab1_row1 = [self.xaxis, self.yaxis, self.yerraxis]
        tab1_row2 = [self.sensitivity, self.color_by, self.yerr_checkbox]

        tab1_ = [tab1_row1, tab1_row2]

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
        tab2_acc3_row1 = [self.scatter_marker, self.scatter_bc, self.scatter_lw]
        tab2_acc3_row2 = [self.scatter_size, self.scatter_alpha]
        tab2_acc3 = [tab2_acc3_row1, tab2_acc3_row2]
        # line
        tab2_acc4_row1 = [self.line_style, self.line_color]
        tab2_acc4_row2 = [self.line_width, self.line_alpha]
        tab2_acc4_row3 = [self.cmap_drop]
        tab2_acc4 = [tab2_acc4_row1, tab2_acc4_row2, tab2_acc4_row3]

        tab2_acc = [tab2_acc1, tab2_acc2, tab2_acc3, tab2_acc4]
        acc_titles = ['General', 'Axis', 'Markers', 'Line']

        accordion = ipywidgets.Accordion(children=[VBox(children=[HBox(children=[wid for wid in row]) for row in rows]) for rows in tab2_acc])

        for i in range(len(acc_titles)):
            accordion.set_title(i, acc_titles[i])


        tab4_row1 = [self.savefile_name, self.plot_fmt]
        tab4_row2 = [self.plot_save_button]
        tab4_ = [tab4_row1, tab4_row2]

        tab1 = VBox(children=[HBox(children=row) for row in tab1_])
        tab2 = accordion
        tab4 = VBox(children=[HBox(children=row) for row in tab4_])

        tab_names = ['Plot', 'Styling', 'Export']

        self.tab = ipywidgets.Tab(children=[tab1, tab2, tab4])

        for i in range(len(tab_names)):
            self.tab.set_title(i, tab_names[i])
        pass

    def setup(self):
        self.set_buttons()
        self.set_tabs()
        pass

    def display(self, data=None):
        self.set_data(data)
        self.setup()
        return VBox(children=[self.tab, self.button, self.out, self.out_text])
    pass






























#
