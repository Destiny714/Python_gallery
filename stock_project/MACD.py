# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/11/25 14:17
# @Author  : Destiny_
# @File    : MACD.py

import talib
import numpy
import data_read
import find_point
import date_handler
import matplotlib.pyplot as plt


# today = date_handler.today()
# yesterday = date_handler.yesterday()


def points(stock, today, paint=True):
    results = []
    r = data_read.READ().MACD_data(stock, today)
    dates = [_1['date'] for _1 in r]
    judge = [(_2['close']) for _2 in r]
    if '--' not in judge:
        closes = numpy.array([float(_2['close']) for _2 in r])
        MACD, MACDsignal, MACDhist = talib.MACD(closes, fastperiod=12, slowperiod=26, signalperiod=9)
        _MACD = [_0 for _0 in MACD if str(_0) != 'nan']
        _MACDsignal = [_1 for _1 in MACDsignal if str(_1) != 'nan']
        if len(_MACD) >= 2 and len(_MACDsignal) >= 2:
            max_macd = max(max(_MACD), max(_MACDsignal))
            min_macd = min(min(_MACD), min(_MACDsignal))
            diff = max_macd - min_macd
            atol = diff / 50
            bars = []
            for i, date in enumerate(dates):
                if str(MACDhist[i]) != 'nan':
                    new_map = {'date': date, 'bar': MACDhist[i], 'macd': MACD[i], 'signal': MACDsignal[i]}
                    bars.append(new_map)
            x = []
            y_bar = []
            y_macd = []
            y_signal = []
            date_map = {}
            for bar in bars:
                date_map[bar['date']] = bar
                x.append(bar['date'][5:])
                y_bar.append(bar['bar'])
                y_macd.append(bar['macd'])
                y_signal.append(bar['signal'])
            new_x = [i for i in range(len(x))]
            _points = find_point.get_point(new_x, y_macd, new_x, y_signal, paint=False, atol=atol)
            for point in _points:
                _x = int(point[0])
                date = bars[_x]['date']
                if date in [today, date_handler.to_yesterday(today)]:
                    last_date = date_handler.to_yesterday(date)
                    if date_map[last_date]['macd'] <= date_map[last_date]['signal']:
                        results.append(date)
            if results and paint:
                plt.figure(figsize=(20, 5))
                plt.bar(x, y_bar, align='center', color='b', alpha=0.6)
                plt.plot(x, y_macd)
                plt.plot(x, y_signal)
                plt.legend(['macd', 'macd_signal'])
                plt.title(label=f'{stock}')
                plt.show()
    return results
