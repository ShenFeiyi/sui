#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
import xlwt as wt
import numpy as np
from datetime import datetime as dt

from AccountingBook import AccountingBook

class Organize:
    def __init__(self, accountingbook, *args):
        self.ab = accountingbook
        if len(args) > 0:
            self.s_time = max(self.ab.init_time, min(args))
            self.e_time = min(self.ab.update_time, max(args))
        else:
            self.s_time = self.ab.init_time
            self.e_time = self.ab.update_time

        self.wb = wt.Workbook(encoding='utf-8')
        self.sheets = {}
        for name in ['hour', 'day', 'week', 'month', 'season', 'year']:
            self.sheets[name] = self.wb.add_sheet(name, cell_overwrite_ok=True)

    def update(self):
        self.hour()
        self.day()
        self.week()
        self.month()
        self.season()
        self.year()

    def save(self, name='ready'):
        self.wb.save(name.split('.')[0]+'.xls')

    ### HOUR ###
    def hour(self):
        """
        class0 classI classII START 0 1 2 ... 23
               xxxxxx xxxxxxx START money data
                      xxxxxxx START money data
        """
        tree = self.ab.tree
        sheet = self.sheets['hour']
        hour_cols = {}
        for h in range(24):
            hour_cols[h] = None

        title = [((0,0),'zero'), ((0,1),'I'), ((0,2),'II'), ((0,3),'START')]
        for h in range(24):
            title.append(((0,4+h),h))
            hour_cols[h] = 4+h

        for item in title:
            (r, c), content = item
            sheet.write(r, c, content)

        newtree = {} # {zero:{I:{II:{hour:number}}}}; init a new tree by hour
        for zero in ['收入', '支出']:
            if not zero in newtree:
                newtree[zero] = {}
            for I in tree[zero]:
                if not I in newtree[zero]:
                    newtree[zero][I] = {}
                for II in tree[zero][I]:
                    if not II in newtree[zero][I]:
                        newtree[zero][I][II] = {}
                    for h in range(24):
                        newtree[zero][I][II][h] = 0

        for zero in ['收入', '支出']:
            for I in tree[zero]:
                for II in tree[zero][I]:
                    deals = tree[zero][I][II]
                    for deal in deals:
                        if self.s_time <= deal['日期'] <= self.e_time:
                            hour = deal['日期'].hour
                            newtree[zero][I][II][hour] += deal['金额']

        row = 1
        fill = []
        for zero in newtree:
            fill.append(((row, 0), zero))
            for I in newtree[zero]:
                fill.append(((row, 1), I))
                for II in newtree[zero][I]:
                    fill.append(((row, 2), II))
                    fill.append(((row, 3), 'START'))
                    for hour in newtree[zero][I][II]:
                        fill.append(((row, hour_cols[hour]), newtree[zero][I][II][hour]))
                    row += 1

        for item in fill:
            (r, c), content = item
            sheet.write(r, c, content)

        sheet.write(row+1, 0, 'END')

        self.sheets['hour'] = sheet

    ### DAY ###
    def day(self):
        """
        class0 classI classII START 1 2 3 ... 31
               xxxxxx xxxxxxx START money data
                      xxxxxxx START money data
        """
        tree = self.ab.tree
        sheet = self.sheets['day']
        day_cols = {}
        for d in range(1,32):
            day_cols[d] = None

        title = [((0,0),'zero'), ((0,1),'I'), ((0,2),'II'), ((0,3),'START')]
        for d in range(1,32):
            title.append(((0,3+d),d))
            day_cols[d] = 3+d

        for item in title:
            (r, c), content = item
            sheet.write(r, c, content)

        newtree = {} # {zero:{I:{II:{hour:number}}}}
        for zero in ['收入', '支出']:
            if not zero in newtree:
                newtree[zero] = {}
            for I in tree[zero]:
                if not I in newtree[zero]:
                    newtree[zero][I] = {}
                for II in tree[zero][I]:
                    if not II in newtree[zero][I]:
                        newtree[zero][I][II] = {}
                    for d in range(1,32):
                        newtree[zero][I][II][d] = 0

        for zero in ['收入', '支出']:
            for I in tree[zero]:
                for II in tree[zero][I]:
                    deals = tree[zero][I][II]
                    for deal in deals:
                        if self.s_time <= deal['日期'] <= self.e_time:
                            day = deal['日期'].day
                            newtree[zero][I][II][day] += deal['金额']

        row = 1
        fill = []
        for zero in newtree:
            fill.append(((row, 0), zero))
            for I in newtree[zero]:
                fill.append(((row, 1), I))
                for II in newtree[zero][I]:
                    fill.append(((row, 2), II))
                    fill.append(((row, 3), 'START'))
                    for day in newtree[zero][I][II]:
                        fill.append(((row, day_cols[day]), newtree[zero][I][II][day]))
                    row += 1

        for item in fill:
            (r, c), content = item
            sheet.write(r, c, content)

        sheet.write(row+1, 0, 'END')

        self.sheets['day'] = sheet

    ### WEEK ###
    def week(self):
        """
                                    2018       2019
        class0 classI classII START  n    n+1   1    2   3
               xxxxxx xxxxxxx START money data
                      xxxxxxx START money data
        """
        def _max_week_this_year(year):
            maxweek = 0
            for day in range(32-7, 32):
                time = dt(year, 12, day, 0, 0, 0)
                week = time.isocalendar()[1]
                if week > maxweek:
                    maxweek = week
            return maxweek

        tree = self.ab.tree
        sheet = self.sheets['week']
        start_date = self.s_time
        end_date = self.e_time
        date = [start_date.isocalendar()[0], start_date.isocalendar()[1]]
        # time.isocalendar() => year week day

        val_cols = {} # {2018:{week:n,...},2019:{1:n,...},...}
        title = [((1,0),'zero'), ((1,1),'I'), ((1,2),'II'), ((1,3),'START'), ((0,4),date[0])]
        col = 4
        while int(date[0]*100+date[1]) <= int(end_date.isocalendar()[0]*100+end_date.isocalendar()[1]):
            if not date[0] in val_cols:
                val_cols[date[0]] = {}
            if not date[1] in val_cols[date[0]]:
                val_cols[date[0]][date[1]] = col
            title.append(((1,col),date[1]))
            col += 1
            date[1] += 1
            if date[1] == _max_week_this_year(date[0])+1:
                date[1] = 1
                date[0] += 1
                title.append(((0,col),date[0]))

        for item in title:
            (r, c), content = item
            sheet.write(r, c, content)

        newtree = {} # {zero:{I:{II:{year-week:number}}}}
        for zero in ['收入', '支出']:
            if not zero in newtree:
                newtree[zero] = {}
            for I in tree[zero]:
                if not I in newtree[zero]:
                    newtree[zero][I] = {}
                for II in tree[zero][I]:
                    if not II in newtree[zero][I]:
                        newtree[zero][I][II] = {}
                    deals = tree[zero][I][II]
                    for deal in deals:
                        time = deal['日期']
                        if start_date <= time <= end_date:
                            if not str(time.isocalendar()[0])+'-'+str(time.isocalendar()[1]) in newtree[zero][I][II]:
                                newtree[zero][I][II][str(time.isocalendar()[0])+'-'+str(time.isocalendar()[1])] = deal['金额']
                            else:
                                newtree[zero][I][II][str(time.isocalendar()[0])+'-'+str(time.isocalendar()[1])] += deal['金额']

        row = 2
        fill = []
        for zero in newtree:
            fill.append(((row, 0), zero))
            for I in newtree[zero]:
                fill.append(((row, 1), I))
                for II in newtree[zero][I]:
                    fill.append(((row, 2), II))
                    fill.append(((row, 3), 'START'))
                    for yw in newtree[zero][I][II]:
                        year, week = yw.split('-')
                        year, week = int(year), int(week)
                        fill.append(((row, val_cols[year][week]), newtree[zero][I][II][yw]))
                    row += 1

        for item in fill:
            (r, c), content = item
            sheet.write(r, c, content)

        sheet.write(row+1, 0, 'END')

        self.sheets['week'] = sheet

    ### MONTH ###
    def month(self):
        """
                                    2018       2019
        class0 classI classII START  n    n+1   1    2   3
               xxxxxx xxxxxxx START money data
                      xxxxxxx START money data
        """
        tree = self.ab.tree
        sheet = self.sheets['month']
        start_date = self.s_time
        end_date = self.e_time
        date = [start_date.year, start_date.month]

        val_cols = {} # {2018:{11:n,12:n},2019:{1:n,...},...}
        title = [((1,0),'zero'), ((1,1),'I'), ((1,2),'II'), ((1,3),'START'), ((0,4),date[0])]
        col = 4
        while int(date[0]*100+date[1]) <= int(end_date.year*100+end_date.month):
            if not date[0] in val_cols:
                val_cols[date[0]] = {}
            if not date[1] in val_cols[date[0]]:
                val_cols[date[0]][date[1]] = col
            title.append(((1,col),date[1]))
            col += 1
            date[1] += 1
            if date[1] == 13:
                date[1] = 1
                date[0] += 1
                title.append(((0,col),date[0]))

        for item in title:
            position, content = item
            sheet.write(position[0], position[1], content)

        newtree = {} # {zero:{I:{II:{year-month:number}}}}
        for zero in ['收入', '支出']:
            if not zero in newtree:
                newtree[zero] = {}
            for I in tree[zero]:
                if not I in newtree[zero]:
                    newtree[zero][I] = {}
                for II in tree[zero][I]:
                    if not II in newtree[zero][I]:
                        newtree[zero][I][II] = {}
                    deals = tree[zero][I][II]
                    for deal in deals:
                        time = deal['日期']
                        if start_date <= time <= end_date:
                            if not str(time.year)+'-'+str(time.month) in newtree[zero][I][II]:
                                newtree[zero][I][II][str(time.year)+'-'+str(time.month)] = deal['金额']
                            else:
                                newtree[zero][I][II][str(time.year)+'-'+str(time.month)] += deal['金额']

        row = 2
        fill = []
        for zero in newtree:
            fill.append(((row, 0), zero))
            for I in newtree[zero]:
                fill.append(((row, 1), I))
                for II in newtree[zero][I]:
                    fill.append(((row, 2), II))
                    fill.append(((row, 3), 'START'))
                    for ym in newtree[zero][I][II]:
                        year, month = ym.split('-')
                        year, month = int(year), int(month)
                        fill.append(((row, val_cols[year][month]), newtree[zero][I][II][ym]))
                    row += 1

        for item in fill:
            position, content = item
            sheet.write(position[0], position[1], content)

        sheet.write(row+1, 0, 'END')

        self.sheets['month'] = sheet

    ### SEASON ###
    def season(self):
        """
                                    2018      2019
        class0 classI classII START  3    4    1    2   3
               xxxxxx xxxxxxx START money data
                      xxxxxxx START money data
        """
        def _month_2_season(month):
            return (month-1)//3 + 1

        tree = self.ab.tree
        sheet = self.sheets['season']
        start_date = self.s_time
        end_date = self.e_time
        date = [start_date.year, _month_2_season(start_date.month)]

        val_cols = {} # {2018:{season:n,...},2019:{1:n,...},...}
        title = [((1,0),'zero'), ((1,1),'I'), ((1,2),'II'), ((1,3),'START'), ((0,4),date[0])]
        col = 4
        while int(date[0]*100+date[1]) <= int(end_date.year*100+_month_2_season(end_date.month)):
            if not date[0] in val_cols:
                val_cols[date[0]] = {}
            if not date[1] in val_cols[date[0]]:
                val_cols[date[0]][date[1]] = col
            title.append(((1,col),date[1]))
            col += 1
            date[1] += 1
            if date[1] == 5:
                date[1] = 1
                date[0] += 1
                title.append(((0,col),date[0]))

        for item in title:
            (r, c), content = item
            sheet.write(r, c, content)

        newtree = {} # {zero:{I:{II:{year-season:number}}}}
        for zero in ['收入', '支出']:
            if not zero in newtree:
                newtree[zero] = {}
            for I in tree[zero]:
                if not I in newtree[zero]:
                    newtree[zero][I] = {}
                for II in tree[zero][I]:
                    if not II in newtree[zero][I]:
                        newtree[zero][I][II] = {}
                    deals = tree[zero][I][II]
                    for deal in deals:
                        time = deal['日期']
                        if start_date <= time <= end_date:
                            if not str(time.year)+'-'+str(_month_2_season(time.month)) in newtree[zero][I][II]:
                                newtree[zero][I][II][str(time.year)+'-'+str(_month_2_season(time.month))] = deal['金额']
                            else:
                                newtree[zero][I][II][str(time.year)+'-'+str(_month_2_season(time.month))] += deal['金额']

        row = 2
        fill = []
        for zero in newtree:
            fill.append(((row, 0), zero))
            for I in newtree[zero]:
                fill.append(((row, 1), I))
                for II in newtree[zero][I]:
                    fill.append(((row, 2), II))
                    fill.append(((row, 3), 'START'))
                    for ys in newtree[zero][I][II]:
                        year, season = ys.split('-')
                        year, season = int(year), int(season)
                        fill.append(((row, val_cols[year][season]), newtree[zero][I][II][ys]))
                    row += 1

        for item in fill:
            (r, c), content = item
            sheet.write(r, c, content)

        sheet.write(row+1, 0, 'END')

        self.sheets['season'] = sheet

    ### YEAR ###
    def year(self):
        """
        class0 classI classII START 2018 2019 2020 2021
               xxxxxx xxxxxxx START money data
                      xxxxxxx START money data
        """
        tree = self.ab.tree
        sheet = self.sheets['year']
        start_date = self.s_time
        end_date = self.e_time
        date = start_date.year

        val_cols = {} # {2018:n,2019:n,...}
        title = [((0,0),'zero'), ((0,1),'I'), ((0,2),'II'), ((0,3),'START')]
        col = 4
        while date <= end_date.year:
            if not date in val_cols:
                val_cols[date] = col
            title.append(((0,col),date))
            col += 1
            date += 1

        for item in title:
            (r, c), content = item
            sheet.write(r, c, content)

        newtree = {} # {zero:{I:{II:{year:number}}}}
        for zero in ['收入', '支出']:
            if not zero in newtree:
                newtree[zero] = {}
            for I in tree[zero]:
                if not I in newtree[zero]:
                    newtree[zero][I] = {}
                for II in tree[zero][I]:
                    if not II in newtree[zero][I]:
                        newtree[zero][I][II] = {}
                    deals = tree[zero][I][II]
                    for deal in deals:
                        time = deal['日期']
                        if start_date <= time <= end_date:
                            if not time.year in newtree[zero][I][II]:
                                newtree[zero][I][II][time.year] = deal['金额']
                            else:
                                newtree[zero][I][II][time.year] += deal['金额']

        row = 1
        fill = []
        for zero in newtree:
            fill.append(((row, 0), zero))
            for I in newtree[zero]:
                fill.append(((row, 1), I))
                for II in newtree[zero][I]:
                    fill.append(((row, 2), II))
                    fill.append(((row, 3), 'START'))
                    for year in newtree[zero][I][II]:
                        fill.append(((row, val_cols[year]), newtree[zero][I][II][year]))
                    row += 1

        for item in fill:
            (r, c), content = item
            sheet.write(r, c, content)

        sheet.write(row+1, 0, 'END')

        self.sheets['year'] = sheet

if __name__ == '__main__':
    AB = AccountingBook()
    order = Organize(AB)
    order.update()
    order.save()
