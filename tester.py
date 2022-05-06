import tdatlib


kospi = tdatlib.view_stock(ticker='1028', endate='20210525', period=5)
kospi.basic.show()