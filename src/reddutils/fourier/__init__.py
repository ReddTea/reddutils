# @auto-fold regex /^\s*if/ /^\s*else/ /^\s*def/
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# version 0.0.1
# date 20 aug 2022

from scipy.fft import fft, fftfreq, fftshift
from scipy import signal
import numpy as np

import matplotlib.pyplot as pl
from matplotlib import ticker
import matplotlib.gridspec as gridspec


import ipywidgets
from ipywidgets import HBox, VBox

class fourier:
    def __init__(self):
        # Default values
        types_ = [self.create_cosine, self.create_sine, self.create_triangles, self.create_squares, self.create_gauss]
        self.type_dict = {'Cosine':types_[0], 'Sine':types_[1], 'Triangles':types_[2],
                     'Squares':types_[3], 'Gaussian':types_[4]}

        self.keys = [*self.type_dict]


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

        self.out = ipywidgets.Output()
        self.out_text = ipywidgets.Output()
        pass


    def create_sine(self) -> list:
        x = np.linspace(-self.duration_slider.value, self.duration_slider.value, self.sr_slider.value * 2 * self.duration_slider.value, endpoint=False)
        y = np.sin(x * self.freq_slider.value * 2 * np.pi)
        return x, y


    def create_cosine(self) -> list:
        x = np.linspace(-self.duration_slider.value, self.duration_slider.value, self.sr_slider.value * 2 * self.duration_slider.value, endpoint=False)
        y = np.cos(x * self.freq_slider.value * 2 * np.pi)
        return x, y


    def create_triangles(self) -> list:
        x = np.linspace(0, self.duration_slider.value, self.sr_slider.value * 2 * self.duration_slider.value, endpoint=False)
        #frequencies = x * freq()
        y = signal.sawtooth(x * self.freq_slider.value * 2 * np.pi, width=0.5)
        return x, y


    def create_squares(self) -> list:
        x = np.linspace(0, self.duration_slider.value, self.sr_slider.value * self.duration_slider.value, endpoint=False)
        frequencies = x * self.freq_slider.value
        y = signal.square(2 * np.pi * frequencies)

        y[y < 0] = 0
        return x, y


    def create_gauss(self) -> list:
        x = np.linspace(-self.duration_slider.value, self.duration_slider.value, self.sr_slider.value * 2 * self.duration_slider.value, endpoint=False)
        i, q, e = signal.gausspulse(x, fc=self.freq_slider.value, retquad=True, retenv=True)
        return x, e


    def henshin(self, signal) -> list:
        N = len(signal)
        yf = fft(signal)
        xf = fftfreq(N, 1 / self.sr_slider.value)

        return xf, yf


    def plot(self):
        # signal_type, duration=8, sample_rate=32, frequency=1, Display_Samples=False
        #freq = self.freq_slider.value  # tag out
        #sample_rate = self.sr_slider.value    # tag out
        #duration = self.duration_slider.value    # tag out
        func = self.type_dict[self.signal_dd.value]
        display_samples = self.display_samples_checkbox.value

        # general
        pl.style.use(self.style_drop.value)
        #########################

        x, y = func()

        self.fig, (ax, axr) = pl.subplots(2, figsize=(self.hsize_slider.value, self.vsize_slider.value), dpi=80)
        #gs = gridspec.GridSpec(4, 4)

        #ax = fig.add_subplot(gs[:2, :])

        #pl.rcParams['font.size'] = 18
        #pl.rcParams['axes.linewidth'] = 2
        pl.subplots_adjust(hspace=0.3)
        pl.minorticks_on()
        if self.grid_checkbox.value:
            ax.grid()
            axr.grid()

        if True:
            #ax = fig.add_axes([0, 0, 1, 1])

            ax.xaxis.set_tick_params(which='major', size=10, width=2, direction='in', top='on')
            ax.xaxis.set_tick_params(which='minor', size=7, width=2, direction='in', top='on')
            ax.yaxis.set_tick_params(which='major', size=10, width=2, direction='in', right='on')
            ax.yaxis.set_tick_params(which='minor', size=7, width=2, direction='in', right='on')

            #axr = fig.add_subplot(gs[2:, :])

            axr.yaxis.set_tick_params(which='major', size=10, width=2, direction='in', right='on')
            axr.yaxis.set_tick_params(which='minor', size=7, width=2, direction='in', right='on')
            axr.xaxis.set_tick_params(which='major', size=10, width=2, direction='in', top='on')
            axr.xaxis.set_tick_params(which='minor', size=7, width=2, direction='in', top='on')

        ax.set_title(self.title_textbox.value, fontsize=self.title_fontsize.value)
        ax.set_xlabel(self.xaxis_label.value, fontsize=self.xaxis_fontsize.value)
        ax.set_ylabel(self.yaxis_label.value, fontsize=self.yaxis_fontsize.value)

        ax.axhline(0, c='gray')
        #ax.errorbar(x_, y_, yerr=yerr_, fmt='o', alpha=0.9, label='data', markersize=10)

        sr_holder = self.sr_slider.value
        self.sr_slider.value = 256
        x_, y_ = func()
        self.sr_slider.value = sr_holder

        ax.plot(x_, y_, ls=self.line_styles[self.line_style.value],
                c=self.line_color.value, label = 'Signal', alpha=self.line_alpha.value,
                lw=self.line_width.value)

        if display_samples:
            ax.scatter(x, y, c=self.scatter_color.value,
                alpha=self.scatter_alpha.value, s=self.scatter_size.value,
                marker=self.marker_styles[self.scatter_marker.value])

        xf, yf = self.henshin(y)
        o = np.argsort(xf)
        xf, yf = xf[o], yf[o]

        axr.plot(xf, abs(yf), ls=self.line_styles[self.line_style.value],
                c=self.line_color.value, label = 'Signal', alpha=self.line_alpha.value,
                lw=self.line_width.value)
        if display_samples:
            axr.scatter(xf, abs(yf), c=self.scatter_color.value,
                alpha=self.scatter_alpha.value, s=self.scatter_size.value,
                marker=self.marker_styles[self.scatter_marker.value])
        #ax.set_title('Signal and its Fourier Transform', fontsize=28)
        axr.set_xlabel(self.xaxis_label2.value, fontsize=self.xaxis_fontsize.value)
        axr.set_ylabel(self.yaxis_label2.value, fontsize=self.yaxis_fontsize.value)
        axr.set_xlim(-8, 8)
        pass


    def set_tabs(self):
        tab1_row1 = [self.signal_dd]
        tab1_row2 = [self.duration_slider, self.freq_slider]
        tab1_row3 = [self.sr_slider, self.display_samples_checkbox]
        tab1_ = [tab1_row1, tab1_row2, tab1_row3]

        # general
        tab2_acc1_row1 = [self.title_textbox, self.title_fontsize]
        tab2_acc1_row2 = [self.hsize_slider, self.vsize_slider]
        tab2_acc1_row3 = [self.style_drop, self.grid_checkbox]
        tab2_acc1 = [tab2_acc1_row1, tab2_acc1_row2, tab2_acc1_row3]


        # axis
        tab2_acc2_row1 = [self.xaxis_label, self.xaxis_label2, self.xaxis_fontsize]
        tab2_acc2_row2 = [self.yaxis_label, self.yaxis_label2, self.yaxis_fontsize]
        #tab2_acc4_row3 = []
        #tab2_acc4_row4 = [self.grid_checkbox]
        tab2_acc2 = [tab2_acc2_row1, tab2_acc2_row2]

        # markers
        tab2_acc3_row1 = [self.scatter_marker, self.scatter_color]
        tab2_acc3_row2 = [self.scatter_size, self.scatter_alpha]
        #tab2_acc3_row3 = [self.scatter_alpha]
        tab2_acc3 = [tab2_acc3_row1, tab2_acc3_row2]
        # line
        tab2_acc4_row1 = [self.line_style, self.line_color]
        tab2_acc4_row2 = [self.line_width, self.line_alpha]
        #tab2_acc4_row3 = [self.line_alpha]
        tab2_acc4 = [tab2_acc4_row1, tab2_acc4_row2]



        tab2_acc = [tab2_acc1, tab2_acc2, tab2_acc3, tab2_acc4]
        acc_titles = ['General', 'Axis', 'Markers', 'Line']

        accordion = ipywidgets.Accordion(children=[VBox(children=[HBox(children=[wid for wid in row]) for row in rows]) for rows in tab2_acc])

        for i in range(len(acc_titles)):
            accordion.set_title(i, acc_titles[i])

        tab3_row1 = [self.savefile_name, self.plot_fmt]
        tab3_row2 = [self.plot_save_button]
        tab3_ = [tab3_row1, tab3_row2]

        tab1 = VBox(children=[HBox(children=row) for row in tab1_])
        tab2 = accordion
        tab3 = VBox(children=[HBox(children=row) for row in tab3_])
        tab_names = ['Plot', 'Styling', 'Export']
        self.tab = ipywidgets.Tab(children=[tab1,tab2, tab3])

        for i in range(len(tab_names)):
            self.tab.set_title(i, tab_names[i])

        pass


    def set_buttons(self):
        ### TAB 1
        self.signal_dd = ipywidgets.Dropdown(options=self.keys,
                value=self.keys[0], description='Signal Type:')

        self.duration_slider = ipywidgets.IntSlider(
                value=8, min=1, max=64, description='Duration: ')

        self.sr_slider = ipywidgets.IntSlider(
                value=32, min=1, max=256, description='Sample Rate: ')

        self.freq_slider = ipywidgets.FloatSlider(
            value=1, min=0.1, max=10, step=0.1,
            description='Frequency:', readout_format='.1f')

        self.period_slider = ipywidgets.FloatSlider(
            value=1, min=2*np.pi/10, max=2*np.pi/0.1, step=2*np.pi/0.1,
            description='Period:', readout_format='.1f')

        self.display_samples_checkbox = ipywidgets.Checkbox(
                            value=False, description='Display Samples')

        #### TAB 2
        if True:
            # general
            self.title_textbox = ipywidgets.Text(
                value='Signal and its Fourier Transform',
                description='Title: ')

            self.title_fontsize = ipywidgets.FloatText(value=28,
                description='Title Fontsize: ',disabled=False)

            self.hsize_slider = ipywidgets.IntSlider(
                value=10, min=2, max=20,
                description='Plot hsize:')

            self.vsize_slider = ipywidgets.IntSlider(
                value=8, min=2, max=20,
                description='Plot vsize:')

            self.style_drop = ipywidgets.Dropdown(
                options=self.style_list,
                value=self.style_list[0],
                description='Plot Style:')

            self.grid_checkbox = ipywidgets.Checkbox(
                        value=False, description='Grid')


            # axis
            self.xaxis_label = ipywidgets.Text(
                value='Time',
                description='x-axis label: ')

            self.yaxis_label = ipywidgets.Text(value='Amplitude',
                description='y-axis label: ')

            self.xaxis_fontsize = ipywidgets.FloatText(value=22,
                description='x-label fontsize: ')

            self.yaxis_fontsize = ipywidgets.FloatText(value=22,
                description='y-label fontsize: ')

            self.xaxis_label2 = ipywidgets.Text(
                value='Frequencies',
                description='Bottom x-axis label: ')

            self.yaxis_label2 = ipywidgets.Text(value='Power',
                description='Bottom y-axis label: ')


            # Scatter
            self.scatter_alpha = ipywidgets.FloatSlider(
                value=1., min=0., max=1., step=0.01,
                description='Transparency:', readout_format='.2f')


            self.scatter_marker = ipywidgets.Dropdown(options=self.marker_keys,
                    value=self.marker_keys[0], description='Shape: ')

            self.scatter_color = ipywidgets.ColorPicker(
                concise=True,
                description='Color: ',
                value=self.cn_colors[1])

            self.scatter_size = ipywidgets.IntSlider(
                        value=20, min=1, max=40,
                        description='Marker size: ')



            # Line

            self.line_style = ipywidgets.Dropdown(options=self.line_keys,
                    value=self.line_keys[0], description='Style: ')

            self.line_color = ipywidgets.ColorPicker(
                concise=True,
                description='Color: ',
                value=self.cn_colors[0])

            self.line_width = ipywidgets.FloatSlider(
                        value=2, min=1, max=5,
                        description='Width: ')

            self.line_alpha = ipywidgets.FloatSlider(
                value=1., min=0., max=1., step=0.01,
                description='Transparency:', readout_format='.2f')



            ########
        ### TAB 3
        if True:
            self.plot_save_button = ipywidgets.Button(
                    description='Save plot')

            self.plot_fmt = ipywidgets.RadioButtons(options=['png', 'pdf', 'svg'],
                                value='pdf', description='Plot format:', disabled=False)

            self.savefile_name = ipywidgets.Text(
                    value='current_plot',
                    description='File Name')

        ######
        self.button = ipywidgets.Button(description='Refresh')
        @self.button.on_click
        def plot_on_click(b):
            self.out.clear_output(wait=True)
            self.out_text.clear_output(wait=True)
            with self.out:
                self.plot()
                pl.show()

        pass


    def setup(self):
        self.set_buttons()
        self.set_tabs()


    def display(self):
        self.setup()
        return VBox(children=[self.tab, self.button, self.out])
