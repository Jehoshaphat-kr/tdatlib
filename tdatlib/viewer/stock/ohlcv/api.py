from tdatlib.dataset.stock.ohlcv import technical as data
from tdatlib.viewer.tools import CD_RANGER, save
from tdatlib.dataset import tools
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd


class technical(object):

    def __init__(self, ticker:str, name:str=str(), period:int=5, endate:str=str()):
        self.ticker = ticker
        self.__tech = data(ticker=ticker, period=period, endate=endate)
        if name:
            self.__tech.label = name
        self.name = self.__tech.label
        return

    def __frm__(self, row_width: list = None):
        row_width = [0.2, 0.8] if not row_width else row_width
        rows = len(row_width)
        fig = make_subplots(
            rows=rows,
            cols=1,
            row_width=row_width,
            shared_xaxes=True,
            vertical_spacing=0.02
        )

        """
        캔들 차트
        """
        if not hasattr(self, '__candle'):
            self.__setattr__(
                '__candle',
                go.Candlestick(
                    name='캔들 차트',
                    x=self.__tech.ohlcv.index,
                    open=self.__tech.ohlcv.시가,
                    high=self.__tech.ohlcv.고가,
                    low=self.__tech.ohlcv.저가,
                    close=self.__tech.ohlcv.종가,
                    visible=True, 
                    showlegend=True, 
                    legendgrouptitle=dict(text='캔들 차트'),
                    increasing_line=dict(color='red'), 
                    decreasing_line=dict(color='royalblue'),
                    xhoverformat='%Y/%-m/%-d',
                    yhoverformat=',' if self.__tech.currency == '원' else '.2f',
                )
            )
        fig.add_trace(trace=self.__getattribute__('__candle'), row=1, col=1)

        """
        주가 차트
        """
        for n, col in enumerate(['시가', '고가', '저가', '종가']):
            if not hasattr(self, f'__{col}'):
                self.__setattr__(
                    f'__{col}',
                    go.Scatter(
                        name=col,
                        x=self.__tech.ohlcv.index,
                        y=self.__tech.ohlcv[col],
                        visible='legendonly',
                        showlegend=True,
                        xhoverformat='%Y/%m/%d',
                        yhoverformat=',' if self.__tech.currency == '원' else '.2f',
                        legendgrouptitle=None if n > 0 else dict(text='주가 차트'),
                        hovertemplate='%{x}<br>' + col + ': %{y}' + self.__tech.currency + '<extra></extra>'
                    )
                )
            fig.add_trace(trace=self.__getattribute__(f'__{col}'), row=1, col=1)

        """
        거래량 차트
        """
        if not hasattr(self, f'__volume'):
            self.__setattr__(
                f'__volume',
                go.Bar(
                    name='거래량',
                    x=self.__tech.ohlcv.index,
                    y=self.__tech.ohlcv.거래량,
                    marker=dict(color=self.__tech.ohlcv.거래량.pct_change().apply(lambda x: 'blue' if x < 0 else 'red')),
                    visible=True,
                    showlegend=False,
                    xhoverformat='%Y/%m/%d',
                    yhoverformat=',',
                    hovertemplate='%{x}<br>거래량: %{y}<extra></extra>'
                )
            )
        fig.add_trace(trace=self.__getattribute__('__volume'), row=2, col=1)

        """
        축 설정
        """
        title, label = '날짜' if rows == 2 else '', True if rows == 2 else False
        fig.update_layout(go.Layout(
            plot_bgcolor='white',
            # legend=dict(groupclick="toggleitem"),
            legend=dict(tracegroupgap=5),
            xaxis=dict(
                title='',
                showticklabels=False,
                tickformat='%Y/%m/%d',
                zeroline=False,
                showgrid=True,
                gridcolor='lightgrey',
                autorange=True,
                showline=True,
                linewidth=1,
                linecolor='grey',
                mirror=False,
                rangeselector=CD_RANGER
            ),
            yaxis=dict(
                title=self.__tech.currency,
                showticklabels=True,
                zeroline=False,
                showgrid=True,
                gridcolor='lightgrey',
                autorange=True,
                showline=True,
                linewidth=0.5,
                linecolor='grey',
                mirror=False
            ),
            xaxis2=dict(
                title=title,
                showticklabels=label,
                tickformat='%Y/%m/%d',
                zeroline=False,
                showgrid=True,
                gridcolor='lightgrey',
                autorange=True,
                showline=True,
                linewidth=1,
                linecolor='grey',
                mirror=False
            ),
            yaxis2=dict(
                title='거래량',
                showticklabels=True,
                zeroline=False,
                showgrid=True,
                gridcolor='lightgrey',
                autorange=True,
                showline=True,
                linewidth=0.5,
                linecolor='grey',
                mirror=False
            ),
            xaxis_rangeslider=dict(visible=False)
        ))
        return fig

    @property
    def fig_basis(self) -> go.Figure:
        fig = self.__frm__()
        
        """
        이동 평균선
        """
        ma = self.__tech.ohlcv_sma
        for n, col in enumerate(ma.columns):
            scatter = go.Scatter(
                name=col,
                x=ma.index,
                y=ma[col],
                visible='legendonly' if col in ['MA5D', 'MA10D', 'MA20D'] else True,
                showlegend=True,
                legendgrouptitle=None if n > 0 else dict(text='이동 평균선'),
                xhoverformat='%Y/%m/%d',
                yhoverformat=',.0f',
                hovertemplate='%{x}<br>' + col + ': %{y}' + self.__tech.currency + '<extra></extra>'
            )
            fig.add_trace(trace=scatter, row=1, col=1)

        """
        노이즈 제거선
        """
        nc = self.__tech.ohlcv_iir
        for n, col in enumerate(nc.columns):
            scatter = go.Scatter(
                name=col,
                x=nc.index,
                y=nc[col],
                visible='legendonly',
                showlegend=True,
                legendgrouptitle=None if n > 0 else dict(text='노이즈 제거선'),
                xhoverformat='%Y/%m/%d',
                yhoverformat=',.0f',
                hovertemplate='%{x}<br>' + col + ': %{y}' + self.__tech.currency + '<extra></extra>'
            )
            fig.add_trace(trace=scatter, row=1, col=1)

        """
        평균 추세선
        """
        trend = self.__tech.ohlcv_trend
        for n, col in enumerate(trend.columns):
            tr = trend[col].dropna()
            dx, dy = (tr.index[-1] - tr.index[0]).days, 100 * (tr[-1] / tr[0] - 1)
            slope = round(dy / dx, 2)
            scatter = go.Scatter(
                name=col.replace('M', '개월').replace('Y', '년'),
                x=tr.index,
                y=tr,
                mode='lines',
                visible='legendonly',
                showlegend=True,
                legendgrouptitle=None if n > 0 else dict(text='평균 추세선'),
                hovertemplate=f'{col} 평균 추세 강도: {slope}[%/days]<extra></extra>'
            )
            fig.add_trace(trace=scatter, row=1, col=1)

        """
        지지/저항선
        """
        bound = self.__tech.ohlcv_bound
        for n, gap in enumerate(['2M', '3M', '6M', '1Y']):
            name = gap.replace('M', '개월').replace('Y', '년')
            resist = go.Scatter(
                name=f'{name}',
                x=bound.index,
                y=bound[gap].resist,
                mode='lines',
                visible='legendonly',
                showlegend=True,
                legendgroup=gap,
                legendgrouptitle=None if n > 0 else dict(text='지지/저항선'),
                line=dict(dash='dot', color='blue'),
                xhoverformat='%Y/%m/%d',
                yhoverformat=',.0f',
                hovertemplate='%{x}<br>저항: %{y}' + self.__tech.currency + '<extra></extra>'
            )
            support = go.Scatter(
                name=f'{name}',
                x=bound.index,
                y=bound[gap].support,
                mode='lines',
                visible='legendonly',
                showlegend=False,
                legendgroup=gap,
                line=dict(dash='dot', color='red'),
                xhoverformat='%Y/%m/%d',
                yhoverformat=',.0f',
                hovertemplate='%{x}<br>지지: %{y}' + self.__tech.currency + '<extra></extra>'
            )
            fig.add_trace(trace=resist, row=1, col=1)
            fig.add_trace(trace=support, row=1, col=1)

        fig.update_layout(
            title=f'{self.__tech.label}({self.ticker}) 기본 차트'
        )
        return fig

    @property
    def fig_bollinger_band(self) -> go.Figure:
        fig = self.__frm__(row_width=[0.15, 0.15, 0.2, 0.5])

        """
        볼린저 밴드
        """
        for n, col, label in [
            (0, 'volatility_bbh', '상단'),
            (1, 'volatility_bbm', 'MA20'),
            (2, 'volatility_bbl', '하단')
        ]:
            if not hasattr(self, f'__{label}'):
                self.__setattr__(
                    f'__{label}',
                    go.Scatter(
                        name='볼린저밴드',
                        x=self.__tech.ohlcv_ta[col].index,
                        y=self.__tech.ohlcv_ta[col],
                        mode='lines',
                        line=dict(color='rgb(184, 247, 212)'),
                        fill='tonexty' if n > 0 else None,
                        visible=True,
                        showlegend=False if n > 0 else True,
                        legendgroup='볼린저밴드',
                        legendgrouptitle=None if n > 0 else dict(text='볼린저밴드'),
                        xhoverformat='%Y/%m/%d',
                        yhoverformat=',.2f',
                        hovertemplate='%{x}<br>' + label + ': %{y}' + self.__tech.currency + '<extra></extra>',
                    )
                )
            fig.add_trace(trace=self.__getattribute__(f'__{label}'), row=1, col=1)

        """
        볼린저 밴드 폭
        """
        if not hasattr(self, f'__bbwidth'):
            self.__setattr__(
                f'__bbwidth',
                go.Scatter(
                    name='폭',
                    x=self.__tech.ohlcv_ta.index,
                    y=self.__tech.ohlcv_ta.volatility_bbw,
                    visible=True,
                    showlegend=True,
                    xhoverformat='%Y/%m/%d',
                    yhoverformat='.2f',
                    hovertemplate='%{x}<br>폭: %{y}%<extra></extra>'
                )
            )
        fig.add_trace(trace=self.__getattribute__(f'__bbwidth'), row=3, col=1)

        """
        볼린저 밴드 신호
        """
        if not hasattr(self, f'__bbsignal'):
            self.__setattr__(
                f'__bbsignal',
                go.Scatter(
                    name='신호',
                    x=self.__tech.ohlcv_ta.index,
                    y=self.__tech.ohlcv_ta.volatility_bbp,
                    visible=True,
                    showlegend=True,
                    xhoverformat='%Y/%m/%d',
                    yhoverformat='.2f',
                    hovertemplate='%{x}<br>신호: %{y}<extra></extra>'
                )
            )
        fig.add_trace(trace=self.__getattribute__(f'__bbsignal'), row=4, col=1)

        mx = self.__tech.ohlcv_ta.volatility_bbp.max()
        mn = self.__tech.ohlcv_ta.volatility_bbp.min()
        fig.add_hrect(y0=1, y1=mx, line_width=0, fillcolor='red', opacity=0.2, row=4, col=1)
        fig.add_hrect(y0=mn, y1=0, line_width=0, fillcolor='green', opacity=0.2, row=4, col=1)

        if not hasattr(self, f'__bbpoint'):
            self.__setattr__(f'__bbpoint', tools.intersect(self.__tech.ohlcv_ta.volatility_bbp, 0))

        pt = self.__getattribute__(f'__bbpoint').rise.dropna()
        rise_sig = go.Scatter(
            name='저점-상승',
            x=pt.index,
            y=pt,
            mode='markers',
            marker=dict(symbol='triangle-up', color='lightgreen'),
            visible='legendonly',
            showlegend=True,
            legendgroup='매수지점',
            hoverinfo='skip'
        )
        fig.add_trace(trace=rise_sig, row=4, col=1)

        price = self.__tech.ohlcv[self.__tech.ohlcv.index.isin(pt.index)]
        rise_price = go.Scatter(
            name='저점-상승',
            x=price.index,
            y=price.종가,
            mode='markers',
            marker=dict(symbol='triangle-up', color='lightgreen'),
            visible='legendonly',
            showlegend=False,
            legendgroup='매수지점',
            xhoverformat='%Y/%m/%d',
            yhoverformat=',' if self.__tech.currency == '원' else ',.2f',
            hovertemplate='%{x}<br>매수가: %{y}<extra></extra>'
        )
        fig.add_trace(trace=rise_price, row=1, col=1)
        
        fig.update_layout(
            title=f'{self.__tech.label}({self.ticker}) 볼린저 밴드',
            xaxis3=dict(
                title='',
                showticklabels=False,
                tickformat='%Y/%m/%d',
                zeroline=False,
                showgrid=True,
                gridcolor='lightgrey',
                autorange=True,
                showline=True,
                linewidth=1,
                linecolor='grey',
                mirror=False
            ),
            yaxis3=dict(
                title='폭[%]',
                showticklabels=True,
                zeroline=False,
                showgrid=True,
                gridcolor='lightgrey',
                autorange=True,
                showline=True,
                linewidth=0.5,
                linecolor='grey',
                mirror=False
            ),
            xaxis4=dict(
                title='날짜',
                showticklabels=True,
                tickformat='%Y/%m/%d',
                zeroline=False,
                showgrid=True,
                gridcolor='lightgrey',
                autorange=True,
                showline=True,
                linewidth=1,
                linecolor='grey',
                mirror=False
            ),
            yaxis4=dict(
                title='신호',
                showticklabels=True,
                zeroline=False,
                showgrid=True,
                gridcolor='lightgrey',
                autorange=True,
                showline=True,
                linewidth=0.5,
                linecolor='grey',
                mirror=False
            ),
        )
        return fig


if __name__ == "__main__":

    # path = r'\\kefico\keti\ENT\Softroom\Temp\J.H.Lee'
    path = str()


    viewer = technical(ticker='306620')
    save(fig=viewer.fig_basis, filename=f'{viewer.ticker}({viewer.name})-01_기본_차트', path=path)
    save(fig=viewer.fig_bollinger_band, filename=f'{viewer.ticker}({viewer.name})-02_볼린저_밴드', path=path)