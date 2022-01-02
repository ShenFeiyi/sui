#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
import xlrd as rd
import numpy as np
from datetime import timedelta as delta

class Values:
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
        self.filename = kwarg['name'] if 'name' in kwarg else 'v5.xls'

        self.length = 0 # data length
        self.switch = 'value' # value or sum

    @property
    def tree(self):
        data = rd.open_workbook(self.filename)
        sheets = data.sheets()
        for sheet in sheets:
            if sheet.name == self.interval:
                break

        T = {}
        ## ZERO ##
        zero = sheet.col_values(0)
        prev_item = None
        for row, item in enumerate(zero):
            if item in ['zero', '']:
                pass
            elif item == 'END':
                if prev_item in T:
                    T[prev_item]['r1'] = row - 1
            else:
                T[item] = {'r0':row}
                if prev_item in T:
                    T[prev_item]['r1'] = row - 1
                prev_item = item

        ## I ##
        I = sheet.col_values(1)
        prev_item = None
        for zero in T:
            for row, item in enumerate(I):
                if item in ['I', '']:
                    pass
                else:
                    if T[zero]['r0'] <= row <= T[zero]['r1']:
                        T[zero][item] = {'r0':row}
                        if prev_item in T[zero]:
                            T[zero][prev_item]['r1'] = row - 1
                        prev_item = item

        ## II ##
        II = sheet.col_values(2)
        for zero in T:
            R0 = T[zero]['r0']
            R1 = T[zero]['r1']
            for I in T[zero]:
                if isinstance(T[zero][I], int):
                    pass
                else:
                    RR0 = T[zero][I]['r0']
                    try:
                        RR1 = T[zero][I]['r1']
                    except KeyError:
                        RR1 = R1
                    for row, item in enumerate(II):
                        if RR0 <= row <= RR1:
                            if item in ['II', '']:
                                pass
                            else:
                                T[zero][I][item] = {'r':row}
                        else:
                            continue

        ## Values ##
        nrows = sheet.nrows
        ncols = sheet.ncols
        for zero in T:
            for I in T[zero]:
                if isinstance(T[zero][I], dict):
                    for II in T[zero][I]:
                        if isinstance(T[zero][I][II], dict):
                            values = sheet.row_values(T[zero][I][II]['r'])[4:]
                            T[zero][I][II]['value'] = [0 if v == '' else v for v in values]
                            T[zero][I][II]['sum'] = [sum(T[zero][I][II]['value'][:i+1]) for i in range(len(values))]
                            if len(values) > self.length:
                                self.length = len(values)

        ## O    I       II      item
        ##收入
        ##	r0
        ##	r1
        ##	职业收入
        ##		r0:1
        ##		r1:7
        ##		利息收入:{'r': 1, 'value': [], 'sum': []}
        ##		生活费:{'r': 2, 'value': [], 'sum': []}
        ##支出
        ##	r0
        ##	r1
        ##	其他杂项
        ##		r0:14
        ##		r1:15
        ##		多退少补:{'r': 14, 'value': [], 'sum': []}
        ##		其他支出:{'r': 15, 'value': [], 'sum': []}
        ##	食品酒水
        ##		r0:16
        ##		r1:20
        ##		吃饭:{'r': 16, 'value': [], 'sum': []}
        ##		奶茶:{'r': 17, 'value': [], 'sum': []}
        ##		零食:{'r': 18, 'value': [], 'sum': []}
        ##		饮料:{'r': 19, 'value': [], 'sum': []}
        ##		水果:{'r': 20, 'value': [], 'sum': []}

        return T

    @property
    def values(self):
        if not self.CALC_MODE:
            value = {} # {A:{value:nparray, sum:nparray}, ...}
            for name in self.category:
                if isinstance(name, str):
                    value[name] = {}
                    for switch in ['value', 'sum']:
                        self.switch = switch
                        val = self._find_name(name)
                        value[name][switch] = val
                else:
                    value[str(name)] = {}
                    for switch in ['value', 'sum']:
                        self.switch = switch
                        val = self._find_names(*name)
                        value[str(name)][switch] = val
        else:
            """支出 part only"""
##            value = {'invest':{},'non':{}} # {invest:{value:nparray, sum:nparray}, non-invest:{value, sum}}
            value = {} # {value:nparray, sum:nparray}

