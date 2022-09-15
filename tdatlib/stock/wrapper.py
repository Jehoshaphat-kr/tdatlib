from tdatlib.stock.fnguide import _fnguide


class krx(object):

    def __init__(self, ticker:str):
        self.fnguide = _fnguide(ticker=ticker)
        return




if __name__ == "__main__":
    kr = krx(ticker='316140')
    print(kr.fnguide.Products)