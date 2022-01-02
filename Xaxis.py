#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
import numpy as np
from datetime import datetime as dt, timedelta as delta

class Xaxis:
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
                    category (list *): [A, B], calculate A/B. * optional in some cases.
            kwarg (dict):
                start (datetime.datetime)
                end (datetime.datetime)
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

    @property
    def xaxis(self):
        """
        Returns:
            xaxis (numpy.ndarray): An array of xaxis labels.
        """
        if self.kind == 'bar':
            if self.interval is None:
                x = self._style_I()
            else:
                x = self._style_II()
        else:
            x = self._style_III()

        return x

    def _style_I(self):
        ##      BAR + [categories]
        ## ^                |
        ## |        |       |
        ## |    |   |   |   |   |
        ## -------------------------->
        ##      A   B   C   D   E
        x = np.array(self.category, dtype=object)
        return x

    def _style_II(self):
        ##      BAR + hour/day/month + [categories]
        ## ^                         -A
        ## |                         -B
        ## |     |  |       ||
        ## |    ||  ||  ||  ||  ||
        ## -------------------------->
        ##      1   2   3   4   5
        # internal functions
        def _hour():
            return [h for h in range(24)]
        def _day():
            return [d for d in range(1,32)]
        def _month():
            return [m for m in range(1,13)]
        # END of internal functions
        switch = {'hour':_hour, 'day':_day, 'month':_month}
        res = switch[self.interval]
        x = res()
        return np.array(x)

    def _style_III(self):
        ##      LINE + week/month/season/year + [categories]
        ## ^  _         ____________
        ## |_/ \      /              xN
        ## |    \____/
        ## -------------------------->
        ##  1 2 3 4 5 6 7 8 9 10 11 12
        # internal functions
        def _max_week_this_year(year):
            maxweek = 0
            for day in range(32-7, 32):
                time = dt(year, 12, day, 0, 0, 0)
                week = time.isocalendar()[1]
                if week > maxweek:
                    maxweek = week
            return maxweek

        def _month_2_season(month):
            return (month-1)//3 + 1

        def _week():
            x = []
            year, week, day = self.s_time.isocalendar()
            final_year, final_week, _ = self.e_time.isocalendar()
            while year*100+week <= final_year*100+final_week:
                x.append(str(year)+'-'+str(week).zfill(2))
                week += 1
                if week == _max_week_this_year(year)+1:
                    week = 1
                    year += 1
            return x

        def _month():
            x = []
            year, month = self.s_time.year, self.s_time.month
            final_year, final_month = self.e_time.year, self.e_time.month
            while year*100+month <= final_year*100+final_month:
                x.append(str(year)+'-'+str(month).zfill(2))
                month += 1
                if month == 13:
                    month = 1
                    year += 1
            return x

        def _season():
            x = []
            year, season = self.s_time.year, _month_2_season(self.s_time.month)
            final_year, final_season = self.e_time.year, _month_2_season(self.e_time.month)
            while year*100+season <= final_year*100+season:
                x.append(str(year)+'-'+str(season))
                season += 1
                if season == 5:
                    season = 1
                    year += 1
            return x

        def _year():
            x = []
            year = self.s_time.year
            final = self.e_time.year
            while year <= final:
                x.append(str(year))
                year += 1
            return x
        # END of internal functions
        switch = {'week':_week, 'month':_month, 'season':_season, 'year':_year}
        res = switch[self.interval]
        x = res()
        return np.array(x)
