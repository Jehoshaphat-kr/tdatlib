from tdatlib.dataset.tools import intersect, normalize
from scipy.stats import linregress
import pandas as pd
import numpy as np


class _bband(object):

    def __init__(self, parent):
        self.__par = parent

        stp = (self.__par.ohlcv.종가 + self.__par.ohlcv.고가 + self.__par.ohlcv.저가) / 3
        std = stp.rolling(window=20).std(ddof=0)
        mid = self.mid = stp.rolling(window=20).mean()
        self.upper2sd, self.lower2sd = mid + 2*std, mid - 2*std
        self.upper1sd, self.lower1sd = mid + 1*std, mid - 1*std
        self.width = ((self.upper2sd - self.lower2sd) / mid) * 100
        self.signal = (stp - self.lower2sd) / (self.upper2sd - self.lower2sd)
        return

    @staticmethod
    def _est_sqz_width(array: pd.Series):
        """
        Estimate <Width Derivative: Volatility Direction> Term
          - Scale from 1 to 10
          - Estimate escaping price(candle) from squeezed - risk-free - width
        """
        x = len(array[array < 0]) / len(array)
        return 1.67 * x + 1 if x < 0.6 else 20 * x - 10

    @staticmethod
    def _est_sqz_price(block: pd.DataFrame):
        """
        Estimate <Escaping Price> Term
          - Scale from 1 to 10
          - High price escape from upper band
          - Deducted by x0.1, when close < open
        """
        x = block.고가 / block.upper
        return (0.1 if block.종가 < block.시가 else 1) * (1 if x >= 1 else x) * 10

    @staticmethod
    def _est_sqz_volume(array:pd.Series):
        """
        Reflection factor by <Volume>
          - Scale up to ~ 1 (Deduction Factor)
          - Insufficient volume level will be deducted
        """
        x = array[-1] / array.mean()
        return 1 if x >= 1 else x

    @staticmethod
    def _est_sqz_level(x:float):
        """
        Reflection factor by <Width Level: Absolute Volatility>
          - Scale up to ~ 1 (Deduction Factor)
          - large width(high volatility) will be deducted
        """
        return 1 if x <= 20 else (-1/80) * x + 1.25

    @property
    def est_squeeze(self):
        basis = pd.concat(
            objs=dict(
                시가=self.__par.ohlcv.시가,
                고가=self.__par.ohlcv.고가,
                종가=self.__par.ohlcv.종가,
                volume=self.__par.ohlcv.거래량,
                upper=self.upper2sd,
                width=self.width,
            ),
            axis=1
        )
        t_sqz = np.sign(basis.width.diff()).rolling(window=8).apply(lambda arr: self._est_sqz_width(arr))
        t_esc = basis.apply(lambda row: self._est_sqz_price(row), axis=1)
        k_vol = basis.volume.rolling(window=20).apply(lambda arr: self._est_sqz_volume(arr))
        k_lvl = basis.width.apply(lambda x:self._est_sqz_level(x))
        est = k_lvl * k_vol * t_sqz * t_esc
        # est = k_vol * t_sqz * t_esc
        return pd.concat(
            objs=dict(
                t_sqz=t_sqz,
                t_esc=t_esc,
                k_vol=k_vol,
                k_lvl=k_lvl,
                est=est
            ),
            axis=1
        )


    @property
    def flag_breakout(self) -> bool:
        return all([
            self.__par.ohlcv.거래량[-1] >= self.__par.ohlcv.거래량[-20:].mean(),
            np.sign(self.width.diff()[-5:]).sum() <= -4,
            self.__par.ohlcv.고가[-1] >= 0.95 * (self.upper2sd[-1] - self.lower2sd[-1]) + self.lower2sd[-1]
        ])


if __name__ == "__main__":
    from tdatlib.dataset import market, stock, index
    from tqdm import tqdm
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # market = market.KR()
    # kosdaq = market.get_deposit(label='kosdaq')
    # stocks = market.icm[market.icm.index.isin(kosdaq)]
    #
    # data = list()
    # proc = tqdm(stocks.index)
    # for ticker in proc:
    #     proc.set_description(desc=f'{stocks.loc[ticker, "종목명"]}({ticker}) ...')
    #     equity = stock.KR(ticker=ticker)
    #     bollinger = bollingerband(ohlcv=equity.ohlcv)
    #     data.append({
    #         '종목코드': ticker,
    #         '종목명': stocks.loc[ticker, "종목명"],
    #         '플래그': bollinger.flag_breakout()
    #     })
    # df = pd.DataFrame(data=data)
    # df.to_csv(r'./test.csv', encoding='euc-kr')

    # pd.set_option('display.expand_frame_repr', False)
    # print(index.overall().kind)
    # for i in index.deposits(ticker='5412'):
    #     myStock = stock.KR(i, period=10)
    #     print(f'{myStock.label}({i}): ', end='')
    #     myBB = _bband(parent=myStock)
    #     print(f'{myBB.hist_breakout_perf}%')


    # my = stock.KR('096770', period=10)
    # df = my.ohlcv_bband.width.copy()
    #
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
    #         x=my.ohlcv_bband.width.index,
    #         y=my.ohlcv_bband.width,
    #         xhoverformat='%Y/%m/%d',
    #         yhoverformat='.2f',
    #         hovertemplate='%{x}<br>%{y}<extra></extra>'
    #     )
    # )
    # fig.add_trace(
    #     row=2, col=1,
    #     trace=go.Scatter(
    #         name='width_level',
    #         x=my.ohlcv_bband.eval_breakout.wdir.index,
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
    # fig.show()

    my = stock.KR('066970', period=10)
    est = my.ohlcv_bband.est_squeeze
    df = est.join(my.ohlcv_btr[['최대', '최소']], how='left')

    summary = df[df.est >= 100]
    achieve = summary[summary.최대 >= 5]
    print(summary)
    print(
        f'개수: {len(summary)}\n',
        f'달성률:{round(100 * len(achieve) / len(summary), 2)}% ({len(achieve)}/{len(summary)})'
    )

    fig = go.Figure()
    scatter = go.Scatter(
        name='all',
        x=df.est,
        y=df.최대,
        mode='markers',
        marker=dict(symbol='circle', color='royalblue', size=8, opacity=0.7),
        meta=[f'{d.year}/{d.month}/{d.day}' for d in df.index],
        xhoverformat='.2f',
        yhoverformat='.2f',
        hovertemplate='%{meta}<br>%{y} / %{x}<extra></extra>'
    )
    fig.add_trace(trace=scatter)
    fig.show()