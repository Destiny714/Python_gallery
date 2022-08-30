# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/11/24 13:36
# @Author  : Destiny_
# @File    : find_point.py
import talib
import pandas
import warnings
import numpy as np
import date_handler
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')


def get_point(x1, y1, x2, y2, paint=False, atol=0.005):
    ax = ''
    points = []
    fourth_x = [0]
    fourth_y = [0]
    similar_points = []
    if paint:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(x1, y1, color='lightblue', linewidth=3)
        ax.plot(x2, y2, color='darkgreen', marker='+')
    x_begin = max(x1[0], x2[0])
    x_end = min(x1[-1], x2[-1])
    points1 = [t for t in zip(x1, y1) if x_begin <= t[0] <= x_end]
    points2 = [t for t in zip(x2, y2) if x_begin <= t[0] <= x_end]
    idx = 0
    nrof_points = len(points1)
    while idx < nrof_points - 1:
        x3 = np.linspace(points1[idx][0], points1[idx + 1][0], 1000)
        y1_new = np.linspace(points1[idx][1], points1[idx + 1][1], 1000)
        y2_new = np.linspace(points2[idx][1], points2[idx + 1][1], 1000)
        tmp_idx = np.argwhere(np.isclose(y1_new, y2_new, atol=atol)).reshape(-1)
        if len(tmp_idx) > 0:
            if len(tmp_idx) == 1:
                # print([x3[tmp_idx][0], y2_new[tmp_idx][0]])
                # if y2_new[tmp_idx][0] >= 0:
                points.append([x3[tmp_idx][0], y2_new[tmp_idx][0]])
                if paint:
                    ax.plot(x3[tmp_idx], y2_new[tmp_idx], 'ro')
            else:
                # list_start = x3[[tmp_idx[0]]][0]
                # print(list_start,y2_new[tmp_idx[0]])
                # if y2_new[tmp_idx[0]] >= 0:
                #     points.append([x3[[tmp_idx[0]]][0],y2_new[tmp_idx[0]]])
                for _ in tmp_idx:
                    if abs(x3[[_]][0] - fourth_x[0]) <= 0.1 and abs(y2_new[[_]][0] - fourth_y[0]) <= 0.1:
                        # print([x3[_], y2_new[_]])
                        similar_points.append([x3[_], y2_new[_]])
                    else:
                        # if y2_new[[_]][0] >= 0:
                        # print([x3[[_]][0], y2_new[[_]][0]])
                        points.append([x3[[_]][0], y2_new[[_]][0]])
                        if paint:
                            ax.plot(x3[[_]], y2_new[[_]], 'ro')
                    fourth_x = x3[[_]]
                    fourth_y = y2_new[[_]]
        else:
            pass
        idx += 1
    if paint:
        plt.show()
    return points


def triangle(stock_detail:tuple,today):
    err = []
    avgs = {}
    dates = {}
    try:
        if len(stock_detail) >= 20:
            stock_data = pandas.DataFrame(stock_detail)
            mas = [5, 10, 20]
            for ma in mas:
                stock_data[f'ma{ma}'] = talib.MA(stock_data[3], timeperiod=ma)
            stock_data = stock_data[19:]
            for value in stock_data.values:
                data = {'date': value[1], 5: value[-3], 10: value[-2], 20: value[-1]}
                avgs[value[1]] = data
            for _i, __ in enumerate([_key for _key in avgs.keys()]):
                dates[_i] = avgs[__]['date']
            x = [index for index in range(len(dates))]
            five_y = [_data[5] for _data in [_value for _value in avgs.values()]]
            ten_y = [_data[10] for _data in [_value for _value in avgs.values()]]
            twenty_y = [_data[20] for _data in [_value for _value in avgs.values()]]
            result5_10 = get_point(x, five_y, x, ten_y, atol=five_y[-1] / 200)
            result5_20 = get_point(x, five_y, x, twenty_y, atol=twenty_y[-1] / 100)
            result10_20 = get_point(x, ten_y, x, twenty_y, atol=ten_y[-1] / 100)
            final5_10 = [_5_10 for _5_10 in result5_10 if
                         avgs[dates[int(_5_10[0])]][5] < avgs[dates[int(_5_10[0])]][10] and
                         avgs[dates[int(_5_10[0]) + 1]][
                             5] >
                         avgs[dates[int(_5_10[0]) + 1]][10]]
            final5_20 = [_5_20 for _5_20 in result5_20 if
                         avgs[dates[int(_5_20[0])]][5] < avgs[dates[int(_5_20[0])]][20] and
                         avgs[dates[int(_5_20[0]) + 1]][
                             5] >
                         avgs[dates[int(_5_20[0]) + 1]][20]]
            final10_20 = [_10_20 for _10_20 in result10_20 if
                          avgs[dates[int(_10_20[0])]][10] < avgs[dates[int(_10_20[0])]][20] and
                          avgs[dates[int(_10_20[0]) + 1]][
                              10] >
                          avgs[dates[int(_10_20[0]) + 1]][20]]
            if final5_10 and final5_20 and final10_20:
                if final5_10[-1][0] < final5_20[-1][0] < final10_20[-1][0]:
                    if dates[int(final10_20[-1][0]) + 1] in [date_handler.last_trade_day(today, i + 1) for i in range(10)]:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False
    except Exception as e:
        err.append(e)
        return False
