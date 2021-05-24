#!/usr/local/bin/python3
# -*- coding:utf-8 -*-
import xlrd as rd
from datetime import datetime as dt
from queue import PriorityQueue as PQ

class AccountingBook:
    def __init__(self, filename='myMoney.xls'):
        """Initialization

        Args:
            filename (str, default='myMoney.xls'): Excel table file.

        Attributes:
            deals (list): See structure below.
            tree (dict): See structure below.
            accounts (dict): See structure below.
            init_time (datetime.datetime)
            update_time (datetime.datetime)

        Returns:
            None
        """
        self.filename = filename
        self.init_time = dt.now()
        self.update_time = dt(2012,3,4,5,6,7,8)
        self.deals = []
        deals = []
        '''Structrue
        self.deals = [
            {'交易类型':,'分类':,'子分类':,'账户1':,'账户2':,'金额':,'日期':,'成员':,'项目':,'商家':,'备注':},
            ...
            ]
        '''
        ### Get data ###
        workbook = rd.open_workbook(filename)
        self.titles = workbook.sheets()[0].row_values(0)
        for sheet in workbook.sheets():
            # sheet.nrows; sheet.ncols; sheet.row_values(n); sheet.col_values(n); sheet.name
            sign = -1 if sheet.name in ['支出','负债变更'] else 1
            for row in range(1, sheet.nrows):
                data = {}
                for i, title in enumerate(self.titles):
                    if title == '金额':
                        data[title] = sign*sheet.row_values(row)[i]
                    elif title == '日期':
                        try:
                            t = dt.strptime(sheet.row_values(row)[i], "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            t = dt.strptime(sheet.row_values(row)[i], "%Y-%m-%d %H:%M")
                        finally:
                            data[title] = t
                            if t < self.init_time:
                                self.init_time = t
                            if t > self.update_time:
                                self.update_time = t
                    elif title == '子分类':
                        if sheet.row_values(row)[i] == '饭卡/停用':
                            try:
                                t = dt.strptime(sheet.row_values(row)[6], "%Y-%m-%d %H:%M:%S")
                            except ValueError:
                                t = dt.strptime(sheet.row_values(row)[6], "%Y-%m-%d %H:%M")
                            data = {
                                '交易类型':'转账','分类':'','子分类':'',
                                '账户1':'饭卡','账户2':sheet.row_values(row)[3],
                                '金额':sheet.row_values(row)[5],'日期':t,
                                '成员':sheet.row_values(row)[7],
                                '项目':sheet.row_values(row)[8],
                                '商家':sheet.row_values(row)[9],
                                '备注':sheet.row_values(row)[10]
                                }
                            break
                        else:
                            data[title] = sheet.row_values(row)[i]
                    else:
                        data[title] = sheet.row_values(row)[i]
                deals.append(data)
            # END OF `for row in range(sheet.nrows):`
        # END OF `for sheet in workbook.sheets():`

        workbook = rd.open_workbook('fanka.xls')
        self.titles = workbook.sheets()[0].row_values(0)
        for sheet in workbook.sheets():
            # sheet.nrows; sheet.ncols; sheet.row_values(n); sheet.col_values(n); sheet.name
            if not sheet.name == '收入':
                sign = -1 if sheet.name in ['支出'] else 1
                for row in range(1, sheet.nrows):
                    data = {}
                    for i, title in enumerate(self.titles):
                        if title == '金额':
                            data[title] = sign*sheet.row_values(row)[i]
                        elif title == '日期':
                            try:
                                t = dt.strptime(sheet.row_values(row)[i], "%Y-%m-%d %H:%M:%S")
                            except ValueError:
                                t = dt.strptime(sheet.row_values(row)[i], "%Y-%m-%d %H:%M")
                            finally:
                                data[title] = t
                                if t < self.init_time:
                                    self.init_time = t
                                if t > self.update_time:
                                    self.update_time = t
                        elif title == '分类':
                            continue
                        elif title == '子分类':
                            # 吃饭 Liquid Solid 吃 用 ZJUWLAN 爱心捐赠 洗澡
                            if title in ['用']:
                                data['分类'] = '居家物业'
                                data['子分类'] = '日常物品'
                            elif title in ['洗澡']:
                                data['分类'] = '居家物业'
                                data['子分类'] = '水电煤气'
                            elif title in ['爱心捐赠']:
                                data['分类'] = '其他杂项'
                                data['子分类'] = '其他支出'
                            elif title in ['Liquid']:
                                data['分类'] = '食品酒水'
                                data['子分类'] = '饮料'
                            elif title in ['Solid', '吃']:
                                data['分类'] = '食品酒水'
                                data['子分类'] = '零食'
                            elif title in ['ZJUWLAN']:
                                data['分类'] = '交流通讯'
                                data['子分类'] = '上网费'
                            else: # 吃饭
                                data['分类'] = '食品酒水'
                                data['子分类'] = '吃饭'
                        else:
                            data[title] = sheet.row_values(row)[i]
                    deals.append(data)
            else: # if not sheet.name...
                for row in range(1, sheet.nrows):
                    try:
                        t = dt.strptime(sheet.row_values(row)[6], "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        t = dt.strptime(sheet.row_values(row)[6], "%Y-%m-%d %H:%M")
                    data = {
                        '交易类型':'转账','分类':'','子分类':'',
                        '账户1':'LOST','账户2':'饭卡',
                        '金额':sheet.row_values(row)[5],'日期':t,
                        '成员':sheet.row_values(row)[7],
                        '项目':sheet.row_values(row)[8],
                        '商家':sheet.row_values(row)[9],
                        '备注':sheet.row_values(row)[10]
                        }
                    deals.append(data)

        q = PQ()
        for deal in deals:
            q.put((deal['日期'],deal))
        while not q.empty():
            deal = q.get()[1]
            self.deals.append(deal)

    def _add_fanka_deals(self):
        pass

    @property
    def tree(self):
        """Set up an accounting tree like the one in previous version.
        ### Structure ###
        ##AccountingTree
        ##  支出 / 交易类型
        ##      Apple / 分类
        ##          Apple Store / 子分类
        ##              [{账户1:., 账户2:., 金额:., 日期:., 成员:., 项目:., 商家:., 备注:.}, ...]
        ##          Apple Music
        ##          ...
        """
        T = {}
        for deal in self.deals:
            # Create category
            if not deal['交易类型'] in T:
                T[deal['交易类型']] = {}
            if not deal['分类'] in T[deal['交易类型']]:
                T[deal['交易类型']][deal['分类']] = {}
            if not deal['子分类'] in T[deal['交易类型']][deal['分类']]:
                T[deal['交易类型']][deal['分类']][deal['子分类']] = []
            # Add data
            data = {}
            for i in range(3, len(self.titles)):
                data[self.titles[i]] = deal[self.titles[i]]
            T[deal['交易类型']][deal['分类']][deal['子分类']].append(data)
        return T

    @property
    def accounts(self):
        """Classify deals via accounts
        ### Structure ###
        ##Accounts
        ##    余额宝
        ##        [{'分类':., '子分类':., '金额':., '日期':., '成员':., '项目':., '商家':., '备注':.}, ...]
        ##    花呗
        ##    微信
        ##    ...
        """
        A = {}
        for deal in self.deals:
            # Create category
            if not deal['账户1'] in A:
                A[deal['账户1']] = []
            if (not deal['账户2'] in A) and (not deal['账户2'] == ''):
                A[deal['账户2']] = []
            # Add data
            data = {}
            for title in self.titles:
                if (title == '账户2') and (not deal['账户2'] == ''):
                    data['至'] = deal[title]
                elif title == '账户1':
                    pass
                else:
                    data[title] = deal[title]
            A[deal['账户1']].append(data)
        return A

    def __repr__(self):
        """Representation

        Args:
            self (账本): The current 账本 object.

        Returns:
            A string to represent the current 账本 instance.
        """
        return '账本 ' + self.filename + ' -- 最近更新时间 ' + str(self.update_time)
