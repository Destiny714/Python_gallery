# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/11/23 22:15
# @Author  : Destiny_
# @File    : sql_action.py

from operator import le
from re import T
from turtle import st
import pymysql


class SQL:
    def __init__(self):
        self.__account = ''
        self.__pswd = ''
        self.__DB = ''
        self.host = ''
        self.db = pymysql.connect(host=self.host, port=3306, user=self.__account, password=self.__pswd,
                                  database=self.__DB,connect_timeout=60)
        self.cursor = self.db.cursor()
        self.word = ''

    def close(self):
        self.cursor.close()
        self.db.close()

    def action(self, output: bool):
        self.cursor.execute(self.word)
        if output:
            callback = self.cursor.fetchall()
            return callback
        else:
            self.db.commit()

    def select(self, table):
        self.word = f'SELECT * FROM {table}'
        result = self.action(output=True)
        return result

    def select_stock(self, stock):
        self.word = f"SELECT * FROM stockDETAIL WHERE no='{stock}'"
        result = self.action(output=True)[0]
        name = result[2]
        category = result[3]
        result = {'name': name, 'category': category}
        return result

    def create_single_stock_db(self, table):
        self.word = f'CREATE TABLE No{table}(No INT NOT NULL primary key auto_increment,date varchar(255)not null,open varchar(255) not null,close varchar(255) not null, high varchar(255) not null,low varchar(255) not null, volume varchar(255) not null,value varchar(255) not null,ma5 varchar(255) not null default "0",ma10 varchar(255) not null default "0",ma20 varchar(255) not null default "0")'
        self.action(output=False)

    def tables(self):
        results = []
        self.word = 'SHOW TABLES'
        result = self.action(output=True)
        for _ in result:
            if _[0] != 'stockDETAIL' and _[0] != 'holiday':
                results.append(str(_[0]).replace('No', ''))
        return results

    def insert(self, stock, data):
        self.word = f"INSERT INTO No{stock} (date,open,close,high,low,volume,value) VALUES ('{data['date']}','{data['open']}','{data['close']}','{data['high']}','{data['low']}','{data['volume']}','0')"
        self.action(output=False)

    def insert_csv(self, table, data):
        self.word = f"INSERT INTO No{table} (date,open,close,high,low,volume,value) VALUES ('{data['日期']}','{data['开盘价']}','{data['收盘价']}','{data['最高价']}','{data['最低价']}','{data['成交量']}','{data['总市值']}')"
        self.action(output=False)

    def delete_table(self, table):
        self.word = f"DROP TABLE IF EXISTS {table}"
        self.action(output=False)

    def update_detail(self, data):
        self.word = f"UPDATE stockDETAIL SET category='{data['category']}',name='{data['name']}' WHERE no={data['no']}"
        self.action(output=False)

    def insert_detail(self, data):
        self.word = f"INSERT INTO stockDETAIL (no, name, category, downloadno) VALUES ('{data['no']}','{data['name']}','{data['category']}','{data['downloadNo']}')"
        self.action(output=False)

    def insert_stock_data_from_excel(self, data: dict):
        self.word = f"INSERT INTO No{data['no']} (date,open,close,high,low,volume,value) VALUES ('{data['date']}','{data['open']}','{data['close']}','{data['high']}','{data['low']}','{data['volume']}','{data['value']}')"
        self.action(output=False)

    def update_stock_data_from_excel(self, data: dict):
        self.word = f"UPDATE No{data['no']} SET open='{data['open']}',close='{data['close']}',high='{data['high']}',low='{data['low']}',volume='{data['volume']}',value='{data['value']}' WHERE  date='{data['date']}'"
        self.action(output=False)

    def delete_record(self, stock, no):
        self.word = f"DELETE FROM No{stock} WHERE No={no}"
        self.action(output=False)

    def stock_Nos(self):
        stocks = []
        self.word = f"SELECT no FROM stockDETAIL"
        results = self.action(output=True)
        for result in results:
            stocks.append(result[0])
        return stocks

    def download_nos(self):
        Nos = []
        self.word = f"SELECT downloadNo FROM stockDETAIL"
        results = self.action(output=True)
        for result in results:
            Nos.append(result[0])
        return Nos

    def select_id_by_date(self, some_day, no):
        self.word = f"SELECT No FROM No{no} WHERE date='{some_day}'"

        result = self.action(output=True)
        if result:
            result = result[0][0]
            return result

    def select_by_id_range_before(self, _id, no):
        self.word = f"SELECT * FROM No{no} WHERE No <= {_id}"
        result = self.action(output=True)
        return result

    def select_by_id_range_after(self, _id, no):
        self.word = f"SELECT * FROM No{no} WHERE No >= {_id}"
        result = self.action(output=True)
        return result

    def select_yesterday_close_price(self, yesterday, no):
        self.word = f"SELECT close FROM No{no} WHERE date = '{yesterday}'"
        result = float(self.action(output=True)[0][0])
        return result

    def select_by_date(self, stock, date):
        self.word = f"SELECT * FROM No{stock} WHERE date='{date}'"
        result = self.action(output=True)
        return result

    def holidays(self):
        self.word = f"SELECT holiday FROM holiday"
        result = self.action(output=True)
        holidays = [_[0] for _ in result]
        return holidays

    def select_close_by_date(self, stock, date):
        self.word = f"SELECT close FROM No{stock} WHERE date='{date}'"
        result = self.action(output=True)[0][0]
        return result

    def add_column(self,stock):
        self.word = f"ALTER TABLE No{stock} ADD ma5 VARCHAR(255) NOT NULL DEFAULT '0',ADD ma10 VARCHAR(255) NOT NULL DEFAULT '0',ADD ma20 VARCHAR(255) NOT NULL DEFAULT '0'"
        self.action(output=False)

    def select_single(self,stock):
        self.word = f"SELECT No FROM No{stock}"
        result = self.action(output=True)
        return len(result)

    def update_ma(self,stock,data):
        self.word = f"UPDATE No{stock} SET ma5='{str(data['ma5'])[:7]}',ma10='{str(data['ma10'])[:7]}',ma20='{str(data['ma20'])[:7]}' WHERE date='{data[1]}'"
        self.action(output=False)

    def select_stock_name(self,stock):
        self.word = f"SELECT name FROM stockDETAIL WHERE no='{stock}'"
        result = self.action(output=True)
        return result[0][0]
