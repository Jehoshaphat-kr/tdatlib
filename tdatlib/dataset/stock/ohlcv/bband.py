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

    def breakout(self):
        base = pd.concat(
            objs=dict(
                high=self.__ohlcv.고가,
                # close=self.__ohlcv.종가,
                vol=self.__ohlcv.거래량,
                vol_mean=self.__ohlcv.거래량.rolling(window=20).mean(),
                width=self.width,
                upper=self.upper,
                # lower=self.lower,
                dir=np.sign(self.width.diff()).rolling(window=5).apply(lambda x:sum(x))
            ),
            axis=1
        )
        return base[(base.dir <= -4) & (base.high >= base.upper) & (base.vol >= base.vol_mean)]


if __name__ == "__main__":
    from tdatlib.dataset import stock
    myStock = stock.KR('123750')
    ohlcv = myStock.ohlcv

    myBB = bollingerband(ohlcv=ohlcv)
    bo = myBB.breakout()
    print(bo.join(myStock.ohlcv_btr[['최대', '최소']], how='left'))
