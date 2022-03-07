from tdatlib.fetch import corporate, index, etf
from tdatlib.market.maps import treemap
from tdatlib.market import market
from tdatlib.stock.analyze import stock

def get_root(file:str) -> str:
    import os
    path = os.path.dirname(file)
    return os.path.join(path[:path.find('tdatlib')], 'tdatlib')