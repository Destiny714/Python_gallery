# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/11/23 22:15
# @Author  : Destiny_
# @File    : data_write.py

import os
import time
import multi
import pandas
import data_read
import sql_action
import date_handler

today = date_handler.today()


def update_details():
    print('开始更新股票详情数据库……')
    start = time.time()
    update_count = 0
    insert_count = 0
    update_stocks = []
    insert_stocks = []
    sql = sql_action.SQL()
    stock_nos = sql.stock_Nos()
    sql.close()
    details = data_read.READ().read_excel(today)
    for detail in details:
        if detail['no'] in stock_nos:
            update_count += 1
            update_stocks.append(detail)
        else:
            insert_count += 1
            insert_stocks.append(detail)
    multi.update_all_detail(update_stocks)
    multi.insert_all_detail(insert_stocks)
    use = int(time.time() - start)
    print(f'股票详情数据库更新完毕,用时{use}秒')
    print(f'新增{insert_count}条股票')
    print(f'更新{update_count}条股票')


def create_tables():
    sql = sql_action.SQL()
    stock_nos = []
    stocks = sql.stock_Nos()
    exist_stocks = sql.tables()
    for stock in stocks:
        if stock not in exist_stocks:
            stock_nos.append(stock)
    for stock_no in stock_nos:
        print(f'create---{stock_no}')
        sql.create_single_stock_db(f'{stock_no}')
    sql.db.commit()
    sql.close()


def read_csv_folder_and_write():
    err = []
    err_stock = []
    sql = sql_action.SQL()
    route = './data'
    files = os.listdir(route)
    for file in files:
        if file.split('.')[1] == 'csv':
            print(f'main---{file.split(".")[0]}')
            try:
                csv = pandas.read_csv(f'{route}/{file}', encoding='GBK')
                if len(csv) != 0:
                    csv = csv.iloc[::-1]
                    for i in range(len(csv)):
                        _ = csv.iloc[i]
                        print(f'write---{file.split(".")[0]}---{_["日期"]}')
                        sql.insert_csv(f"{file.split('.')[0]}", _)
            except Exception as e:
                err.append(e)
                err_stock.append(file.split(".")[0])
    sql.db.commit()
    sql.close()
    print(f'err:{err_stock}')


def read_excel_and_write():
    start = time.time()
    print('开始更新今日行情数据……')
    multi.read_excel_and_write()
    use = int(time.time() - start)
    print(f'更新完毕,用时{use}秒')


def table_clear():
    sql = sql_action.SQL()
    tables = sql.tables()
    for table in tables:
        if table != 'stockDETAIL' and table != 'holiday':
            print(f'delete---{table}')
            sql.delete_table(f'No{table}')
    sql.db.commit()
    sql.close()


def delete_today():
    sql = sql_action.SQL()
    tables = sql.tables()
    datas = data_read.READ().excel_write_data(f'{today}.xlsx')
    for data in datas:
        if data['no'] in tables:
            r = sql.select(f'No{data["no"]}')
            for _ in r:
                date = _[1]
                if date == today:
                    print('delete')
                    sql.delete_record(data['no'], _[0])
    sql.db.commit()
    sql.close()
