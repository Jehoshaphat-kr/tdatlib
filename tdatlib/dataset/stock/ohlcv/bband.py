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
            self.high = self.mid + std * mstd
            self.low = self.mid + std * mstd
            self.width = ((self.high - self.low) / self.mid) * 100
            self.signal = (ohlcv[base] - self.low) / (self.high - self.low)
        else:
            self.mid = self.__ta.volatility_bbm
            self.high = self.__ta.volatility_bbh
            self.low = self.__ta.volaility_bbl
            self.width = self.__ta.volatility_bbw
            self.signal = self.__ta.volatility_bbp
        return

    def breakout(self):
        sign = np.sign(self.width.diff())
        a = sign.rolling(window=5).apply(lambda x:sum(x))
        print(a)
        # ind = pd.concat(objs={'d_width':self.width.diff(), 'close':self.__ohlcv.종가}, axis=1).dropna()[6:]
        # for w, c in zip(ind.d_width, ind.close):
        #     w
        return


if __name__ == "__main__":
    from tdatlib.dataset import stock
    myStock = stock.KR('005960')
    ohlcv = myStock.ohlcv

    myBB = bollingerband(ohlcv=ohlcv)
    myBB.breakout()
