import tdatlib


if __name__ == "__main__":
    import pandas as pd
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)


    # Debug
    # print(tdatlib.corporate.ipo_date)
    print(tdatlib.corporate.market_ohlcv)
    # print(tdatlib.corporate.market_cap)
    # print(tdatlib.corporate.market_fundamentals)
    # print(tdatlib.corporate.wics)
    # print(tdatlib.corporate.wi26)

    # print(tdatlib.index.kospi)
    # print(tdatlib.index.kosdaq)
    # print(tdatlib.index.krx)
    # print(tdatlib.index.theme)
    # print(tdatlib.index.display)
    # print(tdatlib.index.deposit_list(ticker='1002'))

    # print(tdatlib.etf.list)
    # print(tdatlib.etf.deposit(ticker='305720'))
    # print(tdatlib.etf.deposit(ticker='305720', date_or_period=30))


    # meta = tdatlib.corporate.ipo_date
    # stock = tdatlib.stock(ticker='000660', meta=meta)
    # stock = tdatlib.stock(ticker='1002')
    # stock = tdatlib.stock(ticker='TSLA')
    # print(stock.name)
    # print(stock.bb)
    # print(stock.summary)
    # print(stock.ohlcv)
    # print(stock.relative_returns)
    # print(stock.relative_returns['3M'].dropna())
    # print(stock.relative_returns['6M'].dropna())
    # print(stock.relative_returns['1Y'].dropna())
    # print(stock.annual_statement)
    # print(stock.quarter_statement)
    # print(stock.multiples)

    # print(stock.returns)
    # print(stock.fiftytwo)

    # print(stock.foreigner)
    # print(stock.foreigner['3M'].dropna())
    # print(stock.foreigner['1Y'].dropna())
    # print(stock.foreigner['3Y'].dropna())
    # print(stock.consensus)
    # print(stock.short_sell)
    # print(stock.short_balance)

    # print(stock.multi_factor)
    # print(stock.comparable_returns)
    # print(stock.comparable_multiples)

    # print(stock.product)
    # print(stock.costs)
