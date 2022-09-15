# @auto-fold regex /^\s*if/ /^\s*else/ /^\s*def/
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# version 1.0.0
# date 15 sept 2022

import numpy as np
import pandas as pd
from PyAstronomy import pyasl
from tabulate import tabulate
import os

import matplotlib.pyplot as pl
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

import ipywidgets
from ipywidgets import HBox, VBox

from IPython.display import display

from reddutils import imscatter
# TABLES
reads = ['Planet Name', 'Host Name', 'Number of Stars', 'Number of Planets',
         'Discovery Method', 'Discovery Year', 'Controversial Flag', 'Orbital Period [days]', 'Orbit Semi-Major Axis [au])',
         'Planet Radius [Earth Radius]', 'Planet Radius [Jupiter Radius]', 'Planet Mass or Mass*sin(i) [Earth Mass]',
         'Planet Mass or Mass*sin(i) [Jupiter Mass]', 'Planet Mass or Mass*sin(i) Provenance', 'Eccentricity', 'Insolation Flux [Earth Flux]',
         'Equilibrium Temperature [K]', 'Data show Transit Timing Variations', 'Spectral Type', 'Stellar Effective Temperature [K]',
         'Stellar Radius [Solar Radius]', 'Stellar Mass [Solar mass]', 'Stellar Metallicity [dex]', 'Stellar Metallicity Ratio',
         'Stellar Surface Gravity [log10(cm/s**2)]','RA [sexagesimal]','RA [deg]','Dec [sexagesimal]','Dec [deg]',
         'Distance [pc]', 'V (Johnson) Magnitude', 'Ks (2MASS) Magnitude', 'Gaia Magnitude']



good_cols = [2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 19, 20, 21, 22,
            24, 26, 28, 29, 30, 31, 32]

planet_names = ['mercury.png', 'venus.png', 'earth.png', 'mars.png',
                'jupiter.png', 'saturn.png', 'uranus.png', 'neptune.png']

#planet_sizes = [0.025, 0.035, 0.03, 0.03, 0.03, 0.03, 0.025, 0.04]


_ROOT = os.path.dirname(__file__)

def get_data(path):
    return os.path.join(_ROOT, 'data', path)

dataloc = get_data('tables/exo_list.csv')
imageloc = get_data('images/')




