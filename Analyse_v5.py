#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
import os
import xlrd as rd
import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime as dt, timedelta as delta

from Xaxis import Xaxis
from Values import Values
from COLOR import hsv2rgb
from WriteDown import Organize

## Draw the following items:
## 
##      BAR + [categories]
## ^                |
## |        |       |
## |    |   |   |   |   |
## -------------------------->
##      A   B   C   D   E
##
##      BAR + hour/day/month + [categories]
## ^                         -A
## |                         -B
## |     |  |       ||
## |    ||  ||  ||  ||  ||
## -------------------------->
##      1   2   3   4   5
##
##      LINE + week/month/season/year + [categories]
## ^  _         ____________
## |_/ \      /              xN
## |    \____/
## -------------------------->
##  1 2 3 4 5 6 7 8 9 10 11 12

class Analyse:
    """Data Analysis"""
    def __init__(self, AB, *args, **kwarg):
        """
        Args:
            AB (AccountingBook): AccountingBook object.
            args (tuple):
                CALC_MODE_OFF
                    kind (str): `line` or `bar`.
                    category (list): List of categories.
                    interval (str *): One of [hour day week month season year]. * optional in some cases.
                CALC_MODE_ON
                    kind (str): `engle` or `custom`.
                    interval (str): week month season year
                    category (list *): [A, B], calculate A/B.
            kwarg (dict):
                start (datetime.datetime)
                end (datetime.datetime)

        Arguments:
            order (Organize)
            xaxis_obj (Xaxis)
            values_obj (Values)
        """
        self.ab = AB

        args = list(args)
        for i in range(len(args)):
            if isinstance(args[i], str):
                args[i] = args[i].lower()
        kind = [arg for arg in args if arg in ['line', 'bar', 'engle', 'custom']]
        self.kind = kind[0]

        for arg in args:
            if not arg == self.kind:
                if isinstance(arg, list):
                    self.category = arg
                if isinstance(arg, str):
                    self.interval = arg

        switch1 = {'line':False, 'bar':False, 'engle':True, 'custom':True}
        self.CALC_MODE = switch1[self.kind]

        try:
            if isinstance(self.category, list):
                pass
        except AttributeError:
            switch2 = {'engle':['食品酒水', '支出']}
            self.category = switch2[self.kind]

        try:
            if isinstance(self.interval, str):
                pass
        except AttributeError:
            self.interval = None

        self.s_time = kwarg['start'] if 'start' in kwarg else AB.init_time
        self.e_time = kwarg['end'] if 'end' in kwarg else AB.update_time + delta(days=1)

        self.order = Organize(self.ab, self.s_time, self.e_time)
        self.order.update()
        name = kwarg['name'] if 'name' in kwarg else 'v5.xls'
        self.order.save(name)

        self.xaxis_obj = Xaxis(self.ab, self.kind, self.category, self.interval, start=self.s_time, end=self.e_time)
        self.values_obj = Values(self.ab, self.kind, self.category, self.interval, start=self.s_time, end=self.e_time, name=name)

    def __repr__(self):
        """Representation

        Args:
            self (Analyse): The current Analyse object.

        Returns:
            A string to represent the current Analyse instance.
        """
        if self.category:
            return self.ab.__repr__() + ' -- ' + self.kind.upper() + ' -- ' + self.interval.upper() + ' -- ' + str(self.category)
        else:
            return self.ab.__repr__() + ' -- ' + self.kind.upper() + ' -- ' + self.interval.upper()

    def plot_data(self, **kwarg):
        """Main plot function

        Args:
            xlim (tuple)
            ylim (tuple)
            xaxis (numpy.ndarray)
            values (numpy.ndarray)
            reference (dict): data, color, note
            bg/background (bool)
            title (str)
            figsize (tuple)
            dpi (int)
            show (bool)
        """
        xaxis = kwarg['xaxis'] if 'xaxis' in kwarg else self.xaxis_obj.xaxis # nparray
        values = kwarg['values'] if 'values' in kwarg else self.values_obj.values # {A:{value:nparray, sum:nparray}, ...}
        val = values
        valmin, valmax = np.inf, -np.inf
        keys = val.keys()
        if list(keys) == ['value', 'sum']:
            minimum = min(val['value'].min(), val['sum'].min())
            maximum = max(val['value'].max(), val['sum'].max())
        else:
            for item in val:
                minimum = min(val[item]['value'].min(), val[item]['sum'].min())
                maximum = max(val[item]['value'].max(), val[item]['sum'].max())
                if minimum < valmin:
                    valmin = minimum
                if maximum > valmax:
                    valmax = maximum

        if valmin <= 0 and valmax <= 0:
            for item in val:
                val[item]['value'] = -val[item]['value']
                val[item]['sum'] = -val[item]['sum']
            values = val

        figsize = kwarg['figsize'] if 'figsize' in kwarg else (max(12, 0.5*len(xaxis)), 8)
        dpi = kwarg['dpi'] if 'dpi' in kwarg else 200

        if 'bg' in kwarg or 'background' in kwarg:
            try:
                bg = kwarg['bg']
            except KeyError:
                bg = kwarg['background']
        else:
            bg = False

        self.fig = plt.figure(figsize=figsize, dpi=dpi)
        if 'xlim' in kwarg and 'ylim' in kwarg:
            xmin, xmax = kwarg['xlim']
            ymin, ymax = kwarg['ylim']
            xmin -= (xmax-xmin)/(len(xaxis)+1)
            xmax += (xmax-xmin)/(len(xaxis)+1)
            ymin -= (ymax-ymin)/(len(xaxis)+1)
            ymax += (ymax-ymin)/(len(xaxis)+1)
            self.ax = self.fig.add_subplot(1,1,1,xlim=(xmin,xmax),ylim=(ymin,ymax))
        else:
            self.ax = self.fig.add_subplot(1,1,1)

        plt.xticks(range(len(xaxis)), xaxis, rotation=45)
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS'] # display Chinese

        if self.CALC_MODE:
            self._plot_style_III(xaxis, values)
        else:
            if self.kind == 'bar':
                if self.interval is None:
                    self._plot_style_I(xaxis, values)
                else:
                    self._plot_style_II(xaxis, values)
            else:
                self._plot_style_III(xaxis, values)

        if 'reference' in kwarg:
            data = kwarg['reference']['data']
            color = kwarg['reference']['color'] if 'color' in kwarg['reference'] else ['k' for _ in range(len(data))]
            note = kwarg['reference']['note'] if 'note' in kwarg['reference'] else ['' for _ in range(len(data))]
            if not ('xmin' in locals() or 'xmax' in locals()):
                xmin, xmax = self.ax.get_xlim()
            for i in range(len(data)):
                self.ax.plot([xmin,xmax],[data[i],data[i]],color=color[i],linestyle='-.',alpha=0.3)
                plt.text(xmax, data[i], note[i])

        if 'legend' in kwarg:
            plt.legend(kwarg['legend'], loc='upper right')

        if 'xlim' in kwarg and 'ylim' in kwarg:
            X = [[0.6,0.6],[0.7,0.7]]
            plt.imshow(X,interpolation='bicubic',cmap=plt.cm.bwr,extent=(xmin, xmax, ymin, ymax),alpha=0.3,aspect='auto')

        if 'title' in kwarg:
            self.ax.set_title(kwarg['title'])
            if not os.path.exists(os.path.join('.','img')):
                os.mkdir(os.path.join('.','img'))
            plt.savefig(os.path.join('.','img',kwarg['title']+'.png'))

        show = kwarg['show'] if 'show' in kwarg else True
        if show:
            plt.show()

    def plot_calc_data(self, **kwarg):
        """plot function

        Args:
            xlim (tuple)
            ylim (tuple)
            xaxis (numpy.ndarray)
            values (numpy.ndarray)
            reference (dict): data, color, note
            bg/background (bool)
            title (str)
            figsize (tuple)
            dpi (int)
            show (bool)
        """
        keywords = {}
        if 'xlim' in kwarg:
            xlim = kwarg['xlim']
            keywords['xlim'] = xlim
        if 'ylim' in kwarg:
            ylim = kwarg['ylim']
            keywords['ylim'] = ylim
        if 'reference' in kwarg:
            reference = kwarg['reference']
            keywords['reference'] = reference
        if 'title' in kwarg:
            title = kwarg['title']
            keywords['title'] = title
        if 'bg' in kwarg or 'background' in kwarg:
            try:
                bg = kwarg['bg']
                keywords['bg'] = bg
            except KeyError:
                bg = kwarg['background']
                keywords['bg'] = bg
        else:
            bg = False
            keywords['bg'] = bg
        xaxis = kwarg['xaxis'] if 'xaxis' in kwarg else self.xaxis_obj.xaxis # nparray
        values = kwarg['values'] if 'values' in kwarg else self.values_obj.values # {A:{value:nparray, sum:nparray}, ...}
        figsize = kwarg['figsize'] if 'figsize' in kwarg else (max(12, 0.5*len(xaxis)), 8)
        dpi = kwarg['dpi'] if 'dpi' in kwarg else 128
        show = kwarg['show'] if 'show' in kwarg else True
        keywords['xaxis'] = xaxis
        keywords['values'] = values
        keywords['figsize'] = figsize
        keywords['dpi'] = dpi
        keywords['show'] = show

        if self.kind == 'engle':
            if not 'reference' in keywords:
                keywords['reference'] = {
                    'data':[0.2, 0.3, 0.4, 0.5, 0.6],
                    'color':['#0000FF','#008888','#00FF00','#888800','#FF0000'],
                    'note':['极其富裕','富足','相对富裕','小康','温饱']
                    }
            if not 'title' in keywords:
                keywords['title'] = '恩格尔系数'
            if not 'xlim' in keywords:
                keywords['xlim'] = (0, len(xaxis))
            if not 'ylim' in keywords:
                keywords['ylim'] = (0, 1)
        else:
            pass # custom

        if not 'legend' in keywords:
            keywords['legend'] = ['当月','平均']
        self.plot_data(**keywords)

    def _bar_color(self, category):
        color = []
        for i in range(len(category)):
            h, s, v = i*360/len(category), 0.99, 0.99
            r, g, b = hsv2rgb(h,s,v)
            rgb = '#' + hex(r)[2:].zfill(2) + hex(g)[2:].zfill(2) + hex(b)[2:].zfill(2)
            color.append(rgb)
        return color

    def _plot_style_I(self, xaxis, values):
        ##      BAR + [categories]
        ## ^                |
        ## |        |       |
        ## |    |   |   |   |   |
        ## -------------------------->
        ##      A   B   C   D   E
        width = 0.96
        color = self._bar_color(xaxis)
        for x, item in enumerate(values):
            self.ax.bar(x, values[item]['sum'][-1], width=width, label=xaxis[x], color=color[x])

    def _plot_style_II(self, xaxis, values):
        ##      BAR + hour/day/month + [categories]
        ## ^                         -A
        ## |                         -B
        ## |     |  |       ||
        ## |    ||  ||  ||  ||  ||
        ## -------------------------->
        ##      1   2   3   4   5
        width = pow(np.e, len(xaxis)/64)/2
        dw = width/len(self.category)
        color = self._bar_color(self.category)
        for x, _ in enumerate(xaxis):
            for i, item in enumerate(values):
                if not self.kind == 'month':
                    self.ax.bar(x+i*dw, values[item]['value'][x], width=dw, label=item, color=color[i])
                else:
                    self.ax.bar(x+i*dw, values[item]['sum'][-1], width=dw, label=item, color=color[i])

    def _plot_style_III(self, xaxis, values):
        ##      LINE + week/month/season/year + [categories]
        ## ^  _         ____________
        ## |_/ \      /              xN
        ## |    \____/
        ## -------------------------->
        ##  1 2 3 4 5 6 7 8 9 10 11 12
        linestyles = ['-','-.',':','--']
        markers = ['.',',','o','v','^','<','>','1','2','3','4','s','p','*','h','H','+','x','D','d','|','_']
        if self.CALC_MODE:
            for switch in ['value', 'sum']:
                self.ax.plot(
                    values[switch],
                    linestyle=linestyles[np.random.randint(len(linestyles))],
                    marker=markers[np.random.randint(len(markers))]
                    )
        else:
            for item in values:
                self.ax.plot(
                    values[item]['value'],
                    linestyle=linestyles[np.random.randint(len(linestyles))],
                    marker=markers[np.random.randint(len(markers))]
                    )
