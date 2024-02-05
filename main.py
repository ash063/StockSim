import pandas as pd
import numpy as np
import random
from ui_MainWindow import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import pyqtSlot, Qt, QDateTime
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtChart import QChart, QLineSeries, QValueAxis, QCandlestickSet, QCandlestickSeries, QBarSeries, QStackedBarSeries, QBarSet, QBarCategoryAxis, QDateTimeAxis, QScatterSeries
import sys
import os
import datetime

class QmyMainWindow(QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setAutoFillBackground(True)
        self.setCentralWidget(self.ui.splitter)
        self.codeLst, self.cfg, self.codeDic = self.__loadConfig()
        self.__initState()
        self.barLst = [str(i) for i in range(1, self.cfg['显示长度'] + 1)]
        self.__createChart()
        self.ind, self.data, self.length, self.name = self.__loadData()
        # self.length = len(self.data)
        self.__plot()
        self.updateInfo()

    def __loadConfig(self):
        dic = {}
        with open('config\\cfg.txt', 'r', encoding = 'utf-8') as f:
            for line in f.readlines():
                k, v = line.split(',')
                dic[k] = int(v)
        codeLst = os.listdir('data')
        codeData = pd.read_csv('config\\code.csv')
        codeDic = {f'{codeData["code"][i]:06}': codeData['name'][i] for i in range(len(codeData))}
        return codeLst, dic, codeDic
    
    def __initState(self):
        self.state = {
            '可用资金': self.cfg['初始资金'], 
            '持仓成本': 0, 
            '当前盈亏': 0, 
            '持仓资金': 0, 
            '持仓数': 0, 
            '当前天数': 1, 
        }
    
    def __createChart(self):
        self.__chartDic = {
            'day': {
                'k': QChart(), 
                'vol': QChart(), 
                'kdj': QChart(), 
                'macd': QChart(), 
                'atr': QChart()
            }, 
            'week': {
                'k': QChart(), 
                'vol': QChart(), 
                'kdj': QChart(), 
                'macd': QChart(), 
                'atr': QChart()
            }, 
            'month': {
                'k': QChart(), 
                'vol': QChart(), 
                'kdj': QChart(), 
                'macd': QChart(), 
                'atr': QChart()
            }
        }
        x_min = QDateTime.fromString("1978-12-18","yyyy-MM-dd")
        x_max = x_min.addDays(self.cfg['显示长度'])
        # 日趋势 + 均线
        # self.__chartDic['day']['k'].setTitle('趋势线')
        self.ui.chartView_day1.setChart(self.__chartDic['day']['k'])
        self.ui.chartView_day1.setRenderHint(QPainter.Antialiasing)
        self.__chartDic['day']['k'].setTheme(QChart.ChartTheme(2))
        series_day1_1 = QCandlestickSeries()
        series_day1_1.setName('蜡烛图')
        series_day1_1.setIncreasingColor(Qt.red)
        series_day1_1.setDecreasingColor(Qt.darkGreen)
        series_day1_2 = QLineSeries()
        series_day1_2.setName('MA5')
        pen_day1_2 = QPen(Qt.white)
        pen_day1_2.setStyle(Qt.SolidLine)
        pen_day1_2.setWidth(.5)
        series_day1_2.setPen(pen_day1_2)
        series_day1_3 = QLineSeries()
        series_day1_3.setName('MA10')
        pen_day1_3 = QPen(Qt.yellow)
        pen_day1_3.setStyle(Qt.SolidLine)
        pen_day1_3.setWidth(.5)
        series_day1_3.setPen(pen_day1_3)
        series_day1_4 = QLineSeries()
        series_day1_4.setName('MA20')
        pen_day1_4 = QPen(QColor('#4ebdf2'))
        pen_day1_4.setStyle(Qt.SolidLine)
        pen_day1_4.setWidth(.5)
        series_day1_4.setPen(pen_day1_4)
        series_day1_5 = QScatterSeries()
        series_day1_5.setName('BuyPoint')
        series_day1_5.setColor(QColor('#00d6ff'))
        series_day1_5.setMarkerShape(QScatterSeries.MarkerShapeCircle)
        series_day1_5.setMarkerSize(10)
        series_day1_6 = QScatterSeries()
        series_day1_6.setName('SellPoint')
        series_day1_6.setColor(QColor('#e3ff00'))
        series_day1_6.setMarkerShape(QScatterSeries.MarkerShapeCircle)
        series_day1_6.setMarkerSize(10)
        self.__chartDic['day']['k'].addSeries(series_day1_1)
        self.__chartDic['day']['k'].addSeries(series_day1_2)
        self.__chartDic['day']['k'].addSeries(series_day1_3)
        self.__chartDic['day']['k'].addSeries(series_day1_4)
        self.__chartDic['day']['k'].addSeries(series_day1_5)
        self.__chartDic['day']['k'].addSeries(series_day1_6)
        axisX_day1 = QDateTimeAxis()
        axisY_day1 = QValueAxis()
        axisX_day1.setFormat('yyyy-MM-dd')
        axisX_day1.setTickCount(10)
        axisX_day1.setMin(x_min)
        axisX_day1.setMax(x_max)
        axisY_day1.setRange(0, 100)
        axisY_day1.setLabelFormat('%.2f')
        axisY_day1.setTickCount(5)
        axisY_day1.setGridLineVisible(True)
        axisY_day1.setMinorGridLineVisible(False)
        self.__chartDic['day']['k'].addAxis(axisX_day1, Qt.AlignBottom)
        self.__chartDic['day']['k'].addAxis(axisY_day1, Qt.AlignLeft)
        series_day1_1.attachAxis(axisX_day1)
        series_day1_1.attachAxis(axisY_day1)
        series_day1_2.attachAxis(axisX_day1)
        series_day1_2.attachAxis(axisY_day1)
        series_day1_3.attachAxis(axisX_day1)
        series_day1_3.attachAxis(axisY_day1)
        series_day1_4.attachAxis(axisX_day1)
        series_day1_4.attachAxis(axisY_day1)
        series_day1_5.attachAxis(axisX_day1)
        series_day1_5.attachAxis(axisY_day1)
        series_day1_6.attachAxis(axisX_day1)
        series_day1_6.attachAxis(axisY_day1)
        self.__chartDic['day']['k'].legend().markers()[0].setVisible(False)
        # 日成交量
        self.ui.chartView_day2.setChart(self.__chartDic['day']['vol'])
        self.ui.chartView_day2.setRenderHint(QPainter.Antialiasing)
        self.__chartDic['day']['vol'].setTheme(QChart.ChartTheme(2))
        series_day2 = QStackedBarSeries()
        setUp = QBarSet('涨')
        setUp.setColor(Qt.red)
        setDown = QBarSet('跌')
        setDown.setColor(Qt.darkGreen)
        series_day2.append(setUp)
        series_day2.append(setDown)
        self.__chartDic['day']['vol'].addSeries(series_day2)
        axisX_day2_1 = QDateTimeAxis()
        axisX_day2_2 = QBarCategoryAxis()
        axisY_day2 = QValueAxis()
        axisX_day2_1.setFormat('yyyy-MM-dd')
        axisX_day2_1.setTickCount(10)
        axisX_day2_1.setMin(x_min)
        axisX_day2_1.setMax(x_max)
        axisX_day2_2.append(self.barLst)
        axisX_day2_2.setRange(self.barLst[0], self.barLst[-1])
        axisX_day2_2.setVisible(False)
        axisY_day2.setRange(0, 100)
        axisY_day2.setLabelFormat('%d')
        axisY_day2.setTickCount(5)
        axisY_day2.setGridLineVisible(True)
        axisY_day2.setMinorGridLineVisible(False)
        self.__chartDic['day']['vol'].addAxis(axisX_day2_1, Qt.AlignBottom)
        self.__chartDic['day']['vol'].addAxis(axisX_day2_2, Qt.AlignBottom)
        self.__chartDic['day']['vol'].addAxis(axisY_day2, Qt.AlignLeft)
        self.__chartDic['day']['vol'].setAxisX(axisX_day2_2, series_day2)
        self.__chartDic['day']['vol'].setAxisY(axisY_day2, series_day2)
        self.__chartDic['day']['vol'].legend().hide()
        # 日kdj
        self.__chartDic['day']['kdj'].setTitle('KDJ')
        self.ui.chartView_day3.setChart(self.__chartDic['day']['kdj'])
        self.ui.chartView_day3.setRenderHint(QPainter.Antialiasing)
        self.__chartDic['day']['kdj'].setTheme(QChart.ChartTheme(2))
        series_day3_1 = QLineSeries()
        series_day3_1.setName('K')
        pen_day3_1 = QPen(Qt.white)
        pen_day3_1.setStyle(Qt.SolidLine)
        pen_day3_1.setWidth(.5)
        series_day3_1.setPen(pen_day3_1)
        series_day3_2 = QLineSeries()
        series_day3_2.setName('D')
        pen_day3_2 = QPen(Qt.yellow)
        pen_day3_2.setStyle(Qt.SolidLine)
        pen_day3_2.setWidth(.5)
        series_day3_2.setPen(pen_day3_2)
        series_day3_3 = QLineSeries()
        series_day3_3.setName('J')
        pen_day3_3 = QPen(Qt.red)
        pen_day3_3.setStyle(Qt.SolidLine)
        pen_day3_3.setWidth(.5)
        series_day3_3.setPen(pen_day3_3)
        self.__chartDic['day']['kdj'].addSeries(series_day3_1)
        self.__chartDic['day']['kdj'].addSeries(series_day3_2)
        self.__chartDic['day']['kdj'].addSeries(series_day3_3)
        axisX_day3 = QDateTimeAxis()
        axisY_day3 = QValueAxis()
        axisX_day3.setFormat('yyyy-MM-dd')
        axisX_day3.setTickCount(10)
        axisX_day3.setMin(x_min)
        axisX_day3.setMax(x_max)
        axisY_day3.setRange(-20, 120)
        axisY_day3.setLabelFormat('%.2f')
        axisY_day3.setTickCount(5)
        axisY_day3.setGridLineVisible(True)
        axisY_day3.setMinorGridLineVisible(False)
        self.__chartDic['day']['kdj'].addAxis(axisX_day3, Qt.AlignBottom)
        self.__chartDic['day']['kdj'].addAxis(axisY_day3, Qt.AlignLeft)
        series_day3_1.attachAxis(axisX_day3)
        series_day3_1.attachAxis(axisY_day3)
        series_day3_2.attachAxis(axisX_day3)
        series_day3_2.attachAxis(axisY_day3)
        series_day3_3.attachAxis(axisX_day3)
        series_day3_3.attachAxis(axisY_day3)
        # 日macd
        self.__chartDic['day']['macd'].setTitle('MACD')
        self.ui.chartView_day4.setChart(self.__chartDic['day']['macd'])
        self.ui.chartView_day4.setRenderHint(QPainter.Antialiasing)
        self.__chartDic['day']['macd'].setTheme(QChart.ChartTheme(2))
        series_day4_1 = QStackedBarSeries()
        series_day4_1.setName('DELTA')
        setUp = QBarSet('涨')
        setUp.setColor(Qt.red)
        setDown = QBarSet('跌')
        setDown.setColor(Qt.darkGreen)
        series_day4_1.append(setUp)
        series_day4_1.append(setDown)
        series_day4_2 = QLineSeries()
        series_day4_2.setName('DIF')
        pen_day4_2 = QPen(Qt.white)
        pen_day4_2.setStyle(Qt.SolidLine)
        pen_day4_2.setWidth(.5)
        series_day4_2.setPen(pen_day4_2)
        series_day4_3 = QLineSeries()
        series_day4_3.setName('DEA')
        pen_day4_3 = QPen(Qt.yellow)
        pen_day4_3.setStyle(Qt.SolidLine)
        pen_day4_3.setWidth(.5)
        series_day4_3.setPen(pen_day4_3)
        self.__chartDic['day']['macd'].addSeries(series_day4_1)
        self.__chartDic['day']['macd'].addSeries(series_day4_2)
        self.__chartDic['day']['macd'].addSeries(series_day4_3)
        axisX_day4_1 = QDateTimeAxis()
        axisX_day4_2 = QBarCategoryAxis()
        axisY_day4 = QValueAxis()
        axisX_day4_1.setFormat('yyyy-MM-dd')
        axisX_day4_1.setTickCount(10)
        axisX_day4_1.setMin(x_min)
        axisX_day4_1.setMax(x_max)
        axisX_day4_2.append(self.barLst)
        axisX_day4_2.setRange(self.barLst[0], self.barLst[-1])
        axisX_day4_2.setVisible(False)
        axisY_day4.setRange(-1, 1)
        axisY_day4.setLabelFormat('%.2f')
        axisY_day4.setTickCount(5)
        axisY_day4.setGridLineVisible(True)
        axisY_day4.setMinorGridLineVisible(False)
        self.__chartDic['day']['macd'].addAxis(axisX_day4_1, Qt.AlignBottom)
        self.__chartDic['day']['macd'].addAxis(axisX_day4_2, Qt.AlignBottom)
        self.__chartDic['day']['macd'].addAxis(axisY_day4, Qt.AlignLeft)
        self.__chartDic['day']['macd'].setAxisX(axisX_day4_2, series_day4_1)
        self.__chartDic['day']['macd'].setAxisY(axisY_day4, series_day4_1)
        self.__chartDic['day']['macd'].setAxisX(axisX_day4_1, series_day4_2)
        self.__chartDic['day']['macd'].setAxisY(axisY_day4, series_day4_2)
        self.__chartDic['day']['macd'].setAxisX(axisX_day4_1, series_day4_3)
        self.__chartDic['day']['macd'].setAxisY(axisY_day4, series_day4_3)
        self.__chartDic['day']['macd'].legend().markers()[0].setVisible(False)
        self.__chartDic['day']['macd'].legend().markers()[1].setVisible(False)
        # 日atr
        self.__chartDic['day']['atr'].setTitle('ATR')
        self.ui.chartView_day5.setChart(self.__chartDic['day']['atr'])
        self.ui.chartView_day5.setRenderHint(QPainter.Antialiasing)
        self.__chartDic['day']['atr'].setTheme(QChart.ChartTheme(2))
        series_day5_1 = QCandlestickSeries()
        series_day5_1.setIncreasingColor(Qt.red)
        series_day5_1.setDecreasingColor(Qt.darkGreen)
        series_day5_2 = QLineSeries()
        pen_day5_2 = QPen(Qt.white)
        pen_day5_2.setStyle(Qt.SolidLine)
        pen_day5_2.setWidth(.5)
        series_day5_2.setPen(pen_day5_2)
        series_day5_3 = QLineSeries()
        pen_day5_3 = QPen(Qt.yellow)
        pen_day5_3.setStyle(Qt.SolidLine)
        pen_day5_3.setWidth(.5)
        series_day5_3.setPen(pen_day5_3)
        series_day5_4 = QLineSeries()
        pen_day5_4 = QPen(QColor('#4ebdf2'))
        pen_day5_4.setStyle(Qt.SolidLine)
        pen_day5_4.setWidth(.5)
        series_day5_4.setPen(pen_day5_4)
        self.__chartDic['day']['atr'].addSeries(series_day5_1)
        self.__chartDic['day']['atr'].addSeries(series_day5_2)
        self.__chartDic['day']['atr'].addSeries(series_day5_3)
        self.__chartDic['day']['atr'].addSeries(series_day5_4)
        axisX_day5 = QDateTimeAxis()
        axisY_day5 = QValueAxis()
        axisX_day5.setFormat('yyyy-MM-dd')
        axisX_day5.setTickCount(10)
        axisX_day5.setMin(x_min)
        axisX_day5.setMax(x_max)
        axisY_day5.setRange(0, 100)
        axisY_day5.setLabelFormat('%.2f')
        axisY_day5.setTickCount(5)
        axisY_day5.setGridLineVisible(True)
        axisY_day5.setMinorGridLineVisible(False)
        self.__chartDic['day']['atr'].addAxis(axisX_day5, Qt.AlignBottom)
        self.__chartDic['day']['atr'].addAxis(axisY_day5, Qt.AlignLeft)
        series_day5_1.attachAxis(axisX_day5)
        series_day5_1.attachAxis(axisY_day5)
        series_day5_2.attachAxis(axisX_day5)
        series_day5_2.attachAxis(axisY_day5)
        series_day5_3.attachAxis(axisX_day5)
        series_day5_3.attachAxis(axisY_day5)
        series_day5_4.attachAxis(axisX_day5)
        series_day5_4.attachAxis(axisY_day5)
        self.__chartDic['day']['atr'].legend().hide()
        # 周趋势 + 均线
        # self.__chartDic['week']['k'].setTitle('趋势线')
        self.ui.chartView_week1.setChart(self.__chartDic['week']['k'])
        self.ui.chartView_week1.setRenderHint(QPainter.Antialiasing)
        self.__chartDic['week']['k'].setTheme(QChart.ChartTheme(2))
        series_week1_1 = QCandlestickSeries()
        series_week1_1.setName('蜡烛图')
        series_week1_1.setIncreasingColor(Qt.red)
        series_week1_1.setDecreasingColor(Qt.darkGreen)
        series_week1_2 = QLineSeries()
        series_week1_2.setName('MA5')
        pen_week1_2 = QPen(Qt.white)
        pen_week1_2.setStyle(Qt.SolidLine)
        pen_week1_2.setWidth(.5)
        series_week1_2.setPen(pen_week1_2)
        series_week1_3 = QLineSeries()
        series_week1_3.setName('MA10')
        pen_week1_3 = QPen(Qt.yellow)
        pen_week1_3.setStyle(Qt.SolidLine)
        pen_week1_3.setWidth(.5)
        series_week1_3.setPen(pen_week1_3)
        series_week1_4 = QLineSeries()
        series_week1_4.setName('MA20')
        pen_week1_4 = QPen(QColor('#4ebdf2'))
        pen_week1_4.setStyle(Qt.SolidLine)
        pen_week1_4.setWidth(.5)
        series_week1_4.setPen(pen_week1_4)
        self.__chartDic['week']['k'].addSeries(series_week1_1)
        self.__chartDic['week']['k'].addSeries(series_week1_2)
        self.__chartDic['week']['k'].addSeries(series_week1_3)
        self.__chartDic['week']['k'].addSeries(series_week1_4)
        axisX_week1 = QDateTimeAxis()
        axisY_week1 = QValueAxis()
        axisX_week1.setFormat('yyyy-MM-dd')
        axisX_week1.setTickCount(10)
        axisX_week1.setMin(x_min)
        axisX_week1.setMax(x_max)
        axisX_week1.setVisible(False)
        axisY_week1.setRange(0, 100)
        axisY_week1.setLabelFormat('%.2f')
        axisY_week1.setTickCount(5)
        axisY_week1.setGridLineVisible(True)
        axisY_week1.setMinorGridLineVisible(False)
        self.__chartDic['week']['k'].addAxis(axisX_week1, Qt.AlignBottom)
        self.__chartDic['week']['k'].addAxis(axisY_week1, Qt.AlignLeft)
        series_week1_1.attachAxis(axisX_week1)
        series_week1_1.attachAxis(axisY_week1)
        series_week1_2.attachAxis(axisX_week1)
        series_week1_2.attachAxis(axisY_week1)
        series_week1_3.attachAxis(axisX_week1)
        series_week1_3.attachAxis(axisY_week1)
        series_week1_4.attachAxis(axisX_week1)
        series_week1_4.attachAxis(axisY_week1)
        self.__chartDic['week']['k'].legend().markers()[0].setVisible(False)
        # 周成交量
        self.ui.chartView_week2.setChart(self.__chartDic['week']['vol'])
        self.ui.chartView_week2.setRenderHint(QPainter.Antialiasing)
        self.__chartDic['week']['vol'].setTheme(QChart.ChartTheme(2))
        series_week2 = QStackedBarSeries()
        setUp = QBarSet('涨')
        setUp.setColor(Qt.red)
        setDown = QBarSet('跌')
        setDown.setColor(Qt.darkGreen)
        series_week2.append(setUp)
        series_week2.append(setDown)
        self.__chartDic['week']['vol'].addSeries(series_week2)
        axisX_week2_1 = QDateTimeAxis()
        axisX_week2_2 = QBarCategoryAxis()
        axisY_week2 = QValueAxis()
        axisX_week2_1.setFormat('yyyy-MM-dd')
        axisX_week2_1.setTickCount(10)
        axisX_week2_1.setMin(x_min)
        axisX_week2_1.setMax(x_max)
        axisX_week2_1.setVisible(False)
        axisX_week2_2.append(self.barLst)
        axisX_week2_2.setRange(self.barLst[0], self.barLst[-1])
        axisX_week2_2.setVisible(False)
        axisY_week2.setRange(0, 100)
        axisY_week2.setLabelFormat('%d')
        axisY_week2.setTickCount(5)
        axisY_week2.setGridLineVisible(True)
        axisY_week2.setMinorGridLineVisible(False)
        self.__chartDic['week']['vol'].addAxis(axisX_week2_1, Qt.AlignBottom)
        self.__chartDic['week']['vol'].addAxis(axisX_week2_2, Qt.AlignBottom)
        self.__chartDic['week']['vol'].addAxis(axisY_week2, Qt.AlignLeft)
        self.__chartDic['week']['vol'].setAxisX(axisX_week2_2, series_week2)
        self.__chartDic['week']['vol'].setAxisY(axisY_week2, series_week2)
        self.__chartDic['week']['vol'].legend().hide()
        # 周kdj
        self.__chartDic['week']['kdj'].setTitle('KDJ')
        self.ui.chartView_week3.setChart(self.__chartDic['week']['kdj'])
        self.ui.chartView_week3.setRenderHint(QPainter.Antialiasing)
        self.__chartDic['week']['kdj'].setTheme(QChart.ChartTheme(2))
        series_week3_1 = QLineSeries()
        series_week3_1.setName('K')
        pen_week3_1 = QPen(Qt.white)
        pen_week3_1.setStyle(Qt.SolidLine)
        pen_week3_1.setWidth(.5)
        series_week3_1.setPen(pen_week3_1)
        series_week3_2 = QLineSeries()
        series_week3_2.setName('D')
        pen_week3_2 = QPen(Qt.yellow)
        pen_week3_2.setStyle(Qt.SolidLine)
        pen_week3_2.setWidth(.5)
        series_week3_2.setPen(pen_week3_2)
        series_week3_3 = QLineSeries()
        series_week3_3.setName('J')
        pen_week3_3 = QPen(Qt.red)
        pen_week3_3.setStyle(Qt.SolidLine)
        pen_week3_3.setWidth(.5)
        series_week3_3.setPen(pen_week3_3)
        self.__chartDic['week']['kdj'].addSeries(series_week3_1)
        self.__chartDic['week']['kdj'].addSeries(series_week3_2)
        self.__chartDic['week']['kdj'].addSeries(series_week3_3)
        axisX_week3 = QDateTimeAxis()
        axisY_week3 = QValueAxis()
        axisX_week3.setFormat('yyyy-MM-dd')
        axisX_week3.setTickCount(10)
        axisX_week3.setMin(x_min)
        axisX_week3.setMax(x_max)
        axisX_week3.setVisible(False)
        axisY_week3.setRange(-20, 120)
        axisY_week3.setLabelFormat('%.2f')
        axisY_week3.setTickCount(5)
        axisY_week3.setGridLineVisible(True)
        axisY_week3.setMinorGridLineVisible(False)
        self.__chartDic['week']['kdj'].addAxis(axisX_week3, Qt.AlignBottom)
        self.__chartDic['week']['kdj'].addAxis(axisY_week3, Qt.AlignLeft)
        series_week3_1.attachAxis(axisX_week3)
        series_week3_1.attachAxis(axisY_week3)
        series_week3_2.attachAxis(axisX_week3)
        series_week3_2.attachAxis(axisY_week3)
        series_week3_3.attachAxis(axisX_week3)
        series_week3_3.attachAxis(axisY_week3)
        # 周macd
        self.__chartDic['week']['macd'].setTitle('MACD')
        self.ui.chartView_week4.setChart(self.__chartDic['week']['macd'])
        self.ui.chartView_week4.setRenderHint(QPainter.Antialiasing)
        self.__chartDic['week']['macd'].setTheme(QChart.ChartTheme(2))
        series_week4_1 = QStackedBarSeries()
        series_week4_1.setName('DELTA')
        setUp = QBarSet('涨')
        setUp.setColor(Qt.red)
        setDown = QBarSet('跌')
        setDown.setColor(Qt.darkGreen)
        series_week4_1.append(setUp)
        series_week4_1.append(setDown)
        series_week4_2 = QLineSeries()
        series_week4_2.setName('DIF')
        pen_week4_2 = QPen(Qt.white)
        pen_week4_2.setStyle(Qt.SolidLine)
        pen_week4_2.setWidth(.5)
        series_week4_2.setPen(pen_week4_2)
        series_week4_3 = QLineSeries()
        series_week4_3.setName('DEA')
        pen_week4_3 = QPen(Qt.yellow)
        pen_week4_3.setStyle(Qt.SolidLine)
        pen_week4_3.setWidth(.5)
        series_week4_3.setPen(pen_week4_3)
        self.__chartDic['week']['macd'].addSeries(series_week4_1)
        self.__chartDic['week']['macd'].addSeries(series_week4_2)
        self.__chartDic['week']['macd'].addSeries(series_week4_3)
        axisX_week4_1 = QDateTimeAxis()
        axisX_week4_2 = QBarCategoryAxis()
        axisY_week4 = QValueAxis()
        axisX_week4_1.setFormat('yyyy-MM-dd')
        axisX_week4_1.setTickCount(10)
        axisX_week4_1.setMin(x_min)
        axisX_week4_1.setMax(x_max)
        axisX_week4_1.setVisible(False)
        axisX_week4_2.append(self.barLst)
        axisX_week4_2.setRange(self.barLst[0], self.barLst[-1])
        axisX_week4_2.setVisible(False)
        axisY_week4.setRange(-1, 1)
        axisY_week4.setLabelFormat('%.2f')
        axisY_week4.setTickCount(5)
        axisY_week4.setGridLineVisible(True)
        axisY_week4.setMinorGridLineVisible(False)
        self.__chartDic['week']['macd'].addAxis(axisX_week4_1, Qt.AlignBottom)
        self.__chartDic['week']['macd'].addAxis(axisX_week4_2, Qt.AlignBottom)
        self.__chartDic['week']['macd'].addAxis(axisY_week4, Qt.AlignLeft)
        self.__chartDic['week']['macd'].setAxisX(axisX_week4_2, series_week4_1)
        self.__chartDic['week']['macd'].setAxisY(axisY_week4, series_week4_1)
        self.__chartDic['week']['macd'].setAxisX(axisX_week4_1, series_week4_2)
        self.__chartDic['week']['macd'].setAxisY(axisY_week4, series_week4_2)
        self.__chartDic['week']['macd'].setAxisX(axisX_week4_1, series_week4_3)
        self.__chartDic['week']['macd'].setAxisY(axisY_week4, series_week4_3)
        self.__chartDic['week']['macd'].legend().markers()[0].setVisible(False)
        self.__chartDic['week']['macd'].legend().markers()[1].setVisible(False)
        # 周atr
        self.__chartDic['week']['atr'].setTitle('ATR')
        self.ui.chartView_week5.setChart(self.__chartDic['week']['atr'])
        self.ui.chartView_week5.setRenderHint(QPainter.Antialiasing)
        self.__chartDic['week']['atr'].setTheme(QChart.ChartTheme(2))
        series_week5_1 = QCandlestickSeries()
        series_week5_1.setIncreasingColor(Qt.red)
        series_week5_1.setDecreasingColor(Qt.darkGreen)
        series_week5_2 = QLineSeries()
        pen_week5_2 = QPen(Qt.white)
        pen_week5_2.setStyle(Qt.SolidLine)
        pen_week5_2.setWidth(.5)
        series_week5_2.setPen(pen_week5_2)
        series_week5_3 = QLineSeries()
        pen_week5_3 = QPen(Qt.yellow)
        pen_week5_3.setStyle(Qt.SolidLine)
        pen_week5_3.setWidth(.5)
        series_week5_3.setPen(pen_week5_3)
        series_week5_4 = QLineSeries()
        pen_week5_4 = QPen(QColor('#4ebdf2'))
        pen_week5_4.setStyle(Qt.SolidLine)
        pen_week5_4.setWidth(.5)
        series_week5_4.setPen(pen_week5_4)
        self.__chartDic['week']['atr'].addSeries(series_week5_1)
        self.__chartDic['week']['atr'].addSeries(series_week5_2)
        self.__chartDic['week']['atr'].addSeries(series_week5_3)
        self.__chartDic['week']['atr'].addSeries(series_week5_4)
        axisX_week5 = QDateTimeAxis()
        axisY_week5 = QValueAxis()
        axisX_week5.setFormat('yyyy-MM-dd')
        axisX_week5.setTickCount(10)
        axisX_week5.setMin(x_min)
        axisX_week5.setMax(x_max)
        axisX_week5.setVisible(False)
        axisY_week5.setRange(0, 100)
        axisY_week5.setLabelFormat('%.2f')
        axisY_week5.setTickCount(5)
        axisY_week5.setGridLineVisible(True)
        axisY_week5.setMinorGridLineVisible(False)
        self.__chartDic['week']['atr'].addAxis(axisX_week5, Qt.AlignBottom)
        self.__chartDic['week']['atr'].addAxis(axisY_week5, Qt.AlignLeft)
        series_week5_1.attachAxis(axisX_week5)
        series_week5_1.attachAxis(axisY_week5)
        series_week5_2.attachAxis(axisX_week5)
        series_week5_2.attachAxis(axisY_week5)
        series_week5_3.attachAxis(axisX_week5)
        series_week5_3.attachAxis(axisY_week5)
        series_week5_4.attachAxis(axisX_week5)
        series_week5_4.attachAxis(axisY_week5)
        self.__chartDic['week']['atr'].legend().hide()
        # 月趋势 + 均线
        # self.__chartDic['month']['k'].setTitle('趋势线')
        self.ui.chartView_month1.setChart(self.__chartDic['month']['k'])
        self.ui.chartView_month1.setRenderHint(QPainter.Antialiasing)
        self.__chartDic['month']['k'].setTheme(QChart.ChartTheme(2))
        series_month1_1 = QCandlestickSeries()
        series_month1_1.setName('蜡烛图')
        series_month1_1.setIncreasingColor(Qt.red)
        series_month1_1.setDecreasingColor(Qt.darkGreen)
        series_month1_2 = QLineSeries()
        series_month1_2.setName('MA5')
        pen_month1_2 = QPen(Qt.white)
        pen_month1_2.setStyle(Qt.SolidLine)
        pen_month1_2.setWidth(.5)
        series_month1_2.setPen(pen_month1_2)
        series_month1_3 = QLineSeries()
        series_month1_3.setName('MA10')
        pen_month1_3 = QPen(Qt.yellow)
        pen_month1_3.setStyle(Qt.SolidLine)
        pen_month1_3.setWidth(.5)
        series_month1_3.setPen(pen_month1_3)
        series_month1_4 = QLineSeries()
        series_month1_4.setName('MA20')
        pen_month1_4 = QPen(QColor('#4ebdf2'))
        pen_month1_4.setStyle(Qt.SolidLine)
        pen_month1_4.setWidth(.5)
        series_month1_4.setPen(pen_month1_4)
        self.__chartDic['month']['k'].addSeries(series_month1_1)
        self.__chartDic['month']['k'].addSeries(series_month1_2)
        self.__chartDic['month']['k'].addSeries(series_month1_3)
        self.__chartDic['month']['k'].addSeries(series_month1_4)
        axisX_month1 = QDateTimeAxis()
        axisY_month1 = QValueAxis()
        axisX_month1.setFormat('yyyy-MM-dd')
        axisX_month1.setTickCount(10)
        axisX_month1.setMin(x_min)
        axisX_month1.setMax(x_max)
        axisX_month1.setVisible(False)
        axisY_month1.setRange(0, 100)
        axisY_month1.setLabelFormat('%.2f')
        axisY_month1.setTickCount(5)
        axisY_month1.setGridLineVisible(True)
        axisY_month1.setMinorGridLineVisible(False)
        self.__chartDic['month']['k'].addAxis(axisX_month1, Qt.AlignBottom)
        self.__chartDic['month']['k'].addAxis(axisY_month1, Qt.AlignLeft)
        series_month1_1.attachAxis(axisX_month1)
        series_month1_1.attachAxis(axisY_month1)
        series_month1_2.attachAxis(axisX_month1)
        series_month1_2.attachAxis(axisY_month1)
        series_month1_3.attachAxis(axisX_month1)
        series_month1_3.attachAxis(axisY_month1)
        series_month1_4.attachAxis(axisX_month1)
        series_month1_4.attachAxis(axisY_month1)
        self.__chartDic['month']['k'].legend().markers()[0].setVisible(False)
        # 月成交量
        self.ui.chartView_month2.setChart(self.__chartDic['month']['vol'])
        self.ui.chartView_month2.setRenderHint(QPainter.Antialiasing)
        self.__chartDic['month']['vol'].setTheme(QChart.ChartTheme(2))
        series_month2 = QStackedBarSeries()
        setUp = QBarSet('涨')
        setUp.setColor(Qt.red)
        setDown = QBarSet('跌')
        setDown.setColor(Qt.darkGreen)
        series_month2.append(setUp)
        series_month2.append(setDown)
        self.__chartDic['month']['vol'].addSeries(series_month2)
        axisX_month2_1 = QDateTimeAxis()
        axisX_month2_2 = QBarCategoryAxis()
        axisY_month2 = QValueAxis()
        axisX_month2_1.setFormat('yyyy-MM-dd')
        axisX_month2_1.setTickCount(10)
        axisX_month2_1.setMin(x_min)
        axisX_month2_1.setMax(x_max)
        axisX_month2_1.setVisible(False)
        axisX_month2_2.append(self.barLst)
        axisX_month2_2.setRange(self.barLst[0], self.barLst[-1])
        axisX_month2_2.setVisible(False)
        axisY_month2.setRange(0, 100)
        axisY_month2.setLabelFormat('%d')
        axisY_month2.setTickCount(5)
        axisY_month2.setGridLineVisible(True)
        axisY_month2.setMinorGridLineVisible(False)
        self.__chartDic['month']['vol'].addAxis(axisX_month2_1, Qt.AlignBottom)
        self.__chartDic['month']['vol'].addAxis(axisX_month2_2, Qt.AlignBottom)
        self.__chartDic['month']['vol'].addAxis(axisY_month2, Qt.AlignLeft)
        self.__chartDic['month']['vol'].setAxisX(axisX_month2_2, series_month2)
        self.__chartDic['month']['vol'].setAxisY(axisY_month2, series_month2)
        self.__chartDic['month']['vol'].legend().hide()
        # 月kdj
        self.__chartDic['month']['kdj'].setTitle('KDJ')
        self.ui.chartView_month3.setChart(self.__chartDic['month']['kdj'])
        self.ui.chartView_month3.setRenderHint(QPainter.Antialiasing)
        self.__chartDic['month']['kdj'].setTheme(QChart.ChartTheme(2))
        series_month3_1 = QLineSeries()
        series_month3_1.setName('K')
        pen_month3_1 = QPen(Qt.white)
        pen_month3_1.setStyle(Qt.SolidLine)
        pen_month3_1.setWidth(.5)
        series_month3_1.setPen(pen_month3_1)
        series_month3_2 = QLineSeries()
        series_month3_2.setName('D')
        pen_month3_2 = QPen(Qt.yellow)
        pen_month3_2.setStyle(Qt.SolidLine)
        pen_month3_2.setWidth(.5)
        series_month3_2.setPen(pen_month3_2)
        series_month3_3 = QLineSeries()
        series_month3_3.setName('J')
        pen_month3_3 = QPen(Qt.red)
        pen_month3_3.setStyle(Qt.SolidLine)
        pen_month3_3.setWidth(.5)
        series_month3_3.setPen(pen_month3_3)
        self.__chartDic['month']['kdj'].addSeries(series_month3_1)
        self.__chartDic['month']['kdj'].addSeries(series_month3_2)
        self.__chartDic['month']['kdj'].addSeries(series_month3_3)
        axisX_month3 = QDateTimeAxis()
        axisY_month3 = QValueAxis()
        axisX_month3.setFormat('yyyy-MM-dd')
        axisX_month3.setTickCount(10)
        axisX_month3.setMin(x_min)
        axisX_month3.setMax(x_max)
        axisX_month3.setVisible(False)
        axisY_month3.setRange(-20, 120)
        axisY_month3.setLabelFormat('%.2f')
        axisY_month3.setTickCount(5)
        axisY_month3.setGridLineVisible(True)
        axisY_month3.setMinorGridLineVisible(False)
        self.__chartDic['month']['kdj'].addAxis(axisX_month3, Qt.AlignBottom)
        self.__chartDic['month']['kdj'].addAxis(axisY_month3, Qt.AlignLeft)
        series_month3_1.attachAxis(axisX_month3)
        series_month3_1.attachAxis(axisY_month3)
        series_month3_2.attachAxis(axisX_month3)
        series_month3_2.attachAxis(axisY_month3)
        series_month3_3.attachAxis(axisX_month3)
        series_month3_3.attachAxis(axisY_month3)
        # 月macd
        self.__chartDic['month']['macd'].setTitle('MACD')
        self.ui.chartView_month4.setChart(self.__chartDic['month']['macd'])
        self.ui.chartView_month4.setRenderHint(QPainter.Antialiasing)
        self.__chartDic['month']['macd'].setTheme(QChart.ChartTheme(2))
        series_month4_1 = QStackedBarSeries()
        series_month4_1.setName('DELTA')
        setUp = QBarSet('涨')
        setUp.setColor(Qt.red)
        setDown = QBarSet('跌')
        setDown.setColor(Qt.darkGreen)
        series_month4_1.append(setUp)
        series_month4_1.append(setDown)
        series_month4_2 = QLineSeries()
        series_month4_2.setName('DIF')
        pen_month4_2 = QPen(Qt.white)
        pen_month4_2.setStyle(Qt.SolidLine)
        pen_month4_2.setWidth(.5)
        series_month4_2.setPen(pen_month4_2)
        series_month4_3 = QLineSeries()
        series_month4_3.setName('DEA')
        pen_month4_3 = QPen(Qt.yellow)
        pen_month4_3.setStyle(Qt.SolidLine)
        pen_month4_3.setWidth(.5)
        series_month4_3.setPen(pen_month4_3)
        self.__chartDic['month']['macd'].addSeries(series_month4_1)
        self.__chartDic['month']['macd'].addSeries(series_month4_2)
        self.__chartDic['month']['macd'].addSeries(series_month4_3)
        axisX_month4_1 = QDateTimeAxis()
        axisX_month4_2 = QBarCategoryAxis()
        axisY_month4 = QValueAxis()
        axisX_month4_1.setFormat('yyyy-MM-dd')
        axisX_month4_1.setTickCount(10)
        axisX_month4_1.setMin(x_min)
        axisX_month4_1.setMax(x_max)
        axisX_month4_1.setVisible(False)
        axisX_month4_2.append(self.barLst)
        axisX_month4_2.setRange(self.barLst[0], self.barLst[-1])
        axisX_month4_2.setVisible(False)
        axisY_month4.setRange(-1, 1)
        axisY_month4.setLabelFormat('%.2f')
        axisY_month4.setTickCount(5)
        axisY_month4.setGridLineVisible(True)
        axisY_month4.setMinorGridLineVisible(False)
        self.__chartDic['month']['macd'].addAxis(axisX_month4_1, Qt.AlignBottom)
        self.__chartDic['month']['macd'].addAxis(axisX_month4_2, Qt.AlignBottom)
        self.__chartDic['month']['macd'].addAxis(axisY_month4, Qt.AlignLeft)
        self.__chartDic['month']['macd'].setAxisX(axisX_month4_2, series_month4_1)
        self.__chartDic['month']['macd'].setAxisY(axisY_month4, series_month4_1)
        self.__chartDic['month']['macd'].setAxisX(axisX_month4_1, series_month4_2)
        self.__chartDic['month']['macd'].setAxisY(axisY_month4, series_month4_2)
        self.__chartDic['month']['macd'].setAxisX(axisX_month4_1, series_month4_3)
        self.__chartDic['month']['macd'].setAxisY(axisY_month4, series_month4_3)
        self.__chartDic['month']['macd'].legend().markers()[0].setVisible(False)
        self.__chartDic['month']['macd'].legend().markers()[1].setVisible(False)
        # 月atr
        self.__chartDic['month']['atr'].setTitle('ATR')
        self.ui.chartView_month5.setChart(self.__chartDic['month']['atr'])
        self.ui.chartView_month5.setRenderHint(QPainter.Antialiasing)
        self.__chartDic['month']['atr'].setTheme(QChart.ChartTheme(2))
        series_month5_1 = QCandlestickSeries()
        series_month5_1.setIncreasingColor(Qt.red)
        series_month5_1.setDecreasingColor(Qt.darkGreen)
        series_month5_2 = QLineSeries()
        pen_month5_2 = QPen(Qt.white)
        pen_month5_2.setStyle(Qt.SolidLine)
        pen_month5_2.setWidth(.5)
        series_month5_2.setPen(pen_month5_2)
        series_month5_3 = QLineSeries()
        pen_month5_3 = QPen(Qt.yellow)
        pen_month5_3.setStyle(Qt.SolidLine)
        pen_month5_3.setWidth(.5)
        series_month5_3.setPen(pen_month5_3)
        series_month5_4 = QLineSeries()
        pen_month5_4 = QPen(QColor('#4ebdf2'))
        pen_month5_4.setStyle(Qt.SolidLine)
        pen_month5_4.setWidth(.5)
        series_month5_4.setPen(pen_month5_4)
        self.__chartDic['month']['atr'].addSeries(series_month5_1)
        self.__chartDic['month']['atr'].addSeries(series_month5_2)
        self.__chartDic['month']['atr'].addSeries(series_month5_3)
        self.__chartDic['month']['atr'].addSeries(series_month5_4)
        axisX_month5 = QDateTimeAxis()
        axisY_month5 = QValueAxis()
        axisX_month5.setFormat('yyyy-MM-dd')
        axisX_month5.setTickCount(10)
        axisX_month5.setMin(x_min)
        axisX_month5.setMax(x_max)
        axisX_month5.setVisible(False)
        axisY_month5.setRange(0, 100)
        axisY_month5.setLabelFormat('%.2f')
        axisY_month5.setTickCount(5)
        axisY_month5.setGridLineVisible(True)
        axisY_month5.setMinorGridLineVisible(False)
        self.__chartDic['month']['atr'].addAxis(axisX_month5, Qt.AlignBottom)
        self.__chartDic['month']['atr'].addAxis(axisY_month5, Qt.AlignLeft)
        series_month5_1.attachAxis(axisX_month5)
        series_month5_1.attachAxis(axisY_month5)
        series_month5_2.attachAxis(axisX_month5)
        series_month5_2.attachAxis(axisY_month5)
        series_month5_3.attachAxis(axisX_month5)
        series_month5_3.attachAxis(axisY_month5)
        series_month5_4.attachAxis(axisX_month5)
        series_month5_4.attachAxis(axisY_month5)
        self.__chartDic['month']['atr'].legend().hide()

    def __loadData(self):
        code = random.choice(self.codeLst)
        data = pd.read_csv(os.path.join('data', code))[['开盘', '收盘', '最高', '最低', '成交量']]
        minus_lst = [i for i in range(len(data)) if data['收盘'][i] <= 0]
        if minus_lst:
            data = data.iloc[(minus_lst[-1] + 1):, :]
        while data['收盘'].min() < 0 or len(data) < 2 * self.cfg['显示长度'] + self.cfg['操作长度']:
            code = random.choice(self.codeLst)
            data = pd.read_csv(os.path.join('data', code))[['开盘', '收盘', '最高', '最低', '成交量']]
            minus_lst = [i for i in range(len(data)) if data['收盘'][i] <= 0]
            if minus_lst:
                data = data.iloc[(minus_lst[-1] + 1):, :]
        name = self.codeDic[code.split('.')[0]]
        data.reset_index(drop = True, inplace = True)
        # rename
        data.columns = ['day_open', 'day_close', 'day_high', 'day_low', 'day_vol']
        # 5日均线-10日均线-20日均线
        length = len(data)
        data['day_5'] = [data['day_close'][:(i + 1)].mean() for i in range(4)] + [data['day_close'][i:(i + 5)].mean() for i in range(length - 4)]
        data['day_10'] = [data['day_close'][:(i + 1)].mean() for i in range(9)] + [data['day_close'][i:(i + 10)].mean() for i in range(length - 9)]
        data['day_20'] = [data['day_close'][:(i + 1)].mean() for i in range(19)] + [data['day_close'][i:(i + 20)].mean() for i in range(length - 19)]
        # 周相关
        data['week_open'] = [data['day_open'][0] for _ in range(4)] + [data['day_open'][i - 4] for i in range(4, length)]
        data['week_close'] = data['day_close']
        data['week_high'] = [data['day_high'][:(i + 1)].max() for i in range(4)] + [data['day_high'][(i - 4):(i + 1)].max() for i in range(4, length)]
        data['week_low'] = [data['day_low'][:(i + 1)].min() for i in range(4)] + [data['day_low'][(i - 4):(i + 1)].min() for i in range(4, length)]
        data['week_5'] = [data['week_close'][:(i + 1)].mean() for i in range(24)] + [data['week_close'][i:(i + 25)].mean() for i in range(length - 24)]
        data['week_10'] = [data['week_close'][:(i + 1)].mean() for i in range(49)] + [data['week_close'][i:(i + 50)].mean() for i in range(length - 49)]
        data['week_20'] = [data['week_close'][:(i + 1)].mean() for i in range(99)] + [data['week_close'][i:(i + 100)].mean() for i in range(length - 99)]
        # 月相关
        data['month_open'] = [data['day_open'][0] for _ in range(19)] + [data['day_open'][i - 19] for i in range(19, length)]
        data['month_close'] = data['day_close']
        data['month_high'] = [data['day_high'][:(i + 1)].max() for i in range(19)] + [data['day_high'][(i - 19):(i + 1)].max() for i in range(19, length)]
        data['month_low'] = [data['day_low'][:(i + 1)].min() for i in range(19)] + [data['day_low'][(i - 19):(i + 1)].min() for i in range(19, length)]
        data['month_5'] = [data['month_close'][:(i + 1)].mean() for i in range(99)] + [data['month_close'][i:(i + 100)].mean() for i in range(length - 99)]
        data['month_10'] = [data['month_close'][:(i + 1)].mean() for i in range(199)] + [data['month_close'][i:(i + 200)].mean() for i in range(length - 199)]
        data['month_20'] = [data['month_close'][:(i + 1)].mean() for i in range(399)] + [data['month_close'][i:(i + 400)].mean() for i in range(length - 399)]
        # 成交量
        data['week_vol'] = [data['day_vol'][:(i + 1)].sum() for i in range(4)] + [data['day_vol'][(i - 4):(i + 1)].sum() for i in range(4, length)]
        data['month_vol'] = [data['day_vol'][:(i + 1)].sum() for i in range(19)] + [data['day_vol'][(i - 19):(i + 1)].sum() for i in range(19, length)]
        # kdj
        rsv_day = [100 * (data['day_close'][i] - data['day_low'][:(i + 1)].min()) / (data['day_high'][:(i + 1)].max() - data['day_low'][:(i + 1)].min() + 1e-9) for i in range(8)] + [100 * (data['day_close'][i] - data['day_low'][(i - 8):(i + 1)].min()) / (data['day_high'][(i - 8):(i + 1)].max() - data['day_low'][(i - 8):(i + 1)].min() + 1e-9) for i in range(8, length)]
        rsv_week = [100 * (data['week_close'][i] - data['week_low'][:(i + 1)].min()) / (data['week_high'][:(i + 1)].max() - data['week_low'][:(i + 1)].min() + 1e-9) for i in range(44)] + [100 * (data['week_close'][i] - data['week_low'][(i - 44):(i + 1)].min()) / (data['week_high'][(i - 44):(i + 1)].max() - data['week_low'][(i - 44):(i + 1)].min() + 1e-9) for i in range(44, length)]
        rsv_month = [100 * (data['month_close'][i] - data['month_low'][:(i + 1)].min()) / (data['month_high'][:(i + 1)].max() - data['month_low'][:(i + 1)].min() + 1e-9) for i in range(179)] + [100 * (data['month_close'][i] - data['month_low'][(i - 179):(i + 1)].min()) / (data['month_high'][(i - 179):(i + 1)].max() - data['month_low'][(i - 179):(i + 1)].min() + 1e-9) for i in range(179, length)]
        k_day = [50, ]
        d_day = [50, ]
        j_day = [50, ]
        k_week = [50, ]
        d_week = [50, ]
        j_week = [50, ]
        k_month = [50, ]
        d_month = [50, ]
        j_month = [50, ]
        for i in range(1, length):
            k_day.append(k_day[-1] * 2 / 3 + rsv_day[i] / 3)
            d_day.append(d_day[-1] * 2 / 3 + k_day[-1] / 3)
            j_day.append(3 * k_day[-1] - 2 * d_day[-1])
            k_week.append(k_week[-1] * 2 / 3 + rsv_week[i] / 3)
            d_week.append(d_week[-1] * 2 / 3 + k_week[-1] / 3)
            j_week.append(3 * k_week[-1] - 2 * d_week[-1])
            k_month.append(k_month[-1] * 2 / 3 + rsv_month[i] / 3)
            d_month.append(d_month[-1] * 2 / 3 + k_month[-1] / 3)
            j_month.append(3 * k_month[-1] - 2 * d_month[-1])
        data['day_k'] = k_day
        data['day_d'] = d_day
        data['day_j'] = j_day
        data['week_k'] = k_week
        data['week_d'] = d_week
        data['week_j'] = j_week
        data['month_k'] = k_month
        data['month_d'] = d_month
        data['month_j'] = j_month
        # macd
        ema_day_12 = [data['day_close'][0], ]
        ema_day_26 = [data['day_close'][0], ]
        ema_week_12 = [data['week_close'][0], ]
        ema_week_26 = [data['week_close'][0], ]
        ema_month_12 = [data['month_close'][0], ]
        ema_month_26 = [data['month_close'][0], ]
        for i in range(1, length):
            ema_day_12.append(2 * data['day_close'][i] / (12 + 1) + (12 - 1) * ema_day_12[-1] / (12 + 1))
            ema_day_26.append(2 * data['day_close'][i] / (26 + 1) + (26 - 1) * ema_day_26[-1] / (26 + 1))
            ema_week_12.append(2 * data['week_close'][i] / (12 + 1) + (12 - 1) * ema_week_12[-1] / (12 + 1))
            ema_week_26.append(2 * data['week_close'][i] / (26 + 1) + (26 - 1) * ema_week_26[-1] / (26 + 1))
            ema_month_12.append(2 * data['month_close'][i] / (12 + 1) + (12 - 1) * ema_month_12[-1] / (12 + 1))
            ema_month_26.append(2 * data['month_close'][i] / (26 + 1) + (26 - 1) * ema_month_26[-1] / (26 + 1))
        dif_day = [ema_day_12[i] - ema_day_26[i] for i in range(length)]
        dea_day = dif_day[:8] + [np.mean(dif_day[(i - 8):(i + 1)]) for i in range(8, length)]
        macd_day = [2 * (dif_day[i] - dea_day[i]) for i in range(length)]
        dif_week = [ema_week_12[i] - ema_week_26[i] for i in range(length)]
        dea_week = dif_week[:8] + [np.mean(dif_week[(i - 8):(i + 1)]) for i in range(8, length)]
        macd_week = [2 * (dif_week[i] - dea_week[i]) for i in range(length)]
        dif_month = [ema_month_12[i] - ema_month_26[i] for i in range(length)]
        dea_month = dif_month[:8] + [np.mean(dif_month[(i - 8):(i + 1)]) for i in range(8, length)]
        macd_month = [2 * (dif_month[i] - dea_month[i]) for i in range(length)]
        data['day_dif'] = dif_day
        data['day_dea'] = dea_day
        data['day_macd'] = macd_day
        data['week_dif'] = dif_week
        data['week_dea'] = dea_week
        data['week_macd'] = macd_week
        data['month_dif'] = dif_month
        data['month_dea'] = dea_month
        data['month_macd'] = macd_month
        # atr
        atr_day = [0, ] + np.max(abs(np.array([
            (data['day_high'].values - data['day_low'].values)[1:], 
            data['day_high'].values[1:] - data['day_close'].values[:(length - 1)], 
            data['day_low'].values[1:] - data['day_close'].values[:(length - 1)]
        ])), axis = 0).tolist()
        atr_day_14 = np.array([0 for _ in range(13)] + [np.mean(atr_day[(i - 13):(i + 1)]) for i in range(13, length)])
        atr_day_high = data['day_20'].values + 3 * atr_day_14
        atr_day_low = data['day_20'].values - 3 * atr_day_14
        atr_week = [0, ] + np.max(abs(np.array([
            (data['week_high'].values - data['week_low'].values)[1:], 
            data['week_high'].values[1:] - data['week_close'].values[:(length - 1)], 
            data['week_low'].values[1:] - data['week_close'].values[:(length - 1)]
        ])), axis = 0).tolist()
        atr_week_14 = np.array([0 for _ in range(13)] + [np.mean(atr_week[(i - 13):(i + 1)]) for i in range(13, length)])
        atr_week_high = data['week_20'].values + 3 * atr_week_14
        atr_week_low = data['week_20'].values - 3 * atr_week_14
        atr_month = [0, ] + np.max(abs(np.array([
            (data['month_high'].values - data['month_low'].values)[1:], 
            data['month_high'].values[1:] - data['month_close'].values[:(length - 1)], 
            data['month_low'].values[1:] - data['month_close'].values[:(length - 1)]
        ])), axis = 0).tolist()
        atr_month_14 = np.array([0 for _ in range(13)] + [np.mean(atr_month[(i - 13):(i + 1)]) for i in range(13, length)])
        atr_month_high = data['day_20'].values + 3 * atr_month_14
        atr_month_low = data['day_20'].values - 3 * atr_month_14
        data['day_atr_high'] = atr_day_high
        data['day_atr_low'] = atr_day_low
        data['week_atr_high'] = atr_week_high
        data['week_atr_low'] = atr_week_low
        data['month_atr_high'] = atr_month_high
        data['month_atr_low'] = atr_month_low
        ind = random.randint(2 * self.cfg['显示长度'], length - self.cfg['操作长度'])
        start = QDateTime.fromString('1978-12-18', 'yyyy-MM-dd')
        data['time'] = [start.addDays(i) for i in range(length)]
        data['ms'] = [282758400000 + 86400000 * i for i in range(length)]
        return ind, data, len(data), name
    
    def __plot(self, cnt = 0):
        # day
        min_x_day = self.data['time'][self.ind - self.cfg['显示长度'] + 1]
        max_x = self.data['time'][self.ind]
        # 蜡烛 + 均线
        chartView_day1 = self.__chartDic['day']['k']
        series_day1_1, series_day1_2, series_day1_3, series_day1_4, series_day1_5, series_day1_6 = chartView_day1.series()
        candle_day1 = series_day1_1.sets()
        if not candle_day1:
            for i in range(self.ind - self.cfg['显示长度'] + 1, self.ind + 1):
                oneCandle = QCandlestickSet()
                oneCandle.setOpen(self.data['day_open'][i])
                oneCandle.setHigh(self.data['day_high'][i])
                oneCandle.setLow(self.data['day_low'][i])
                oneCandle.setClose(self.data['day_close'][i])
                oneCandle.setTimestamp(self.data['ms'][i])
                series_day1_1.append(oneCandle)
                series_day1_2.append(self.data['ms'][i], self.data['day_5'][i])
                series_day1_3.append(self.data['ms'][i], self.data['day_10'][i])
                series_day1_4.append(self.data['ms'][i], self.data['day_20'][i])
        else:
            series_day1_1.remove(candle_day1[0])
            oneCandle = QCandlestickSet()
            oneCandle.setOpen(self.data['day_open'][self.ind])
            oneCandle.setHigh(self.data['day_high'][self.ind])
            oneCandle.setLow(self.data['day_low'][self.ind])
            oneCandle.setClose(self.data['day_close'][self.ind])
            oneCandle.setTimestamp(self.data['ms'][self.ind])
            series_day1_1.append(oneCandle)
            series_day1_2.remove(series_day1_2.at(0))
            series_day1_2.append(self.data['ms'][self.ind], self.data['day_5'][self.ind])
            series_day1_3.remove(series_day1_3.at(0))
            series_day1_3.append(self.data['ms'][self.ind], self.data['day_10'][self.ind])
            series_day1_4.remove(series_day1_4.at(0))
            series_day1_4.append(self.data['ms'][self.ind], self.data['day_20'][self.ind])            
            if series_day1_5.count() > self.cfg['显示长度']:
                series_day1_5.remove(0)
            if series_day1_6.count() > self.cfg['显示长度']:
                series_day1_6.remove(0)
            if cnt > 0:
                series_day1_5.append(self.data['ms'][self.ind], self.data['day_open'][self.ind])
            elif cnt < 0:
                series_day1_6.append(self.data['ms'][self.ind], self.data['day_open'][self.ind])
        yl = self.data[['day_low', 'day_5', 'day_10', 'day_20']][(self.ind - self.cfg['显示长度'] + 1):(self.ind + 1)].min().min()
        yh = self.data[['day_high', 'day_5', 'day_10', 'day_20']][(self.ind - self.cfg['显示长度'] + 1):(self.ind + 1)].max().max()
        chartView_day1.axisX().setRange(min_x_day, max_x)
        chartView_day1.axisY().setRange(round(yl - .1 * (yh - yl), 2), round(yh + .1 * (yh - yl), 2))
        # 成交量
        chartView_day2 = self.__chartDic['day']['vol']
        series_day2 = chartView_day2.series()[0]
        setUp, setDown = series_day2.barSets()
        if not setUp.count():
            for i in range(self.ind - self.cfg['显示长度'] + 1, self.ind + 1):
                if self.data['day_close'][i] >= self.data['day_open'][i]:
                    setUp.append(self.data['day_vol'][i])
                    setDown.append(0)
                else:
                    setUp.append(0)
                    setDown.append(self.data['day_vol'][i])
        else:
            setUp.remove(0)
            setDown.remove(0)
            if self.data['day_close'][self.ind] >= self.data['day_open'][self.ind]:
                setUp.append(self.data['day_vol'][self.ind])
                setDown.append(0)
            else:
                setUp.append(0)
                setDown.append(self.data['day_vol'][self.ind])
        yl = int(self.data['day_vol'][(self.ind - self.cfg['显示长度'] + 1):(self.ind + 1)].max() * 1.1)
        chartView_day2.axisX().setRange(min_x_day, max_x)
        chartView_day2.axisY().setRange(0, yl)
        # kdj
        chartView_day3 = self.__chartDic['day']['kdj']
        series_day3_1, series_day3_2, series_day3_3 = chartView_day3.series()
        if not series_day3_1.count():
            for i in range(self.ind - self.cfg['显示长度'] + 1, self.ind + 1):
                series_day3_1.append(self.data['ms'][i], self.data['day_k'][i])
                series_day3_2.append(self.data['ms'][i], self.data['day_d'][i])
                series_day3_3.append(self.data['ms'][i], self.data['day_j'][i])
        else:
            series_day3_1.remove(series_day3_1.at(0))
            series_day3_1.append(self.data['ms'][self.ind], self.data['day_k'][self.ind])
            series_day3_2.remove(series_day3_2.at(0))
            series_day3_2.append(self.data['ms'][self.ind], self.data['day_d'][self.ind])
            series_day3_3.remove(series_day3_3.at(0))
            series_day3_3.append(self.data['ms'][self.ind], self.data['day_j'][self.ind])            
        chartView_day3.axisX().setRange(min_x_day, max_x)
        chartView_day3.axisY().setRange(min(-20, self.data[['day_k', 'day_d', 'day_j']][(self.ind - self.cfg['显示长度'] + 1):(self.ind + 1)].min().min() * 1.1), max(120, self.data[['day_k', 'day_d', 'day_j']][(self.ind - self.cfg['显示长度'] + 1):(self.ind + 1)].max().max() * 1.1))
        # macd
        chartView_day4 = self.__chartDic['day']['macd']
        series_day4_1, series_day4_2, series_day4_3 = chartView_day4.series()
        setUp, setDown = series_day4_1.barSets()
        if not setUp.count():
            for i in range(self.ind - self.cfg['显示长度'] + 1, self.ind + 1):
                if self.data['day_macd'][i] >= 0:
                    setUp.append(self.data['day_macd'][i])
                    setDown.append(0)
                else:
                    setUp.append(0)
                    setDown.append(self.data['day_macd'][i])
                series_day4_2.append(self.data['ms'][i], self.data['day_dif'][i])
                series_day4_3.append(self.data['ms'][i], self.data['day_dea'][i])
        else:
            setUp.remove(0)
            setDown.remove(0)
            series_day4_2.remove(series_day4_2.at(0))
            series_day4_3.remove(series_day4_3.at(0))
            if self.data['day_macd'][self.ind] >= 0:
                setUp.append(self.data['day_macd'][self.ind])
                setDown.append(0)
            else:
                setUp.append(0)
                setDown.append(self.data['day_macd'][self.ind])
            series_day4_2.append(self.data['ms'][self.ind], self.data['day_dif'][self.ind])
            series_day4_3.append(self.data['ms'][self.ind], self.data['day_dea'][self.ind])
        chartView_day4.axisX().setRange(min_x_day, max_x)
        chartView_day4.axisY().setRange(self.data[['day_dif', 'day_dea', 'day_macd']][(self.ind - self.cfg['显示长度'] + 1):(self.ind + 1)].min().min() * 1.1, self.data[['day_dif', 'day_dea', 'day_macd']][(self.ind - self.cfg['显示长度'] + 1):(self.ind + 1)].max().max() * 1.1)
        # atr
        chartView_day5 = self.__chartDic['day']['atr']
        series_day5_1, series_day5_2, series_day5_3, series_day5_4 = chartView_day5.series()
        candle_day5 = series_day5_1.sets()
        if not candle_day5:
            for i in range(self.ind - self.cfg['显示长度'] + 1, self.ind + 1):
                oneCandle = QCandlestickSet()
                oneCandle.setOpen(self.data['day_open'][i])
                oneCandle.setHigh(self.data['day_high'][i])
                oneCandle.setLow(self.data['day_low'][i])
                oneCandle.setClose(self.data['day_close'][i])
                oneCandle.setTimestamp(self.data['ms'][i])
                series_day5_1.append(oneCandle)
                series_day5_2.append(self.data['ms'][i], self.data['day_atr_high'][i])
                series_day5_3.append(self.data['ms'][i], self.data['day_20'][i])
                series_day5_4.append(self.data['ms'][i], self.data['day_atr_low'][i])
        else:
            series_day5_1.remove(candle_day5[0])
            series_day5_2.remove(series_day5_2.at(0))
            series_day5_3.remove(series_day5_3.at(0))
            series_day5_4.remove(series_day5_4.at(0))
            oneCandle = QCandlestickSet()
            oneCandle.setOpen(self.data['day_open'][self.ind])
            oneCandle.setHigh(self.data['day_high'][self.ind])
            oneCandle.setLow(self.data['day_low'][self.ind])
            oneCandle.setClose(self.data['day_close'][self.ind])
            oneCandle.setTimestamp(self.data['ms'][self.ind])
            series_day5_1.append(oneCandle)
            series_day5_2.append(self.data['ms'][self.ind], self.data['day_atr_high'][self.ind])
            series_day5_3.append(self.data['ms'][self.ind], self.data['day_20'][self.ind])
            series_day5_4.append(self.data['ms'][self.ind], self.data['day_atr_low'][self.ind])
        chartView_day5.axisX().setRange(min_x_day, max_x)
        chartView_day5.axisY().setRange(self.data[['day_low', 'day_atr_low']][(self.ind - self.cfg['显示长度'] + 1):(self.ind + 1)].min().min() * .9, self.data[['day_high', 'day_atr_high']][(self.ind - self.cfg['显示长度'] + 1):(self.ind + 1)].max().max() * 1.1)
        # week
        start_ind_week = max(self.ind % 5, self.ind - 5 * self.cfg['显示长度'] + 5)
        min_x_week = self.data['time'][self.ind - (self.ind - start_ind_week) // 5]
        cnt_week = (self.ind - start_ind_week) // 5 + 1
        if cnt_week != self.cfg['显示长度']:
            barLst = [str(i) for i in range(cnt_week)]
            chart = self.__chartDic['week']['vol']
            series = chart.series()[0]
            axis = chart.axisX(series)
            axis.clear()
            axis.append(barLst)
            axis.setRange(barLst[0], barLst[-1])
            chart = self.__chartDic['week']['macd']
            series = chart.series()[0]
            axis = chart.axisX(series)
            axis.clear()
            axis.append(barLst)
            axis.setRange(barLst[0], barLst[-1])
        chartView_week1 = self.__chartDic['week']['k']
        series_week1_1, series_week1_2, series_week1_3, series_week1_4 = chartView_week1.series()
        series_week1_1.clear()
        series_week1_2.clear()
        series_week1_3.clear()
        series_week1_4.clear()
        for i in range(start_ind_week, self.ind + 1, 5):
            ts = self.data['ms'][self.ind - (self.ind - i) // 5]
            oneCandle = QCandlestickSet()
            oneCandle.setOpen(self.data['week_open'][i])
            oneCandle.setHigh(self.data['week_high'][i])
            oneCandle.setLow(self.data['week_low'][i])
            oneCandle.setClose(self.data['week_close'][i])
            oneCandle.setTimestamp(ts)
            series_week1_1.append(oneCandle)
            series_week1_2.append(ts, self.data['week_5'][i])
            series_week1_3.append(ts, self.data['week_10'][i])
            series_week1_4.append(ts, self.data['week_20'][i])
        chartView_week1.axisX().setRange(min_x_week, max_x)
        chartView_week1.axisY().setRange(self.data[['week_low', 'week_5', 'week_10', 'week_20']][start_ind_week:(self.ind + 1)].min().min() * .9, self.data[['week_high', 'week_5', 'week_10', 'week_20']][start_ind_week:(self.ind + 1)].max().max() * 1.1)
        chartView_week2 = self.__chartDic['week']['vol']
        series_week2 = chartView_week2.series()[0]
        setUp, setDown = series_week2.barSets()
        setUp.remove(0, setUp.count())
        setDown.remove(0, setDown.count())
        for i in range(start_ind_week, self.ind + 1, 5):
            if self.data['week_close'][i] >= self.data['week_open'][i]:
                setUp.append(self.data['week_vol'][i])
                setDown.append(0)
            else:
                setUp.append(0)
                setDown.append(self.data['week_vol'][i])
        chartView_week2.axisX().setRange(min_x_week, max_x)
        chartView_week2.axisY().setRange(0, self.data['week_vol'][start_ind_week:(self.ind + 1)].max() * 1.1)
        chartView_week3 = self.__chartDic['week']['kdj']
        series_week3_1, series_week3_2, series_week3_3 = chartView_week3.series()
        series_week3_1.clear()
        series_week3_2.clear()
        series_week3_3.clear()
        for i in range(start_ind_week, self.ind + 1, 5):
            ts = self.data['ms'][self.ind - (self.ind - i) // 5]
            series_week3_1.append(ts, self.data['week_k'][i])
            series_week3_2.append(ts, self.data['week_d'][i])
            series_week3_3.append(ts, self.data['week_j'][i])
        chartView_week3.axisX().setRange(min_x_week, max_x)
        chartView_week3.axisY().setRange(min(-20, self.data[['week_k', 'week_d', 'week_j']][start_ind_week:(self.ind + 1)].min().min() * 1.1), max(120, self.data[['week_k', 'week_d', 'week_j']][start_ind_week:(self.ind + 1)].max().max() * 1.1))
        chartView_week4 = self.__chartDic['week']['macd']
        series_week4_1, series_week4_2, series_week4_3 = chartView_week4.series()
        setUp, setDown = series_week4_1.barSets()
        setUp.remove(0, setUp.count())
        setDown.remove(0, setDown.count())
        series_week4_2.clear()
        series_week4_3.clear()
        for i in range(start_ind_week, self.ind + 1, 5):
            ts = self.data['ms'][self.ind - (self.ind - i) // 5]
            if self.data['week_macd'][i] >= 0:
                setUp.append(self.data['week_macd'][i])
                setDown.append(0)
            else:
                setUp.append(0)
                setDown.append(self.data['week_macd'][i])
            series_week4_2.append(ts, self.data['week_dif'][i])
            series_week4_3.append(ts, self.data['week_dea'][i])
        chartView_week4.axisX().setRange(min_x_week, max_x)
        chartView_week4.axisY().setRange(self.data[['week_macd', 'week_dif', 'week_dea']][start_ind_week:(self.ind + 1)].min().min() * 1.1, self.data[['week_macd', 'week_dif', 'week_dea']][start_ind_week:(self.ind + 1)].max().max() * 1.1)
        chartView_week5 = self.__chartDic['week']['atr']
        series_week5_1, series_week5_2, series_week5_3, series_week5_4 = chartView_week5.series()
        series_week5_1.clear()
        series_week5_2.clear()
        series_week5_3.clear()
        series_week5_4.clear()
        for i in range(start_ind_week, self.ind + 1, 5):
            ts = self.data['ms'][self.ind - (self.ind - i) // 5]
            oneCandle = QCandlestickSet()
            oneCandle.setOpen(self.data['week_open'][i])
            oneCandle.setHigh(self.data['week_high'][i])
            oneCandle.setLow(self.data['week_low'][i])
            oneCandle.setClose(self.data['week_close'][i])
            oneCandle.setTimestamp(ts)
            series_week5_1.append(oneCandle)
            series_week5_2.append(ts, self.data['week_atr_high'][i])
            series_week5_3.append(ts, self.data['week_20'][i])
            series_week5_4.append(ts, self.data['week_atr_low'][i])
        chartView_week5.axisX().setRange(min_x_week, max_x)
        chartView_week5.axisY().setRange(self.data[['week_low', 'week_atr_low']][start_ind_week:(self.ind + 1)].min().min() * .9, self.data[['week_high', 'week_atr_high']][start_ind_week:(self.ind + 1)].max().max() * 1.1)
        # month
        start_ind_month = max(self.ind % 20, self.ind - 20 * self.cfg['显示长度'] + 20)
        min_x_month = self.data['time'][self.ind - (self.ind - start_ind_month) // 20]
        cnt_month = (self.ind - start_ind_month) // 20 + 1
        if cnt_month != self.cfg['显示长度']:
            barLst = [str(i) for i in range(cnt_month)]
            chart = self.__chartDic['month']['vol']
            series = chart.series()[0]
            axis = chart.axisX(series)
            axis.clear()
            axis.append(barLst)
            axis.setRange(barLst[0], barLst[-1])
            chart = self.__chartDic['month']['macd']
            series = chart.series()[0]
            axis = chart.axisX(series)
            axis.clear()
            axis.append(barLst)
            axis.setRange(barLst[0], barLst[-1])
        chartView_month1 = self.__chartDic['month']['k']
        series_month1_1, series_month1_2, series_month1_3, series_month1_4 = chartView_month1.series()
        series_month1_1.clear()
        series_month1_2.clear()
        series_month1_3.clear()
        series_month1_4.clear()
        for i in range(start_ind_month, self.ind + 1, 20):
            ts = self.data['ms'][self.ind - (self.ind - i) // 20]
            oneCandle = QCandlestickSet()
            oneCandle.setOpen(self.data['month_open'][i])
            oneCandle.setHigh(self.data['month_high'][i])
            oneCandle.setLow(self.data['month_low'][i])
            oneCandle.setClose(self.data['month_close'][i])
            oneCandle.setTimestamp(ts)
            series_month1_1.append(oneCandle)
            series_month1_2.append(ts, self.data['month_5'][i])
            series_month1_3.append(ts, self.data['month_10'][i])
            series_month1_4.append(ts, self.data['month_20'][i])
        chartView_month1.axisX().setRange(min_x_month, max_x)
        chartView_month1.axisY().setRange(self.data[['month_low', 'month_5', 'month_10', 'month_20']][start_ind_month:(self.ind + 1)].min().min() * .9, self.data[['month_high', 'month_5', 'month_10', 'month_20']][start_ind_month:(self.ind + 1)].max().max() * 1.1)
        chartView_month2 = self.__chartDic['month']['vol']
        series_month2 = chartView_month2.series()[0]
        setUp, setDown = series_month2.barSets()
        setUp.remove(0, setUp.count())
        setDown.remove(0, setDown.count())
        for i in range(start_ind_month, self.ind + 1, 20):
            if self.data['month_close'][i] >= self.data['month_open'][i]:
                setUp.append(self.data['month_vol'][i])
                setDown.append(0)
            else:
                setUp.append(0)
                setDown.append(self.data['month_vol'][i])
        chartView_month2.axisX().setRange(min_x_month, max_x)
        chartView_month2.axisY().setRange(0, self.data['month_vol'][start_ind_month:(self.ind + 1)].max() * 1.1)
        chartView_month3 = self.__chartDic['month']['kdj']
        series_month3_1, series_month3_2, series_month3_3 = chartView_month3.series()
        series_month3_1.clear()
        series_month3_2.clear()
        series_month3_3.clear()
        for i in range(start_ind_month, self.ind + 1, 20):
            ts = self.data['ms'][self.ind - (self.ind - i) // 20]
            series_month3_1.append(ts, self.data['month_k'][i])
            series_month3_2.append(ts, self.data['month_d'][i])
            series_month3_3.append(ts, self.data['month_j'][i])
        chartView_month3.axisX().setRange(min_x_month, max_x)
        chartView_month3.axisY().setRange(min(-20, self.data[['month_k', 'month_d', 'month_j']][start_ind_month:(self.ind + 1)].min().min() * .9), max(120, self.data[['month_k', 'month_d', 'month_j']][start_ind_month:(self.ind + 1)].max().max() * 1.1))
        chartView_month4 = self.__chartDic['month']['macd']
        series_month4_1, series_month4_2, series_month4_3 = chartView_month4.series()
        setUp, setDown = series_month4_1.barSets()
        setUp.remove(0, setUp.count())
        setDown.remove(0, setDown.count())
        series_month4_2.clear()
        series_month4_3.clear()
        for i in range(start_ind_month, self.ind + 1, 20):
            ts = self.data['ms'][self.ind - (self.ind - i) // 20]
            if self.data['month_macd'][i] >= 0:
                setUp.append(self.data['month_macd'][i])
                setDown.append(0)
            else:
                setUp.append(0)
                setDown.append(self.data['month_macd'][i])
            series_month4_2.append(ts, self.data['month_dif'][i])
            series_month4_3.append(ts, self.data['month_dea'][i])
        chartView_month4.axisX().setRange(min_x_month, max_x)
        chartView_month4.axisY().setRange(self.data[['month_macd', 'month_dif', 'month_dea']][start_ind_month:(self.ind + 1)].min().min() * 1.1, self.data[['month_macd', 'month_dif', 'month_dea']][start_ind_month:(self.ind + 1)].max().max() * 1.1)
        chartView_month5 = self.__chartDic['month']['atr']
        series_month5_1, series_month5_2, series_month5_3, series_month5_4 = chartView_month5.series()
        series_month5_1.clear()
        series_month5_2.clear()
        series_month5_3.clear()
        series_month5_4.clear()
        for i in range(start_ind_month, self.ind + 1, 20):
            ts = self.data['ms'][self.ind - (self.ind - i) // 20]
            oneCandle = QCandlestickSet()
            oneCandle.setOpen(self.data['month_open'][i])
            oneCandle.setHigh(self.data['month_high'][i])
            oneCandle.setLow(self.data['month_low'][i])
            oneCandle.setClose(self.data['month_close'][i])
            oneCandle.setTimestamp(ts)
            series_month5_1.append(oneCandle)
            series_month5_2.append(ts, self.data['month_atr_high'][i])
            series_month5_3.append(ts, self.data['month_20'][i])
            series_month5_4.append(ts, self.data['month_atr_low'][i])
        chartView_month5.axisX().setRange(min_x_month, max_x)
        chartView_month5.axisY().setRange(self.data[['month_low', 'month_atr_low']][start_ind_month:(self.ind + 1)].min().min() * .9, self.data[['month_high', 'month_atr_high']][start_ind_month:(self.ind + 1)].max().max() * 1.1)
        # self.ind += 1

    def updateInfo(self):
        self.ui.lineEdit_1.setText(f'{self.state["可用资金"]:.2f}')
        self.ui.lineEdit_2.setText(f'{self.state["持仓成本"]:.2f}')
        self.ui.lineEdit_3.setText(f'{self.state["当前盈亏"]:.2f}')
        self.ui.lineEdit_4.setText(f'{self.state["持仓资金"]:.2f}')
        self.ui.lineEdit_5.setText(f'{self.state["持仓数"]:d}')
        self.ui.lineEdit_6.setText(f'{self.state["当前天数"]:d}')
        self.ui.spinBox_buy.setValue(0)
        self.ui.spinBox_sell.setValue(0)

    def clearChart(self):
        for series in self.__chartDic['day']['k'].series():
            series.clear()
        for st in self.__chartDic['day']['vol'].series()[0].barSets():
            st.remove(0, st.count())
        for series in self.__chartDic['day']['kdj'].series():
            series.clear()
        series1, series2, series3 = self.__chartDic['day']['macd'].series()
        for st in series1.barSets():
            st.remove(0, st.count())
        series2.clear()
        series3.clear()
        for series in self.__chartDic['day']['atr'].series():
            series.clear()

    @pyqtSlot()
    def on_pushButton_next_clicked(self):
        if self.ind >= self.length - 1:
            QMessageBox.warning(self, 'warning', '已到最后一日，请重置', QMessageBox.Ok)
        else:
            # get buy&sell info
            buy_cnt = int(self.ui.spinBox_buy.value())
            sell_cnt = int(self.ui.spinBox_sell.value())
            if buy_cnt and sell_cnt:
                QMessageBox.warning(self, 'warning', '仅允许买卖中一种操作，请重新选择', QMessageBox.Ok)
            else:
                self.ind += 1
                if buy_cnt:
                    # 这里可能会因手续费溢出
                    if buy_cnt * self.data['day_open'][self.ind] * 100 > self.state['可用资金']:
                        buy_cnt = int(self.state['可用资金'] / self.data['day_open'][self.ind] / 100)
                    cnt = buy_cnt
                elif sell_cnt:
                    if sell_cnt > self.state['持仓数']:
                        sell_cnt = self.state['持仓数']
                    cnt = -sell_cnt
                else:
                    cnt = 0
                if cnt:
                    # cal money
                    money = cnt * self.data['day_open'][self.ind] * 100
                    # commission
                    commission = (money * .0001) if money > 50000 else 5
                    self.state['可用资金'] -= (money + commission)
                    if self.state['持仓数']:
                        if self.state['持仓数'] + cnt != 0:
                            self.state['持仓成本'] = (self.state['持仓成本'] * self.state['持仓数'] * 100 + money + commission) / (self.state['持仓数'] + cnt) / 100
                        else:
                            self.state['持仓成本'] = 0
                    else:
                        self.state['持仓成本'] = self.data['day_open'][self.ind]
                    self.state['持仓数'] += cnt
                self.state['持仓资金'] = self.state['持仓数'] * self.data['day_close'][self.ind] * 100
                self.state['当前盈亏'] = self.state['可用资金'] + self.state['持仓资金'] - self.cfg['初始资金']
                self.state['当前天数'] += 1
                # update info
                self.updateInfo()
                self.__plot(cnt)

    @pyqtSlot()
    def on_pushButton_reset_clicked(self):
        if self.state['可用资金'] != self.cfg['初始资金']:
            with open('log\\log.txt', 'a', encoding = 'utf-8') as f:
                dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                income = self.state['可用资金'] + self.state['持仓资金'] - self.cfg['初始资金']
                f.write(f'{dt}: 在{self.name}上获得了{income:.2f}元的收益\n')
        self.__initState()
        self.clearChart()
        self.ind, self.data, self.length, self.name = self.__loadData()
        self.updateInfo()
        self.__plot()

if  __name__ == "__main__": 
   app = QApplication(sys.argv) 
   form = QmyMainWindow() 
   form.setWindowState(Qt.WindowMaximized)
   form.show()
   sys.exit(app.exec_())
