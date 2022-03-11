from pykrx import stock as krx
from datetime import datetime, timedelta
from pytz import timezone
from tqdm import tqdm
import pandas as pd
import time


pd.set_option('display.expand_frame_repr', False)
kst = datetime.now(timezone('Asia/Seoul'))
t_today = kst.strftime("%Y%m%d")
t_stamp = [(kst - timedelta(days)).strftime("%Y%m%d") for days in [7, 30, 91, 183, 365]]


# indices = ['1028', '1003', '1004', '2203', '2003']
# tickers = krx.get_etf_ticker_list(t_today)
# for index in tqdm(indices):
#     tickers += krx.get_index_portfolio_deposit_file(index, date=t_today)
# tickers = list(set(tickers))
# print(len(tickers), tickers)


# key = '상장주식수'
# cap_curr = krx.get_market_cap_by_ticker(date=t_today, market='ALL')
# cap_prev = krx.get_market_cap_by_ticker(date=t_stamp[-1], market='ALL')
# n_stock = pd.concat(objs={f'{key}_전':cap_prev[key], f'{key}_후':cap_curr[key]}, axis=1).dropna()
# n_stock[f'변동비율'] = n_stock[f'{key}_후'] / n_stock[f'{key}_전']
# n_stock = n_stock[n_stock.index.isin(tickers)]
# n_split = n_stock[n_stock[f'{key}_전'] != n_stock[f'{key}_후']]
# n_stock.to_csv(r'./split.csv', encoding='euc-kr', index=True)
# print(n_stock)
# print(n_split)

# tic = time.perf_counter()
# objs = {}
# objs['R1D'] = krx.get_market_ohlcv(t_today, market='ALL')['등락률']
# for label, t in zip(['R1W', 'R1M', 'R3M', 'R6M', 'R1Y'], t_stamp):
#     objs[label] = krx.get_market_price_change(t, t_today, market='ALL')['등락률']
# df = pd.concat(objs=objs, axis=1, ignore_index=False)
# df.to_csv(r'./test.csv', encoding='euc-kr', index=True)
# print(df)


ticker = '251370'
ohlcv = krx.get_market_ohlcv_by_date(fromdate=t_stamp[-1], todate=t_today, ticker=ticker)['종가'].tolist()
market_curr = krx.get_market_ohlcv_by_ticker(date=t_today, market='ALL')['종가']
market_prev = krx.get_market_ohlcv_by_ticker(date=t_stamp[-1], market='ALL')['종가']
market = pd.concat({'전':market_prev, '후':market_curr}, axis=1, ignore_index=False)
market_r = round(100 * (market['후']/market['전'] - 1), 2)

print(krx.get_stock_major_changes(ticker=ticker))
print(f"정답-변동: {round(100 * (ohlcv[-1]/ohlcv[0] - 1), 2)}%")
print(f"대조-변동: {market_r[ticker]}%")