##            CateInvest = '定期投资'
##            val_invest = {}
##            for switch in ['value', 'sum']:
##                self.switch = switch
##                val = self._find_name(CateInvest)
##                val_invest[switch] = abs(val)

            CateA, CateB = self.category
            val_A, val_B = {}, {} # {value:nparray, sum:nparray}
            if isinstance(CateA, str):
                for switch in ['value', 'sum']:
                    self.switch = switch
                    val = self._find_name(CateA)
                    val_A[switch] = abs(val)
            else:
                for switch in ['value', 'sum']:
                    self.switch = switch
                    val = self._find_names(*CateA)
                    val_A[switch] = abs(val)
            if isinstance(CateB, str):
                for switch in ['value', 'sum']:
                    self.switch = switch
                    val = self._find_name(CateB)
                    val_B[switch] = abs(val)
            else:
                for switch in ['value', 'sum']:
                    self.switch = switch
                    val = self._find_names(*CateB)
                    val_B[switch] = abs(val)

            for switch in ['value', 'sum']:
##                value['invest'][switch] = val_A[switch] / val_B[switch]
##                value['non'][switch] = val_A[switch] / (val_B[switch]-val_invest[switch])
                value[switch] = val_A[switch] / val_B[switch]

            # show data sheet
            # value = {
            #     value:nparray, sum:nparray
            #     }
            data = rd.open_workbook(self.filename)
            sheets = data.sheets()
            for sheet in sheets:
                if sheet.name == self.interval:
                    break

            if self.interval == 'year':
                row0 = sheet.row_values(0)
                title = [y for y in row0 if not y in ['zero', 'I', 'II', 'START', '']]
            else:
                title = []
                row0 = sheet.row_values(0)
                row1 = sheet.row_values(1)
                for col in range(len(row1)):
                    if not row0[col] == '':
                        year = row0[col]
                    if not row1[col] in ['zero', 'I', 'II', 'START', '']:
                        interval = row1[col]
                    try:
                        title.append(str(int(year))+'-'+str(int(interval)).zfill(2))
                    except NameError:
                        continue
            title.reverse()

            cols = np.zeros((len(title),2), dtype='float64')
            for i in range(len(title)):
##                cols[len(title)-i-1][:] = value['invest']['value'][i], value['non']['value'][i], value['invest']['sum'][i], value['non']['sum'][i]
                cols[len(title)-i-1][:] = value['value'][i], value['sum'][i]

##            print('\t\t投资\t\t无投资\t\t\t 平均')
            print('\t\t  每月\t\t  平均')
            for i in range(len(title)):
                print(title[i], end='\t\t')
                if int(1e4*cols[i][0]) == int(1e4*cols[i][1]):
                    print('', end='\t\t')
                else:
                    print('{:6.2f}%'.format(1e2*cols[i][0]), end='\t\t')
##                print('{:5.2f}%'.format(1e2*cols[i][1]), end='\t\t')
                print('{:6.2f}%'.format(1e2*cols[i][1]))
##                if int(1e4*cols[i][2]) == int(1e4*cols[i][3]):
##                    print('', end='\t\t')
##                else:
##                    print('{:5.2f}%'.format(1e2*cols[i][2]), end='\t\t')
##                print('{:5.2f}%'.format(1e2*cols[i][3]))
            # END show data sheet

        return value

    def _add_class_O(self, O):
        val = np.zeros(self.length, dtype='float64')
        for I in self.tree[O]:
            if isinstance(self.tree[O][I], dict):
                val += self._add_class_I(O, I)
        return val

    def _add_class_I(self, O, I):
        val = np.zeros(self.length, dtype='float64')
        for II in self.tree[O][I]:
            if isinstance(self.tree[O][I][II], dict):
                val += self._add_class_II(O, I, II)
        return val

    def _add_class_II(self, O, I, II):
        val = np.array(self.tree[O][I][II][self.switch], dtype='float64')
        return val

    def _find_name(self, name):
        F = False
        for O in self.tree:
            if O == name:
                val = self._add_class_O(O)
                F = True
            if F:
                break
            for I in self.tree[O]:
                if I == name:
                    val = self._add_class_I(O, I)
                    F = True
                if F:
                    break
                if isinstance(self.tree[O][I], dict):
                    for II in self.tree[O][I]:
                        if II == name:
                            val = self._add_class_II(O, I, II)
                            F = True
                        if F:
                            break
        return val if 'val' in locals() else np.zeros(self.length)

    def _find_names(self, *names):
        val = self._find_name(names[0])
        for name in names[1:]:
            val += self._find_name(name)
        return val

if __name__ == '__main__':
    data = rd.open_workbook('ready.xls')
    sheets = data.sheets()
    for sheet in sheets:
        if sheet.name == 'hour':
            break

    """
    ...
    """

##    for zero in T:
##        print(f'{zero}')
##        for I in T[zero]:
##            print(f'\t{I}')
##            if isinstance(T[zero][I], str) or isinstance(T[zero][I], int):
##                pass
##            else:
##                for II in T[zero][I]:
##                    print(f'\t\t{II}:{T[zero][I][II]}')
