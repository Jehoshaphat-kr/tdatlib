from tdatlib.dataset import market, index
from tdatlib.viewer import stock
from tdatlib.tdef import labels, crypto
from tqdm import tqdm
import pandas as pd
import os, random

DESKTOP = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
DEBUG_TREEMAP  = False
DEBUG_MARKET   = False
DEBUG_INDEX    = False
DEBUG_STOCK_KR = False
DEBUG_STOCK_US = False
DEBUG_GROUP    = True

if DEBUG_TREEMAP:
    krx = market.KR()
    treemap = krx.treemap(category='WICS', sub_category='1028')
    print(treemap)

if DEBUG_MARKET:
    krx = market.KR()
    krx.isetfokay()

if DEBUG_INDEX:
    idx = index.overall()
    print(idx.kind)

if DEBUG_STOCK_KR:
    viewer = stock.KR(
        # ticker=labels.우리금융지주,
        ticker=labels.아프리카TV,
        period=3
    )
    viewer.saveall()

if DEBUG_STOCK_US:
    viewer = stock.US(
        ticker='TSLA',
        period=5
    )
    viewer.saveall()

if DEBUG_GROUP:
    # for ticker in labels.은행:
    #     myStock = stock.KR(ticker=ticker, period=3)
    #     myStock.saveall()

    crypto = crypto()
    data = list()

    process = tqdm(
        crypto.tickers
        # random.sample(population=crypto.ALL, k=20)
        # ['BTC', 'ETH', 'SOL', 'ADA', 'USDT', 'XRP', 'DOGE']
    )
    for ticker in process:
        process.set_description(desc=f'{ticker} ...')
        viewer = stock.US(
            ticker=f'{ticker}-USD',
            period=3,
            endate='20220801'
        )
        sqz = viewer.technical.src.ohlcv_bband.est_squeeze_break
        data.append({
            '종목코드': ticker,
            '종목명': ticker,
            'sqz_term': float(sqz.t_sqz),
            'esc_term': float(sqz.t_esc),
            'vol_fact': float(sqz.k_vol),
            'lvl_fact': float(sqz.k_lvl),
            'sqz_est': float(sqz.est)
        })
    df = pd.DataFrame(data=data)
    df.to_csv(r'C:\Users\Administrator\Desktop\tdat\test.csv', encoding='euc-kr')
    print(df)