class Exoplanet_Archive:
    def __init__(self, data=None):
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

        self.marker_presets = {}

        self.line_styles = {'Solid': '-',
                            'Dashed': '--',
                            'Dash-dotted': '-.',
                            'Dotted':':'}

        self.line_keys = [*self.line_styles]

        self.cn_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        self.include_ss = False

        self.legend_title = 'Planet Discovery Method'

        self.switch_method = True
        self.method_key = 'discoverymethod'
        self.data = data

        if self.data == 'ExoplanetEU2':
            self.method_key = 'detection_type'

        if self.data == 'ExoplanetsOrg':
            self.method_key = 'pl_dtype'

        if self.data == 'NasaExoplanetArchive':
            self.switch_method = False

        # SET OUT
        self.out = ipywidgets.Output()
        self.out_h = ipywidgets.Output()

    def plot(self, b=None):
        pl.close('all')
        x_axis, y_axis = [b.value for b in [self.xaxis, self.yaxis]]
        TITLE = self.title_textbox.value

        minmask_x, maxmask_x = self.xlim1_textbox.value, self.xlim2_textbox.value
        minmask_y, maxmask_y = self.ylim1_textbox.value, self.ylim2_textbox.value

        pl.style.use(self.style_drop.value)



        ###############
        key1 = self.unreadable[x_axis]
        key2 = self.unreadable[y_axis]

        x, y = self.d[key1], self.d[key2]

        self.fig, ax = pl.subplots(figsize=(self.hsize_slider.value, self.vsize_slider.value), dpi=80)
        if self.grid_checkbox.value:
            ax.grid()

        if self.xlog_button.value:
            ax.set_xscale('log')
        if self.ylog_button.value:
            ax.set_yscale('log')

        Ndat = x.size

        if True:
            lims_mask = (minmask_x<x)&(x<maxmask_x)&(minmask_y<y)&(y<maxmask_y)
            data = self.d[lims_mask]

            x0, y0 = data[key1], data[key2]
            Ndat = x0.size


        if self.methodbutton.value:
            Ndat = 0
            for m in self.methods:
                if self.method_dict[m].value:
                    mask = data[self.method_key] == m
                    xx = x0[mask]
                    yy = y0[mask]

                    ax.scatter(xx, yy, label=m, **self.marker_presets[m])

                    Ndat += xx.size
                else:
                    pass
        else:
            ax.scatter(x0, y0, label='Planets', **self.marker_presets['unique'])
            pass


        if self.include_ss:
            #try:
            xs = self.ss[key1]
            ys = self.ss[key2]
            for p in range(len(xs)):
                imscatter(xs[p], ys[p], imageloc+'%s' % planet_names[p], ax=ax)
            #except:
            #    pass


        # AXIS
        ax.xaxis.set_tick_params(which='major', size=10, width=2, direction='in', top='on')
        ax.xaxis.set_tick_params(which='minor', size=7, width=2, direction='in', top='on')
        ax.yaxis.set_tick_params(which='major', size=10, width=2, direction='in', right='on')
        ax.yaxis.set_tick_params(which='minor', size=7, width=2, direction='in', right='on')

        ax.set_xlabel(self.readable[x.name], fontsize=self.xaxis_fontsize.value)
        ax.set_ylabel(self.readable[y.name], fontsize=self.yaxis_fontsize.value)

        # TITLE
        ax.set_title(TITLE+' N = %i' % Ndat, fontsize=self.title_fontsize.value)


        # LEGEND
        if self.switch_method:
            TFP = {'style':'italic', 'size':'large', 'weight':'semibold'}
            pl.legend(title=self.legend_title, title_fontproperties=TFP)

    def plot_h(self, b=None):
        pl.close('all')
        x_axis = self.xaxis.value

        #by_method, alpha = [b.value for b in [self.methodbutton, self.alpha_slider]]

        TITLE = self.title_textbox.value

        NORM = self.norm_h.value
        bins = self.bins_textbox.value

        minmask_x, maxmask_x = self.xlim1_textbox.value, self.xlim2_textbox.value

        pl.style.use(self.style_drop.value)
        #########################################################

        key1 = self.unreadable[x_axis]
        x = self.d[key1]

        self.fig, ax = pl.subplots(figsize=(self.hsize_slider.value, self.vsize_slider.value), dpi=80)

        if self.grid_checkbox.value:
            ax.grid()



        if True:
            lims_mask = (minmask_x<x)&(x<maxmask_x)
            data = self.d[lims_mask]
            x0 = data[key1]

        if self.methodbutton.value:
            xm = np.array([])
            for m in self.methods:
                if self.method_dict[m].value:
                    mask = data[self.method_key] == m
                    xm = np.append(xm, x0[mask].values)


        else:
            xm = x0.values

        Ndat = len(xm)

        if self.xlogh_button.value:
            ax.set_xscale('log')
            histl, binsl = np.histogram(xm, bins=bins)
            bins = np.logspace(np.log10(binsl[0]),np.log10(binsl[-1]),len(binsl))
            pass

        if self.ylogh_button.value:
            ax.set_yscale('log')

        n, bins, patches = pl.hist(xm, bins, density=NORM, stacked=NORM,
                                    facecolor=self.bins_fc.value, alpha=self.bins_alpha.value,
                                    edgecolor=self.bins_ec.value)


        ax.set_xlabel(self.readable[x.name], fontsize=22)
        if NORM:
            ax.set_ylabel('frequency', fontsize=22)
        else:
            ax.set_ylabel('counts', fontsize=22)

        # TITLE
        ax.set_title(TITLE+' N = %i' % Ndat, fontsize=28)

        pass

    def set_buttons(self):
        if True:
            # axis
            self.xaxis = ipywidgets.Dropdown(options=self.unkeys,
                value=self.unkeys[self.xinit], description='x-axis:',
                disabled=False)


            self.yaxis = ipywidgets.Dropdown(options=self.unkeys,
                value=self.unkeys[self.yinit], description='y-axis:',
                disabled=False)

            self.xlim1_textbox = ipywidgets.FloatText(value=np.amin(self.d[self.unreadable[self.xaxis.value]]), description='x Minimum:',disabled=False)
            self.xlim2_textbox = ipywidgets.FloatText(value=np.max(self.d[self.unreadable[self.xaxis.value]]), description='x Maximum:',disabled=False)

            self.ylim1_textbox = ipywidgets.FloatText(value=np.min(self.d[self.unreadable[self.yaxis.value]]), description='y Minimum:',disabled=False)
            self.ylim2_textbox = ipywidgets.FloatText(value=np.max(self.d[self.unreadable[self.yaxis.value]]), description='y Maximum:',disabled=False)

            self.xlims_restore = ipywidgets.Button(description='Reset x range')
            self.ylims_restore = ipywidgets.Button(description='Reset y range')


            self.xlog_button = ipywidgets.Checkbox(
                value=True, description='x log')

            self.ylog_button = ipywidgets.Checkbox(
                value=True, description='y log')

            self.axis_restore =  ipywidgets.Button(description='Reset axis')
            self.axis_invert =  ipywidgets.Button(description='Invert axis')



            self.ss_add_box = ipywidgets.Button(description='Add SS')

            self.ss_add_box.style.button_color = 'mediumpurple'

            # axis limits

        if True:
            # TAB 2
            # general
            self.title_textbox = ipywidgets.Text(
                value='Exoplanet Population',
                description='Title: ')

            self.title_fontsize = ipywidgets.FloatText(value=28,
                description='Title Fontsize: ',disabled=False)

            self.hsize_slider = ipywidgets.IntSlider(
                value=9, min=2, max=20,
                description='Plot hsize:')

            self.vsize_slider = ipywidgets.IntSlider(
                value=6, min=2, max=20,
                description='Plot vsize:')

            self.style_drop = ipywidgets.Dropdown(
                options=self.style_list,
                value=self.style_list[0],
                description='Plot Style: ')

            self.grid_checkbox = ipywidgets.Checkbox(
                        value=False, description='Grid')

            # axis
            self.xaxis_label = ipywidgets.Text(
                value=self.xaxis.value,
                description='x-axis label: ')

            self.yaxis_label = ipywidgets.Text(value=self.yaxis.value,
                description='y-axis label: ')

            self.xaxis_fontsize = ipywidgets.FloatText(value=22,
                description='x-label fontsize: ')

            self.yaxis_fontsize = ipywidgets.FloatText(value=22,
                description='y-label fontsize: ')

            # markers
            self.scatter_applyto = ipywidgets.Dropdown(options=np.append('All', self.methods),
                    value='All', description='Apply to: ')

            self.scatter_marker = ipywidgets.Dropdown(options=self.marker_keys,
                    value=self.marker_keys[0], description='Shape: ')
            self.scatter_size = ipywidgets.IntSlider(
                        value=100, min=1, max=200,
                        description='Size: ')
            self.scatter_alpha = ipywidgets.FloatSlider(
                value=1., min=0., max=1., step=0.01,
                description='Transparency:', readout_format='.2f')

            self.scatter_fc = ipywidgets.ColorPicker(
                concise=False,
                description='Face color: ',
                value='#000000')
            self.scatter_ec = ipywidgets.ColorPicker(
                concise=False,
                description='Edge color: ',
                value='#000000')
            self.scatter_ew = ipywidgets.FloatSlider(
                value=1.5, min=0., max=3, step=0.1,
                description='Edge width:', readout_format='.2f')


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

        if True:
            # TAB 4
            self.plot_fmt = ipywidgets.RadioButtons(options=['png', 'pdf', 'svg'],
                            value='pdf', description='Plot format:', disabled=False)

            self.savefile_name = ipywidgets.Text(
                value='current_plot',
                description='File Name')


            self.button = ipywidgets.Button(
                description='Refresh')
            self.plot_save_button = ipywidgets.Button(
                description='Save plot')

        if True:
            # methods
            self.methodbutton = ipywidgets.ToggleButton(
                value=self.switch_method, description='By Method',
                icon='check')


            self.method_dict = {}
            for m in self.methods:
                self.method_dict[m] = ipywidgets.ToggleButton(value=self.fav_met[m], description=m, icon='check')
                self.marker_presets[m] = {'marker':self.marker_styles['Circle'], 's':None, 'alpha':0.9,
                                                        'facecolors':'none',
                                                        'edgecolors':self.method_colors[m],
                                                        'linewidths':1.5}

            self.method_restore = ipywidgets.Button(description='Reset Methods')
            self.method_invert = ipywidgets.Button(description='Invert Methods', button_style='warning')
            self.method_unselect = ipywidgets.Button(description='Unselect all', button_style='danger')

            self.method_restore.style.button_color = 'lightgreen'




            # ALL

            self.all_restore = ipywidgets.Button(description='Restart', button_style='danger')

    def set_buttonsh(self):
        if True:
            # axis
            self.xaxis = ipywidgets.Dropdown(options=self.unkeys,
                    value=self.unkeys[self.xinit], description='x-axis:')
            self.bins_textbox = ipywidgets.IntText(value=60, description='Bins: ')
            self.norm_h = ipywidgets.Checkbox(value=False,
                            description='Normalise')
            self.axis_restoreh =  ipywidgets.Button(description='Reset axis')

            self.xlim1_textbox = ipywidgets.FloatText(value=np.amin(self.d[self.unreadable[self.xaxis.value]]), description='x Minimum:')
            self.xlim2_textbox = ipywidgets.FloatText(value=np.max(self.d[self.unreadable[self.xaxis.value]]), description='x Maximum:')
            self.xlims_restore = ipywidgets.Button(description='Reset x range')

            self.button_h = ipywidgets.Button(description='Refresh')

        if True:
            self.title_textbox = ipywidgets.Text(
                value='Exoplanet Population',
                description='Title: ')
            self.hsize_slider = ipywidgets.IntSlider(
                value=9, min=2, max=20,
                description='Plot hsize:')
            self.vsize_slider = ipywidgets.IntSlider(
                value=6, min=2, max=20,
                description='Plot vsize:')

            self.bins_alpha = ipywidgets.FloatSlider(
                value=0.75, min=0., max=1., step=0.01,
                description='Transparency:', readout_format='.2f')
            self.xlogh_button = ipywidgets.ToggleButton(
                    value=False, description='x log')
            self.ylogh_button = ipywidgets.ToggleButton(
                    value=False, description='y log')
            self.grid_checkbox = ipywidgets.Checkbox(
                    value=False, description='Grid')

            self.style_drop = ipywidgets.Dropdown(
                options=self.style_list,
                value=self.style_list[0],
                description='Plot Style: ')
            self.bins_fc = ipywidgets.ColorPicker(
                concise=False,
                description='Face color: ',
                value='#008000')
            self.bins_ec = ipywidgets.ColorPicker(
                concise=False,
                description='Edge color: ',
                value='#000000')

        if True:
            # TAB 4
            self.plot_fmt = ipywidgets.RadioButtons(options=['png', 'pdf', 'svg'],
                            value='pdf', description='Plot format:')
            self.savefile_name = ipywidgets.Text(
                value='current_plot', description='File Name')
            self.plot_save_button = ipywidgets.Button(
                description='Save plot')

            self.button = ipywidgets.Button(
                            description='Refresh')


        if True:
            # methods
            self.methodbutton = ipywidgets.ToggleButton(
                value=self.switch_method, description='By Method',
                icon='check')

            self.method_dict = {}
            for m in self.methods:
                self.method_dict[m] = ipywidgets.ToggleButton(value=self.fav_met[m], description=m, icon='check')
                self.marker_presets[m] = {'marker':self.marker_styles['Circle'], 's':None, 'alpha':0.9,
                                                        'facecolors':'none',
                                                        'edgecolors':self.method_colors[m],
                                                        'linewidths':1.5}

            self.method_restore = ipywidgets.Button(description='Reset Methods')
            self.method_invert = ipywidgets.Button(description='Invert Methods', button_style='warning')
            self.method_unselect = ipywidgets.Button(description='Unselect all', button_style='danger')

            self.method_restore.style.button_color = 'lightgreen'

            self.all_restore = ipywidgets.Button(description='Restart', button_style='danger')

    def set_methods(self):
        if True:
            # AXIS
            @self.axis_restore.on_click
            def restore_axis(b):
                self.xaxis.value = self.unkeys[self.xinit]
                self.yaxis.value = self.unkeys[self.yinit]
                self.xlog_button.value = True
                self.ylog_button.value = True

            @self.axis_invert.on_click
            def invert_axis(b):
                foo, bar = self.xaxis.value, self.yaxis.value
                self.xaxis.value = bar
                self.yaxis.value = foo

                foo, bar = self.xlog_button.value, self.ylog_button.value
                self.xlog_button.value = bar
                self.ylog_button.value = foo

            # LIMITS
            @self.xlims_restore.on_click
            def restore_xlims(b):
                self.xlim1_textbox.value = np.min(self.d[self.unreadable[self.xaxis.value]])
                self.xlim2_textbox.value = np.max(self.d[self.unreadable[self.xaxis.value]])

            @self.ylims_restore.on_click
            def restore_ylims(b):
                self.ylim1_textbox.value = np.min(self.d[self.unreadable[self.yaxis.value]])
                self.ylim2_textbox.value = np.max(self.d[self.unreadable[self.yaxis.value]])



            # METHODS
             #method_dict[methods[i]] = ipywidgets.ToggleButton(value=fav_met[i]

            @self.method_restore.on_click
            def restore_methods(b):
                for m in self.methods:
                    self.method_dict[m].value = self.fav_met[m]

            @self.method_invert.on_click
            def invert_methods(b):
                for m in self.methods:
                    foo = self.method_dict[m].value
                    self.method_dict[m].value = not foo

            @self.method_unselect.on_click
            def unselect_methods(b):
                for m in self.methods:
                    if m == 'Radial Velocity':
                        pass
                    else:
                        self.method_dict[m].value = False


            @self.all_restore.on_click
            def restore_all(b):
                self.method_restore.click()
                self.axis_restore.click()
                self.xlims_restore.click()
                self.ylims_restore.click()

            @self.button.on_click
            def plot_on_click(b):
                self.out.clear_output(wait=True)
                if self.scatter_applyto.value == 'All':
                    for m in self.methods:
                        self.marker_presets[m]['marker'] = self.marker_styles[self.scatter_marker.value]
                        self.marker_presets[m]['s'] = self.scatter_size.value
                        self.marker_presets[m]['alpha'] = self.scatter_alpha.value
                        #self.marker_presets[m]['facecolors'] = self.scatter_fc.value
                        #self.marker_presets[m]['edgecolors'] = self.scatter_ec.value
                        self.marker_presets[m]['linewidths'] = self.scatter_ew.value
                else:

                    self.marker_presets[self.scatter_applyto.value]['marker'] = self.marker_styles[self.scatter_marker.value]
                    self.marker_presets[self.scatter_applyto.value]['s'] = self.scatter_size.value
                    self.marker_presets[self.scatter_applyto.value]['alpha'] = self.scatter_alpha.value
                    self.marker_presets[self.scatter_applyto.value]['facecolors'] = self.scatter_fc.value
                    self.marker_presets[self.scatter_applyto.value]['edgecolors'] = self.scatter_ec.value
                    self.marker_presets[self.scatter_applyto.value]['linewidths'] = self.scatter_ew.value

                with self.out:
                    self.plot()
                    pl.show()

            @self.plot_save_button.on_click
            def save_plot_on_click(b):
                self.fig.savefig(self.savefile_name.value, format=self.plot_fmt.value)

            @self.ss_add_box.on_click
            def draw_ss(b):
                self.include_ss = ~self.include_ss

    def set_methodsh(self):
        if True:
            @self.axis_restoreh.on_click
            def restore_axish(b):
                self.xaxis.value = self.unkeys[self.xinit]
                self.bins_textbox.value = 60
                self.xlogh_button.value = False
                self.ylogh_button.value = False
                self.norm_h.value = False

            @self.xlims_restore.on_click
            def restore_xlims(b):
                self.xlim1_textbox.value = np.min(self.d[self.unreadable[self.xaxis.value]])
                self.xlim2_textbox.value = np.max(self.d[self.unreadable[self.xaxis.value]])

            @self.method_restore.on_click
            def restore_methods(b):
                for m in self.methods:
                    self.method_dict[m].value = self.fav_met[m]

            @self.method_invert.on_click
            def invert_methods(b):
                for m in self.methods:
                    foo = self.method_dict[m].value
                    self.method_dict[m].value = not foo

            @self.method_unselect.on_click
            def unselect_methods(b):
                for m in self.methods:
                    if m == 'Radial Velocity':
                        pass
                    else:
                        self.method_dict[m].value = False

            @self.all_restore.on_click
            def restore_all(b):
                self.method_restore.click()
                self.axis_restoreh.click()
                self.xlims_restore.click()

            @self.plot_save_button.on_click
            def save_plot_on_click(b):
                self.fig.savefig(self.savefile_name.value, format=self.plot_fmt.value)

            @self.button_h.on_click
            def plot_on_click(b):
                self.out_h.clear_output(wait=True)
                with self.out_h:
                    self.plot_h()
                    pl.show()
        pass

    def set_tabs(self):
        if True:
            # TABS
            t1_row1 = [self.xaxis, self.yaxis, self.axis_restore, self.axis_invert]
            t1_row2 = [self.xlim1_textbox, self.xlim2_textbox, self.xlims_restore, self.xlog_button]
            t1_row3 = [self.ylim1_textbox, self.ylim2_textbox, self.ylims_restore, self.ylog_button]
            t1_row4 = [self.all_restore, self.ss_add_box]
            tab1_ = [t1_row1, t1_row2, t1_row3, t1_row4]


            # general
            tab2_acc1_row1 = [self.title_textbox, self.title_fontsize]
            tab2_acc1_row2 = [self.hsize_slider, self.vsize_slider]
            tab2_acc1_row3 = [self.style_drop, self.grid_checkbox]
            tab2_acc1 = [tab2_acc1_row1, tab2_acc1_row2, tab2_acc1_row3]

            # axis
            tab2_acc2_row1 = [self.xaxis_label, self.xaxis_fontsize]
            tab2_acc2_row2 = [self.yaxis_label, self.yaxis_fontsize]
            tab2_acc2 = [tab2_acc2_row1, tab2_acc2_row2]

            # markers
            tab2_acc3_row0 = [self.scatter_applyto]
            tab2_acc3_row1 = [self.scatter_marker, self.scatter_size, self.scatter_alpha]
            tab2_acc3_row2 = [self.scatter_fc, self.scatter_ec, self.scatter_ew]
            tab2_acc3 = [tab2_acc3_row0, tab2_acc3_row1, tab2_acc3_row2]

            # line
            tab2_acc4_row1 = [self.line_style, self.line_color]
            tab2_acc4_row2 = [self.line_width, self.line_alpha]

            tab2_acc4 = [tab2_acc4_row1, tab2_acc4_row2]

            tab2_acc = [tab2_acc1, tab2_acc2, tab2_acc3, tab2_acc4]
            acc_titles = ['General', 'Axis', 'Markers', 'Line']
            accordion = ipywidgets.Accordion(children=[VBox(children=[HBox(children=[wid for wid in row]) for row in rows]) for rows in tab2_acc])

            for i in range(len(acc_titles)):
                accordion.set_title(i, acc_titles[i])

            t3_row1 = [self.method_dict[m] for m in self.methods[:4]]
            t3_row2 = [self.method_dict[m] for m in self.methods[4:8]]
            t3_row3 = [self.method_dict[m] for m in self.methods[8:11]]
            t3_row4 = [self.method_restore, self.method_invert, self.method_unselect, self.methodbutton]
            tab3_ = [t3_row1, t3_row2, t3_row3, t3_row4]


            t4_row1 = [self.savefile_name, self.plot_fmt]
            t4_row2 = [self.plot_save_button]
            tab4_ = [t4_row1, t4_row2]

            tab1 = VBox(children=[HBox(children=row) for row in tab1_])
            tab2 = accordion
            tab3 = VBox(children=[HBox(children=row) for row in tab3_])
            tab4 = VBox(children=[HBox(children=row) for row in tab4_])

            tab_names = ['Plot', 'Styling', 'Methods', 'Export']

            self.tab = ipywidgets.Tab(children=[tab1, accordion, tab3, tab4])

            for i in range(len(tab_names)):
                self.tab.set_title(i, tab_names[i])


            ##########
        pass

    def set_tabsh(self):
        if True:
            th1_row1 = [self.xaxis, self.bins_textbox, self.norm_h, self.axis_restoreh]
            th1_row2 = [self.xlim1_textbox, self.xlim2_textbox, self.xlims_restore]
            th1_row3 = [self.all_restore]
            tabh1 = [th1_row1, th1_row2, th1_row3]


            th2_row1 = [self.title_textbox, self.hsize_slider, self.vsize_slider]
            th2_row2 = [self.bins_alpha, self.xlogh_button, self.ylogh_button, self.grid_checkbox]
            th2_row3 = [self.style_drop, self.bins_fc, self.bins_ec]
            tabh2 = [th2_row1, th2_row2, th2_row3]


            th3_row1 = [self.method_dict[m] for m in self.methods[:4]]
            th3_row2 = [self.method_dict[m] for m in self.methods[4:8]]
            th3_row3 = [self.method_dict[m] for m in self.methods[8:11]]
            th3_row4 = [self.method_restore, self.method_invert, self.method_unselect]
            tabh3 = [th3_row1, th3_row2, th3_row3, th3_row4]

            th4_row1 = [self.savefile_name, self.plot_fmt]
            th4_row2 = [self.plot_save_button]
            tabh4 = [th4_row1, th4_row2]

            tabh_names = ['Plot', 'Styling', 'Methods', 'Export']
            tabsh = {'tabh1':tabh1, 'tabh2':tabh2, 'tabh3':tabh3, 'tab4':tabh4}
            for tabh in tabsh:
                setattr(self, tabh, VBox(children=[HBox(children=row) for row in tabsh[tabh]]))


            self.tabh = ipywidgets.Tab(children=[getattr(self, t) for t in tabsh])
            for i in range(len(tabh_names)):
                self.tabh.set_title(i, tabh_names[i])

    def set_data(self):
        if self.data == 'offline' or self.data == None:
            data = dataloc
            self.d = pd.read_csv(data, usecols=good_cols)
            self.ss = pd.read_csv(get_data('tables/ss_list_offline.csv'))

            # SET COLORS
            self.methods = np.unique(self.d[self.method_key])
            fav_met = [False, False, True, True, True, False, False, False, True, True, True]

            self.good_reads = pd.read_csv(get_data('tables/good_reads_offline.dat')).values.T[0]
            initcoords = [5, 9]


        elif self.data == 'NasaExoplanetArchive':
            self.d = pd.DataFrame.from_records(getattr(pyasl, self.data)().getAllData())  ###
            self.ss = pd.read_csv(get_data('tables/ss_list_nasa.csv'))

            # SET COLORS
            self.methods = np.array(['unique'])  ###
            fav_met = [True]  ###

            self.good_reads = pd.read_csv(get_data('tables/good_reads_nasa.dat')).values.T[0]
            initcoords = [5, 6]

        elif self.data == 'ExoplanetEU2':
            v = pyasl.ExoplanetEU2()
            self.d = v.getAllDataPandas()
            self.ss = pd.read_csv(get_data('tables/ss_list_epeu.csv'))

            # SET COLORS
            self.methods = np.unique(self.d['detection_type'])
            # Astrometry, Default, Imaging, Microlensing
            #Primary Transit, Radial Velocity, TTV, Timing
            fav_met = [False, False, True, True,
                       True, True, False, False]

            self.good_reads = pd.read_csv(get_data('tables/good_reads_epeu.dat')).values.T[0]
            initcoords = [10, 2]


        elif self.data == 'ExoplanetsOrg':
            self.d = pd.DataFrame.from_records(getattr(pyasl, self.data)().getAllData())  ###

            self.ss = pd.read_csv(get_data('tables/ss_list_eporg.csv'))

            # SET COLORS
            self.methods = np.unique(self.d['pl_dtype'])
            # 'Imaging', 'Microlensing', 'None', 'RV',
            #'Timing', 'Transit', 'Transit Timing Variations'
            fav_met = [True, True, False, True,
                       False, True, False]

            self.good_reads = pd.read_csv(get_data('tables/good_reads_eporg.dat')).values.T[0]
            initcoords = [10, 2]



        else:
            raise ValueError('String not recognised! Try with offline/NasaExoplanetArchive/ExoplanetEU2/ExoplanetsOrg')
            pass

        self.keys = [*self.d.columns]

        self.readable = {}

        for i in range(len(self.keys)):
            self.readable[self.keys[i]] = self.good_reads[i]  ###

        self.unreadable = {v: k for k, v in self.readable.items()}
        self.unkeys = [*self.unreadable.keys()]

        self.method_colors = {}
        self.fav_met = {}

        for i in range(len(self.methods)):
            self.method_colors[self.methods[i]] = 'C%i' % i
            self.fav_met[self.methods[i]] = fav_met[i]

        self.xinit = initcoords[0]
        self.yinit = initcoords[1]

    def setup(self):
        self.set_buttons()
        self.set_methods()
        self.set_tabs()
        pass

    def setuph(self):
        self.set_buttonsh()
        self.set_methodsh()
        self.set_tabsh()
        pass


    def display(self):
        self.set_data()
        #raise ValueError('String not recognised! Try with offline/NEXA/exoplanetEU/exoplanetsORG')

        self.setup()
        return VBox(children=[self.tab, self.button, self.out])

    def display_hist(self):
        self.set_data()
        self.setuph()
        return VBox(children=[self.tabh, self.button_h, self.out_h])

    pass

















#
