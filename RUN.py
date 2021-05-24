#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
from datetime import datetime as dt

from Analyse_v4 import Analyse
from AccountingBook import AccountingBook as AB

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

if __name__ == '__main__':
    ab = AB()

    # pass
    #A = Analyse(ab, 'bar', ['支出','收入',['支出','收入']])
    #A.plot_data(legend=['支出','收入','+'])
    #A = Analyse(ab, 'bar', ['食品酒水','支出','收入',['支出','收入']])
    #A.plot_data(legend=['食品酒水','支出','收入','+'])
    #A = Analyse(ab, 'bar', ['食品酒水','居家物业',['医疗保健','休闲娱乐'],'职业收入'])
    #A.plot_data(legend=['A','B','C','D'])

    # Pass
    #A = Analyse(ab, 'bar', ['食品酒水','居家物业',['医疗保健','休闲娱乐'],'职业收入'], 'month')
    #A.plot_data(legend=['A','B','C','D'])
    #A = Analyse(ab, 'bar', ['食品酒水','居家物业',['医疗保健','休闲娱乐']], 'hour')
    #A.plot_data(legend=['A','B','C'])
    #A = Analyse(ab, 'bar', ['食品酒水','居家物业',['医疗保健','休闲娱乐']], 'day')
    #A.plot_data(legend=['A','B','C'])

    # PASS
    #A = Analyse(ab, 'line', ['食品酒水','居家物业',['医疗保健','休闲娱乐'],'职业收入'], 'year')
    #A.plot_data(legend=['A','B','C','D'])
    #A = Analyse(ab, 'line', ['食品酒水','居家物业',['医疗保健','休闲娱乐'],'职业收入'], 'season')
    #A.plot_data(legend=['A','B','C','D'])
    #A = Analyse(ab, 'line', ['食品酒水','居家物业',['医疗保健','休闲娱乐'],'职业收入'], 'month')
    #A.plot_data(legend=['A','B','C','D'])
    #A = Analyse(ab, 'line', ['食品酒水','居家物业',['医疗保健','休闲娱乐'],'职业收入'], 'week')
    #A.plot_data(legend=['A','B','C','D'])

    c1 = [
        '职业收入',
        '其他收入',
        'Apple',
        '食品酒水',
        '学习进修',
        '衣服饰品',
        '居家物业',
        '行车交通',
        '交流通讯',
        '休闲娱乐',
        '市民卡',
        '人情往来',
        '医疗保健',
        '金融保险',
        '其他杂项',
        ['支出','收入']
        ]
    A1 = Analyse(ab, 'bar', c1, start=dt(2019,1,1,0,0,0), end=dt(2021,1,1,0,0,0))
    A1.plot_data(legend=c1, show=False, title='style1')

    c2 = ['吃饭', '奶茶', '日常用品', '理发', '洗衣房', '打车租车']
    A2 = Analyse(ab, 'bar', c2, 'month', start=dt(2019,1,1,0,0,0), end=dt(2021,1,1,0,0,0))
    A2.plot_data(legend=c2, show=False, title='style2-month')
    A3 = Analyse(ab, 'bar', c2, 'day', start=dt(2019,1,1,0,0,0), end=dt(2021,1,1,0,0,0))
    A3.plot_data(legend=c2, show=False, title='style2-day')
    A4 = Analyse(ab, 'bar', c2, 'hour', start=dt(2019,1,1,0,0,0), end=dt(2021,1,1,0,0,0))
    A4.plot_data(legend=c2, show=False, title='style2-hour')

    c3 = c1
    A5 = Analyse(ab, 'line', c3, 'year')
    A5.plot_data(legend=c3, show=False, title='style3-year')
    A6 = Analyse(ab, 'line', c3, 'season')
    A6.plot_data(legend=c3, show=False, title='style3-season')
    A7 = Analyse(ab, 'line', c3, 'month')
    A7.plot_data(legend=c3, show=False, title='style3-month')
    A8 = Analyse(ab, 'line', c3, 'week')
    A8.plot_data(legend=c3, show=False, title='style3-week')

    A = Analyse(ab, 'Engle', 'month', start=dt(2018,11,1,0,0,0))
    A.plot_calc_data(show=False)
