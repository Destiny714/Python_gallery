# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/11/21 19:49
# @Author  : Destiny_
# @File    : data_read.py

import xlrd
import pandas
import sql_action


class READ:
    def __init__(self):
        self.file = '/Users/destiny/Desktop/MyCode/Python/stock_project/'

    def check_excel_format(self, route):
        result = True
        workbook = xlrd.open_workbook(filename=f'{self.file}excel/{route}')
        sheet = workbook.sheet_by_index(0)
        index = sheet.row_values(0)
        check_list = ['代码', '现价', '总手', '总市值', '开盘', '最高', '最低']
        for i, v in enumerate([1, 5, 9, 16, 33, 35, 36]):
            if index[v] != check_list[i]:
                result = False
        return result

    def excel_write_data(self, route: str):
        datas = []
        workbook = xlrd.open_workbook(filename=f'{self.file}excel/{route}')
        sheet = workbook.sheet_by_index(0)
        nos = sheet.col_values(1)[1:]
        opens = sheet.col_values(33)[1:]
        closes = sheet.col_values(5)[1:]
        highs = sheet.col_values(35)[1:]
        lows = sheet.col_values(36)[1:]
        volumes = sheet.col_values(9)[1:]
        values = sheet.col_values(16)[1:]
        for i, no in enumerate(nos):
            single_map = {'no': no[2:], 'open': opens[i], 'close': closes[i], 'high': highs[i], 'low': lows[
                i], 'volume': volumes[i], 'value': values[i], 'date': route.split('.')[0]}
            datas.append(single_map)
        return datas

    def MACD_data(self, stock, today):
        data = []
        sql = sql_action.SQL()
        self.file = '/Users/destiny/Desktop/PycharmProject/stock_project'
        _id = sql.select_id_by_date(today,stock)
        r = sql.select_by_id_range_before(_id,stock)
        r = pandas.DataFrame(r)
        closes = r[3].values
        dates = r[1].values
        for i, date in enumerate(dates):
            new_map = {'date': date, 'close': closes[i]}
            data.append(new_map)
        return data

    def read_excel(self, route):
        stockList = []
        workbook = xlrd.open_workbook(filename=f'{self.file}excel/{route}.xlsx')
        sheet = workbook.sheet_by_index(0)
        stockNos = sheet.col_values(1)[1:]
        stockNames = sheet.col_values(2)[1:]
        stockCategory = sheet.col_values(21)[1:]
        for index, value in enumerate(stockNos):
            marketNo = 0 if value[0:2] == 'SH' else 1
            stockMap = {'no': value[2:], 'name': stockNames[index], 'category': stockCategory[
                index], 'downloadNo': f'{marketNo}{value[2:]}'}
            stockList.append(stockMap)
        return stockList

    def read_csv(self, route):
        self.file = route
        csv = pandas.read_csv(self.file, encoding='GBK').set_index('日期').iloc[::-1]
        return csv
