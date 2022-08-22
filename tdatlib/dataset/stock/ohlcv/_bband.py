from tdatlib.dataset.tools import intersect, normalize
from scipy.stats import linregress
import pandas as pd
import numpy as np


def _est_sqz_width(array: pd.Series):
    """
    Estimate <Width Derivative: Volatility Direction> Term
      - Scale from 1 to 10
      - Estimate squeezing direction (slope x r-squared)
    """
    r, _, rsq, _, _ = linregress(x=np.arange(0, len(array), 1), y=array)
    return abs(rsq) * (10 if r < 0 else 2)

def _est_sqz_price(block: pd.DataFrame):
    """
    Estimate <Escaping Price> Term
      - Scale from 1 to 10
      - High price escape from upper band
      - Close price tagging upper band
      - Deducted by x0.1, when (close < open) or (high <= mid)
    """
    dd = 0.1 if block.종가 < block.시가 or block.고가 <= block.mid else 1
    k1 = block.고가 / block.upper
    k2 = block.종가 / block.upper
    return 10 * (1 if k1 >= 1 else k1) * (1 if k2 >= 0.95 else k2) * dd

def _est_sqz_volume(array:pd.Series):
    """
    Deduction factor by <20TD Volume>
      - Scale up to ~ 1 (Deduction Factor)
      - Insufficient volume level will be deducted
    """
    f_t = 0.75
    _avg = array.mean()
    _max = array.max()
    _min = array.min()
    m1 = (f_t - 0.1) / (_avg - _min)
    m2 = (1 - f_t) / (_max - _avg)
    c1 = f_t - m1 * _avg
    c2 = 1 - m2 * _max
    return m1 * array[-1] + c1 if array[-1] <= _avg else m2 * array[-1] + c2

def _est_sqz_level(x:float):
    """
    Reflection factor by <Width Level: Absolute Volatility>
      - Scale up to ~ 1 (Deduction Factor)
      - large width(high volatility) will be deducted
    """
    w_c = 12
    a = -0.9/(100 - w_c)
    return 1 if x <= w_c else a * x + 1 - a * w_c

def _est_band_contain(block: pd.DataFrame):
    """
    Estimate <2SD~1SD Band Contains Price Band(Candlestick)>
    """
    price_h = max([block.종가, block.시가])
    price_l = min([block.종가, block.시가])
    if price_l >= block.upper1sd:
        return 100
    if block.고가 < block.upper1sd or price_h < block.mid:
        return 0
    if price_h < block.upper1sd <= block.고가:
        return 100 * (block.고가 - block.upper1sd) / (block.고가 - block.저가)
    return 100 * (price_h - block.upper1sd) / (price_h - price_l)


class bband(object):

    def __init__(self, parent):
        self.__p = parent

        stp = (self.__p.ohlcv.종가 + self.__p.ohlcv.고가 + self.__p.ohlcv.저가) / 3
        std = stp.rolling(window=20).std(ddof=0)
        self.mid = stp.rolling(window=20).mean()
        self.upper2sd = self.mid + 2*std
        self.lower2sd = self.mid - 2*std
        self.upper1sd = self.mid + 1*std
        self.lower1sd = self.mid - 1*std
        self.width = ((self.upper2sd - self.lower2sd) / self.mid) * 100
        self.signal = (stp - self.lower2sd) / (self.upper2sd - self.lower2sd)

        objs = dict(
            upper=self.upper2sd,
            upper1sd=self.upper1sd,
            mid=self.mid,
            width=self.width
        )
        self.__base = self.__p.ohlcv.join(other=pd.concat(objs=objs, axis=1), how='left')
        return

    @property
    def squeeze_break(self) -> pd.DataFrame:
        win = 5
        est = pd.concat(
            objs=dict(
                t_sqz=self.__base.width.rolling(window=win).apply(lambda arr: _est_sqz_width(arr)),
                t_esc=self.__base.apply(lambda row: _est_sqz_price(row), axis=1),
                k_vol=self.__base.거래량.rolling(window=20).apply(lambda arr: _est_sqz_volume(arr)),
                k_lvl=self.__base.width.apply(lambda x: _est_sqz_level(x)),
            ),
            axis=1
        )
        est['est'] = est.k_lvl * est.k_vol * est.t_sqz * est.t_esc
        return est

    @property
    def est_squeeze_break(self) -> pd.DataFrame:
        win = 5
        if self.__base.empty or len(self.__base) <= 20:
            return pd.DataFrame(
                data=dict(t_sqz=np.nan, t_esc=np.nan, k_vol=np.nan, k_lvl=np.nan, est=np.nan),
                index=[self.__base.index[-1]]
            )
        t_sqz = _est_sqz_width(self.__base.width[-win:])
        t_esc = _est_sqz_price(self.__base.iloc[-1])
        k_vol = _est_sqz_volume(self.__base.거래량[-20:])
        k_lvl = _est_sqz_level(self.__base.width[-1])
        _est = k_lvl * k_vol * t_sqz * t_esc
        return pd.DataFrame(
            data=dict(t_sqz=t_sqz, t_esc=t_esc, k_vol=k_vol, k_lvl=k_lvl, est=_est),
            index=[self.__base.index[-1]]
        )

    @property
    def inner_band(self):
        est = self.__base.apply(lambda row: _est_band_contain(row), axis=1)
        return est


