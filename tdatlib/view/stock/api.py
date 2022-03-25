from tdatlib.view.stock.raw import *
from tdatlib import stock


class analyze:
    def __init__(self, ticker:str, period:int=5, namebook=None):
        name = getName(ticker=ticker, namebook=namebook)
        self.fetch = stock(ticker=ticker, period=period, name=name)
        print(self.fetch.name)
        return

    def show_price_volume(self):
        return


if __name__ == "__main__":
    t_analyze = analyze(ticker='005930')