import warnings

warnings.filterwarnings(action = 'ignore')

import pandas as pd
import akshare as ak
import time
import datetime
import os

class Down:
    def __init__(self):
        self.path = 'data'
        today = datetime.datetime.now()
        self.end = f'{today.year}{today.month:02}{today.day:02}'
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        self.code_lst = pd.read_csv('config\\code.csv')['code'].values
    def download(self):
        for i in range(len(self.code_lst)):
            code = f'{self.code_lst[i]:06}'
            target_path = os.path.join(self.path, f'{code}.csv')
            print(f'\r下载进度: {(i + 1) / len(self.code_lst) * 100:.3f}%', end = '')
            try:
                if not os.path.exists(target_path):
                    data = ak.stock_zh_a_hist(symbol = code, period = 'daily', end_date = self.end, adjust = 'qfq')
                    data.to_csv(target_path, index = False)
                else:
                    data_r = pd.read_csv(target_path)
                    start = data_r['日期'][len(data_r) - 1].replace('-', '')
                    data_a = ak.stock_zh_a_hist(symbol = code, period = 'daily', start_date = start, end_date = self.end, adjust = 'qfq')
                    data = data_r.append(data_a.iloc[1:, :])
                    data.to_csv(target_path, index = False)
            except Exception as e:
                print('something is wrong:', e)
            finally:
                time.sleep(.5)

if __name__ == '__main__':
    d5 = Down()
    d5.download()