import datetime
import json
import os
import time
import getpass
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

import numpy as np
import pandas_datareader as pdr
from pandas_datareader.data import get_quote_yahoo

SEP = os.path.sep
TICKER_LIST_FILE = 'US_TICKER_LIST.txt'
WORKING_FOLDER_PATH = 'C:\\pystock'

if os.name != 'nt':
    WORKING_FOLDER_PATH = '/Users/{}/stock-selector'.format(getpass.getuser())

HIST_MAX_DAYS = 255
MA_LIST = [3, 5, 10, 20, 30, 60, 180, 200]  ## moving average checking days
ALERTED_DICT = {}
historical_cache = {}

## loading all tickers file to ALL_TICKERS
with open('{}{}{}'.format(WORKING_FOLDER_PATH, SEP, TICKER_LIST_FILE)) as f:
    us_tickers = f.readlines()
ALL_TICKERS = [x.strip() for x in us_tickers if '/' not in x]


def chunk_list(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))


def get_historical_for_chunk(lst, start, end):
    return pdr.DataReader(lst, data_source='yahoo', start=start, end=end)


def get_N_MA(hist_data):
    ma_info = {}
    for index, row in hist_data.transpose().iterrows():
        if (index[0] == 'Close'):
            ticker_name = index[1]
            ma_avg_list = []
            ma_p25_list = []
            for ma in MA_LIST:
                tmp_list = row.values.tolist()[-1 * ma:]
                ma_avg_list.append({ma: np.percentile(tmp_list, 50)})
                ma_p25_list.append({ma: np.percentile(tmp_list, 25)})
            ma_info[ticker_name] = {'ma_avg_list': ma_avg_list, 'ma_p25_list': ma_p25_list}
    return ma_info


def check_alert_conditions(hist_data, now_prices):
    """
    First version conditions for POC:
    1. comparing current price with past moving-50/25 percentile price list,
       if the price is 9% lower than historical percentile prices, cur_alert_cnt++
    2. threshold for cur_alert_cnt = 5
    """

    ma_info = get_N_MA(hist_data)
    DOWN_PERCENT_THRESHOLD = 9
    alert_msgs = {}
    for index, row in now_prices.iterrows():
        tmp_alert_msgs = []
        ticker_name = index
        cur_price = row.price
        # print(ticker_name, cur_price)
        cur_ma_info = ma_info[ticker_name]
        cur_alert_cnt = 0
        for ma_avg in cur_ma_info['ma_avg_list']:
            k = next(iter(ma_avg))
            v = ma_avg[k]
            down_percent = float("{:.2f}".format((v - cur_price) / v * 100))
            if cur_price < v and down_percent > DOWN_PERCENT_THRESHOLD:
                alert_content = '{} lower than {}-moving-p50 ({}, {} = -{}%)'.format(ticker_name, k, cur_price,
                                                                                     "{:.2f}".format(v), down_percent)
                tmp_alert_msgs.append(alert_content)
                cur_alert_cnt += 1

        for mp25 in cur_ma_info['ma_p25_list']:
            k = next(iter(mp25))
            v = mp25[k]
            down_percent = float("{:.2f}".format((v - cur_price) / v * 100))
            if cur_price < v and down_percent > DOWN_PERCENT_THRESHOLD:
                alert_content = '{} lower than {}-moving-p25 ({}, {} = -{}%)'.format(ticker_name, k, cur_price,
                                                                                     "{:.2f}".format(v), down_percent)
                tmp_alert_msgs.append(alert_content)
                cur_alert_cnt += 1

        if cur_alert_cnt > 5:
            alert_msgs[ticker_name] = tmp_alert_msgs

    return (alert_msgs)


def send_alert(alert_msg):
    print(alert_msg)


def check_alert(idx, task):
    task_start = time.time()
    print(idx, len(task), task)
    now_prices = get_quote_yahoo(task)

    end = datetime.now().strftime("%Y-%m-%d")
    historical_data_key = '{}_{}'.format(end, idx)
    if historical_data_key not in historical_cache:
        hist_data = pdr.DataReader(task, data_source='yahoo', start=datetime.today() - timedelta(days=HIST_MAX_DAYS),
                                   end=end)
        historical_cache[historical_data_key] = hist_data
    else:
        hist_data = historical_cache[historical_data_key]
    alert_msg = check_alert_conditions(hist_data, now_prices)
    print('{} secs used for task {}'.format(int(time.time() - task_start), idx))
    send_alert(alert_msg)
    time.sleep(2)
    return alert_msg


if __name__ == '__main__':
    # Y Finance API limitation: 2000 / hr, 48000/ day

    start = time.time()
    rtn_alert_msgs = {}
    split_tasks = chunk_list(ALL_TICKERS, 60)
    futures = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        for idx, task in enumerate(split_tasks):
            future = executor.submit(check_alert, idx, task)
            futures.append(future)

    for future in as_completed(futures):
        rtn_alert_msgs.update(future.result())

    with open('{}{}rtn_alert_msgs.json'.format(WORKING_FOLDER_PATH, SEP), 'w') as fp:
        json.dump(rtn_alert_msgs, fp)

    with open('{}{}dog_health_chk.txt'.format(WORKING_FOLDER_PATH, SEP), 'w') as fp:
        for k in rtn_alert_msgs:
            fp.write('https://statementdog.com/analysis/{}/stock-health-check\n'.format(k))

    print('Done. {} secs used in total'.format(int(time.time() - start)))
