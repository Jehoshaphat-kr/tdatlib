from tdatlib.dataset.tools import intersect
import pandas as pd
import numpy as np


class bollingerband(object):

    def __init__(
        self,
        ohlcv:pd.DataFrame,
        ohlcv_ta:pd.DataFrame=pd.DataFrame(),
        base:str='종가',
        window:int=20,
        std:int=2
    ):
        self.__ohlcv = ohlcv
        # self.__base = base
        # self.__window = window
        # self.__std = std
        self.__ta = pd.DataFrame() if not (base == '종가' and window == 20 and std == 2) else ohlcv_ta

        if self.__ta.empty:
            mstd = ohlcv[base].rolling(window=window).std(ddof=0)
            self.mid = ohlcv[base].rolling(window=window).mean()
            self.upper = self.mid + std * mstd
            self.lower = self.mid - std * mstd
            self.width = ((self.upper - self.lower) / self.mid) * 100
            self.signal = (ohlcv[base] - self.lower) / (self.upper - self.lower)
        else:
            self.mid = self.__ta.volatility_bbm
            self.upper = self.__ta.volatility_bbh
            self.lower = self.__ta.volaility_bbl
            self.width = self.__ta.volatility_bbw
            self.signal = self.__ta.volatility_bbp
        return

    def history_breakout(self, mode:str='mild'):
        """
        :param mode: 상승점 판별 참조 가격
            - mild(default) : 고가
            - strict        : 종가
            - manipulate    : (a x 고가) + (b x 저가) + (c x 종가)
        :return:
        """
        def func(row):
            mid = (row.고가 + row.저가)/2
            a, b = (0.2, 0.3) if row.종가 < mid else (0.3, 0.2)
            return a*row.고가 + b*row.저가 + 0.5*row.종가

        objs = dict(
            vol=self.__ohlcv.거래량,
            vol_mean=self.__ohlcv.거래량.rolling(window=20).mean(),
            width=self.width,
            upper=self.upper,
            dir=np.sign(self.width.diff()).rolling(window=5).apply(lambda x:sum(x))
        )
        if mode == 'mild':
            objs.update(dict(price=self.__ohlcv.고가))
        elif mode == 'strict':
            objs.update(dict(price=self.__ohlcv.종가))
        elif mode == 'manipulate':
            objs.update(dict(price=self.__ohlcv.apply(lambda row:func(row), axis=1)))
        else:
            raise KeyError

        base = pd.concat(objs=objs, axis=1)
        return base[(base.dir <= -4) & (base.price >= base.upper) & (base.vol >= base.vol_mean)]

    def flag_breakout(self):
        return all([
            self.__ohlcv.거래량[-1] >= self.__ohlcv.거래량[-20:].mean(),
            np.sign(self.width.diff()[-5:]).sum() <= -4,
            self.__ohlcv.고가[-1] >= self.upper[-1]
        ])


if __name__ == "__main__":
    from tdatlib.dataset import market, stock
    from tqdm import tqdm

    market = market.KR()
    kosdaq = market.get_deposit(label='kosdaq')
    stocks = market.icm[market.icm.index.isin(kosdaq)]

    data = list()
    proc = tqdm(stocks.index)
    for ticker in proc:
        proc.set_description(desc=f'{stocks.loc[ticker, "종목명"]}({ticker}) ...')
        equity = stock.KR(ticker=ticker)
        bollinger = bollingerband(ohlcv=equity.ohlcv)
        data.append({
            '종목코드': ticker,
            '종목명': stocks.loc[ticker, "종목명"],
            '플래그': bollinger.flag_breakout()
        })
    df = pd.DataFrame(data=data)
    df.to_csv(r'./test.csv', encoding='euc-kr')
    # myStock = stock.KR('053800', period=10)
    #
    # ohlcv = myStock.ohlcv
    # myBB = bollingerband(ohlcv=ohlcv)
    # bo = myBB.history_breakout()
    # print(bo.join(myStock.ohlcv_btr[['최대', '최소']], how='left'))
    #
    # bo = myBB.history_breakout(mode='strict')
    # print(bo.join(myStock.ohlcv_btr[['최대', '최소']], how='left'))
    #
    # bo = myBB.history_breakout(mode='manipulate')
    # print(bo.join(myStock.ohlcv_btr[['최대', '최소']], how='left'))