if __name__ == "__main__":
    # pd.set_option('display.expand_frame_repr', False)

    from tdatlib.dataset import market, stock, index
    from tdatlib.viewer.tools import save
    from tqdm import tqdm
    from datetime import datetime
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # print(index.overall().kind)

    # my = stock.KR(ticker='000660', period=2)
    # breakout = my.ohlcv_bband.squeeze_break
    # print(breakout)


    market = market.KR()
    endate = '20220810'
    # kosdaq = market.get_deposit(label='kosdaq')
    # kospi_mid = market.get_deposit(label='1003')
    # kospi_small = market.get_deposit(label='1004')
    # stocks = market.icm[market.icm.index.isin(kosdaq)]
    stocks = market.icm[market.icm.시가총액 > 100000000000]
    stocks = stocks[~stocks.종목명.isna()]
    stocks = stocks[stocks.IPO < datetime.strptime(endate, "%Y%m%d")]

    data = list()
    proc = tqdm(stocks.index)
    for ticker in proc:
        proc.set_description(desc=f'{stocks.loc[ticker, "종목명"]}({ticker}) ...')
        my = stock.KR(ticker=ticker, period=2, endate=endate)
        sqz = my.ohlcv_bband.est_squeeze_break
        _ = my.ohlcv_btr.copy()
        ans_mx = _.iloc[0, -2]
        ans_mn = _.iloc[0, -1]
        print(ans_mx, ans_mn)
        data.append({
            '종목코드': ticker,
            '종목명': stocks.loc[ticker, "종목명"],
            'sqz_term': float(sqz.t_sqz),
            'esc_term': float(sqz.t_esc),
            'vol_fact': float(sqz.k_vol),
            'lvl_fact': float(sqz.k_lvl),
            'sqz_est': float(sqz.est),
            'ans_mx': float(ans_mx),
            'ans_mn': float(ans_mn)
        })
    df = pd.DataFrame(data=data)
    df.to_csv(r'C:\Users\Administrator\Desktop\tdat\test.csv', encoding='euc-kr')

    # my = stock.KR('389260', period=2, endate='20220504')
    # sqz = my.ohlcv_bband.est_squeeze(span='last', win=5)
    # print(sqz)
    # print(sqz.t_sqz)


    # ratio = list()
    # for i in index.deposits(ticker='5412'):
    #     myStock = stock.KR(i, period=10)
    #     print(f'{myStock.label}({i}): ', end='')
    #     myBB = myStock.ohlcv_bband
    #     sqz = myBB.est_squeeze(span='all', win=5)
    #
    #     hist = sqz.join(myStock.ohlcv_btl[['최대', '최소']])
    #     mom = hist[hist.est >= 90].copy()
    #     ach = mom[mom.최대 >= 4]
    #     if mom.empty:
    #         print('N/A')
    #     else:
    #         ratio.append(round(100 * len(ach) / len(mom), 2))
    #         print(f'{round(100 * len(ach) / len(mom), 2)}({len(ach)} / {len(mom)}) for N={len(sqz)}')
    # print(f'전체 정답률: {round(sum(ratio) / len(ratio), 2)}%')


    # my = stock.KR('020150', period=10)
    # est = my.ohlcv_bband.est_squeeze(span='all')
    # df = est.join(my.ohlcv_btl[['최대', '최소']], how='left').dropna()
    # df['label'] = 'eval<br>----<br>sqz: ' + df.t_sqz.astype(str) + '<br>esc: ' + df.t_esc.astype(str) + '<br>vol: ' + df.k_vol.astype(str) + '<br>lvl: ' + df.k_lvl.astype(str)
    #
    # summary = df[df.est >= 95].drop(columns=['label'])
    # achieve = summary[summary.최대 >= 4]
    # print(summary)
    # print(
    #     f'개수: {len(summary)}\n',
    #     f'달성률:{round(100 * len(achieve) / len(summary), 2)}% ({len(achieve)}/{len(summary)})'
    # )
    #
    # fig = go.Figure()
    # scatter = go.Scatter(
    #     name='all',
    #     x=df.est,
    #     y=df.최대,
    #     mode='markers',
    #     marker=dict(symbol='circle', color='royalblue', size=8, opacity=0.7),
    #     meta=[f'{d.year}/{d.month}/{d.day}' for d in df.index],
    #     customdata=df.label,
    #     xhoverformat='.2f',
    #     yhoverformat='.2f',
    #     hovertemplate='%{meta}<br>%{y}%<br>%{customdata}<br>Eval: %{x}<extra></extra>'
    # )
    # fig.add_trace(trace=scatter)
    # save(fig, filename='test-scatter', path=r'\\kefico\keti\ENT\Softroom\Temp\J.H.Lee')
    # fig.show()


    # my = stock.KR('096770', period=10)
    # fig = make_subplots(
    #     rows=4, cols=1,
    #     row_width=[0.2, 0.2, 0.2, 0.4],
    #     shared_xaxes=True,
    #     vertical_spacing=0.02
    # )
    # fig.add_trace(
    #     row=1, col=1,
    #     trace=go.Scatter(
    #         name='width',
    #         x=df.index,
    #         y=df.width,
    #         mode='markers+lines',
    #         customdata=df.label,
    #         xhoverformat='%Y/%m/%d',
    #         yhoverformat='.2f',
    #         hovertemplate='%{x}<br>width: %{y}<br>%{customdata}<extra></extra>'
    #     )
    # )
    # fig.add_trace(
    #     row=2, col=1,
    #     trace=go.Scatter(
    #         name='width_level',
    #         x=df.index,
    #         y=my.ohlcv_bband.eval_breakout.wdir,
    #         xhoverformat='%Y/%m/%d',
    #         yhoverformat='.2f',
    #         hovertemplate='%{x}<br>%{y}<extra></extra>'
    #     )
    # )
    # fig.add_trace(
    #     row=3, col=1,
    #     trace=go.Scatter(
    #         name='d_width',
    #         x=my.ohlcv_bband.width.diff().index,
    #         y=my.ohlcv_bband.width.diff(),
    #         xhoverformat='%Y/%m/%d',
    #         yhoverformat='.2f',
    #         hovertemplate='%{x}<br>%{y}<extra></extra>'
    #     )
    # )
    # fig.add_hline(y=0, row=3, col=1, line_width=0.5, line_dash="dash", line_color="black")
    # fig.add_trace(
    #     row=4, col=1,
    #     trace=go.Scatter(
    #         name='d2_width',
    #         x=my.ohlcv_bband.width.diff().diff().index,
    #         y=my.ohlcv_bband.width.diff().diff(),
    #         xhoverformat='%Y/%m/%d',
    #         yhoverformat='.2f',
    #         hovertemplate='%{x}<br>%{y}<extra></extra>'
    #     )
    # )
    # fig.add_hline(y=0, row=4, col=1, line_width=0.5, line_dash="dash", line_color="black")
    #
    # xaxis = dict(
    #     showgrid=True,
    #     gridcolor='lightgrey',
    #     autorange=True,
    #     tickformat='%Y/%m/%d',
    #     showspikes=True,
    #     spikecolor="black",
    #     spikesnap="cursor",
    #     spikemode="across",
    #     spikethickness=0.5
    # )
    #
    # fig.update_layout(
    #     plot_bgcolor='white',
    #     hovermode="x",
    #     hoverlabel=dict(font=dict(color='white')),
    #     xaxis=xaxis,
    #     xaxis2=xaxis,
    #     xaxis3=xaxis,
    #     xaxis4=xaxis
    # )
    # save(fig, filename='test', path=r'\\kefico\keti\ENT\Softroom\Temp\J.H.Lee')

