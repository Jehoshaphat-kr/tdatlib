from tdatlib.dataset import stock
from tdatlib.dataset import tools
from tdatlib.dataset import market

my_asset = stock.KR(ticker='000990')
print(my_asset.summary)
# test_data = tools.intersect(my_asset.ta.trend_trix)
# print(test_data)

# my_market = market.KR()
# print(my_market.etf_list)