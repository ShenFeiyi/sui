#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
from datetime import datetime as dt

from Analyse_v5 import Analyse
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
    print(ab)

    start = ab.init_time
    end = ab.update_time

    c1 = [
        '职业收入',
        '其他收入',
        '电子数码',
        '食品酒水',
        '学习进修',
        '衣服饰品',
        '居家物业',
        '行车交通',
        '网络通信',
        '休闲娱乐',
        '医院看病',
        '金融保险',
        '其他支出',
        ['支出','收入']
        ]
    A1 = Analyse(ab, 'bar', c1, start=start, end=end)
    A1.plot_data(legend=c1, show=False, title='style1')

    c2 = ['吃饭', '日常用品', '理发', '折旧', '打车', '租车']
    #A2 = Analyse(ab, 'bar', c2, 'month', start=start, end=end) # 需要至少一整年的数据
    #A2.plot_data(legend=c2, show=False, title='style2-month')
    A3 = Analyse(ab, 'bar', c2, 'day', start=start, end=end)
    A3.plot_data(legend=c2, show=False, title='style2-day')
    A4 = Analyse(ab, 'bar', c2, 'hour', start=start, end=end)
    A4.plot_data(legend=c2, show=False, title='style2-hour')

    c3 = [
        '职业收入',
        '食品酒水',
        '学习进修',
        '衣服饰品',
        '居家物业',
        '休闲娱乐',
        '金融保险',
        ['支出','收入']
        ]
    l3 = []
    for c in c3:
        if isinstance(c,str):
            l3.append(c)
        else:
            l3.append('结余')
    A5 = Analyse(ab, 'line', c3, 'year')
    A5.plot_data(legend=l3, show=False, title='style3-year')
    A6 = Analyse(ab, 'line', c3, 'season')
    A6.plot_data(legend=l3, show=False, title='style3-season')
    A7 = Analyse(ab, 'line', c3, 'month')
    A7.plot_data(legend=l3, show=False, title='style3-month')
    A8 = Analyse(ab, 'line', c3, 'week')
    A8.plot_data(legend=l3, show=False, title='style3-week')

    A = Analyse(ab, 'Engle', 'month', start=start)
    A.plot_calc_data(show=False)
