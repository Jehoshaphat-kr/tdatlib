from tdatlib.view.compare.datum import datum
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.offline as of
import numpy as np


colors = [
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf'   # blue-teal
]

rangeselector = dict(
    buttons=list([
        dict(count=1, label="1m", step="month", stepmode="backward"),
        dict(count=3, label="3m", step="month", stepmode="backward"),
        dict(count=6, label="6m", step="month", stepmode="backward"),
        dict(count=1, label="YTD", step="year", stepmode="todate"),
        dict(count=1, label="1y", step="year", stepmode="backward"),
        dict(step="all")
    ])
)

class compare(datum):

    def __init__(self, tickers:list or np.array, period:int):
        super().__init__(tickers=tickers, period=period)
        return

    def save(self, fig:go.Figure, title:str, path:str=str(), tag:bool=True):
        """
        차트 저장
        :param fig: 차트 오브젝트
        :param title: 파일명
        :param path:
        :param tag: 티커 종류 표시 유무
        """
        if tag:
            title += f"-{'_'.join(self.names)}"
        if path:
            of.plot(fig, filename=f'{path}/{title}.html', auto_open=False)
        else:
            of.plot(fig, filename=f'{archive.desktop}/{title}.html', auto_open=False)
        return

    @property
    def fig_returns(self) -> go.Figure:
        """ 기간별 수익률 비교 """
        fig = go.Figure()

        gaps = ['3M', '6M', '1Y', '2Y', '3Y', '5Y']
        tags = ['3개월', '6개월', '1년', '2년', '3년', '5년']
        names, data, price = self.names, self.rel_yield.copy(), self.price.copy()
        for c, col in enumerate(gaps):
            for n, name in enumerate(names):
                _data = data[(col, name)].dropna()
                meta = [f'{d.year}/{d.month}/{d.day}' for d in _data.index]
                p = price[price.index >= _data.index[0]][name]
                fig.add_trace(go.Scatter(
                    name=name, x=_data.index, y=_data, visible=False if c else True, showlegend=True,
                    mode='lines', line=dict(color=colors[n]), meta=meta, customdata=p,
                    hovertemplate='날짜: %{meta}<br>' + name + ': %{y:.2f}%<br>가격: %{customdata:,}원<extra></extra>'
                ))

        steps = []
        for i in range(len(gaps)):
            step = dict(
                method="update",
                args=[{"visible": [False] * len(fig.data)}, {"title": f"{tags[i]}({gaps[i]}) 수익률 비교"}],
                label=tags[i]
            )
            for j in range(len(self.tickers)):
                step["args"][0]["visible"][len(self.tickers) * i + j] = True
            steps.append(step)
        sliders = [dict(active=0, currentvalue={"prefix": "비교 기간: "}, pad={"t": 50}, steps=steps)]

        fig.update_layout(
            title=f'{tags[0]}({gaps[0]}) 수익률 비교',
            plot_bgcolor='white',
            sliders=sliders,
            xaxis=dict(title='날짜', showgrid=True, gridcolor='lightgrey', autorange=True),
            yaxis=dict(title='수익률[%]', showgrid=True, gridcolor='lightgrey', autorange=True,
                       zeroline=True, zerolinecolor='grey', zerolinewidth=1)
        )
        return fig

    @property
    def fig_drawdown(self) -> go.Figure:
        """ 기간별 낙폭 비교 """
        fig = go.Figure()

        gaps = ['3M', '6M', '1Y', '2Y', '3Y', '5Y']
        tags = ['3개월', '6개월', '1년', '2년', '3년', '5년']
        names, data, price = self.names, self.rel_drawdown.copy(), self.price.copy()
        for c, col in enumerate(gaps):
            for n, name in enumerate(names):
                _data = data[(col, name)].dropna()
                meta = [f'{d.year}/{d.month}/{d.day}' for d in _data.index]
                p = price[price.index >= _data.index[0]][name]
                fig.add_trace(go.Scatter(
                    name=name, x=_data.index, y=_data, visible=False if c else True, showlegend=True,
                    mode='lines', line=dict(color=colors[n]), meta=meta, customdata=p,
                    hovertemplate='날짜: %{meta}<br>' + name + ': %{y:.2f}%<br>가격: %{customdata:,}원<extra></extra>'
                ))

        steps = []
        for i in range(len(gaps)):
            step = dict(
                method="update",
                args=[{"visible": [False] * len(fig.data)}, {"title": f"{tags[i]}({gaps[i]}) 낙폭 비교"}],
                label=tags[i]
            )
            for j in range(len(self.tickers)):
                step["args"][0]["visible"][len(self.tickers) * i + j] = True
            steps.append(step)
        sliders = [dict(active=0, currentvalue={"prefix": "비교 기간: "}, pad={"t": 50}, steps=steps)]

        fig.update_layout(
            title=f'{tags[0]}({gaps[0]}) 낙폭 비교',
            plot_bgcolor='white',
            sliders=sliders,
            xaxis=dict(title='날짜', showgrid=True, gridcolor='lightgrey', autorange=True),
            yaxis=dict(title='낙폭[%]', showgrid=True, gridcolor='lightgrey', autorange=True,
                       zeroline=True, zerolinecolor='grey', zerolinewidth=1)
        )
        return fig

    @property
    def fig_rsi(self) -> go.Figure:
        """ RSI / STOCH-RSI 비교 """
        fig = make_subplots(
            rows=2, cols=1, vertical_spacing=0.11, subplot_titles=("RSI", "Stochastic-RSI"), shared_xaxes=True,
            specs=[[{"type": "xy"}], [{"type": "xy"}]]
        )

        data = self.rel_rsi.copy()
        for n, col in enumerate(data.columns):
            d = data[col].dropna()
            fig.add_trace(go.Scatter(
                name=f'RSI: {col}', x=d.index, y=d, mode='lines', line=dict(color=colors[n]),
                meta=[f'{_.year}/{_.month}/{_.day}' for _ in d.index],
                hovertemplate='날짜: %{meta}<br>' + col + ': %{y:.2f}%<extra></extra>'
            ), row=1, col=1)
        fig.add_hrect(y0=70, y1=80, line_width=0, fillcolor='red', opacity=0.2, row=1, col=1)
        fig.add_hrect(y0=20, y1=30, line_width=0, fillcolor='green', opacity=0.2, row=1, col=1)

        data = self.rel_stoch.copy()
        for n, col in enumerate(data.columns):
            d = data[col].dropna()
            fig.add_trace(go.Scatter(
                name=f'S-RSI: {col}', x=d.index, y=d, mode='lines', line=dict(color=colors[n]),
                meta=[f'{_.year}/{_.month}/{_.day}' for _ in d.index],
                hovertemplate='날짜: %{meta}<br>' + col + ': %{y:.2f}[%]<extra></extra>'
            ), row=2, col=1)
        fig.add_hrect(y0=80, y1=100, line_width=0, fillcolor='red', opacity=0.2, row=2, col=1)
        fig.add_hrect(y0=0, y1=20, line_width=0, fillcolor='green', opacity=0.2, row=2, col=1)

        fig.update_layout(
            title=f'RSI 비교',
            plot_bgcolor='white',
            xaxis=dict(title='', showgrid=True, gridcolor='lightgrey', autorange=True, rangeselector=rangeselector),
            xaxis2=dict(title='날짜', showgrid=True, gridcolor='lightgrey', autorange=True),
            yaxis=dict(title='RSI[%]', showgrid=True, gridcolor='lightgrey', autorange=True),
            yaxis2=dict(title='S-RSI[-]', showgrid=True, gridcolor='lightgrey', autorange=True)
        )
        return fig

    @property
    def fig_cci_vortex(self) -> go.Figure:
        """ CCI / VORTEX 비교 """
        fig = make_subplots(
            rows=2, cols=1, vertical_spacing=0.11, subplot_titles=("CCI", "VORTEX"), shared_xaxes=True,
            specs=[[{"type": "xy"}], [{"type": "xy"}]]
        )

        data = self.rel_cci.copy()
        for n, col in enumerate(data.columns):
            d = data[col].dropna()
            fig.add_trace(go.Scatter(
                name=f'CCI: {col}', x=d.index, y=d, mode='lines', line=dict(color=colors[n]),
                meta=[f'{_.year}/{_.month}/{_.day}' for _ in d.index],
                hovertemplate='날짜: %{meta}<br>' + col + ': %{y:.2f}[-]<extra></extra>'
            ), row=1, col=1)
        fig.add_hrect(y0=200, y1=400, line_width=0, fillcolor='red', opacity=0.2, row=1, col=1)
        fig.add_hrect(y0=100, y1=200, line_width=0, fillcolor='brown', opacity=0.2, row=1, col=1)
        fig.add_hrect(y0=-200, y1=-100, line_width=0, fillcolor='lightgreen', opacity=0.4, row=1, col=1)
        fig.add_hrect(y0=-400, y1=-200, line_width=0, fillcolor='green', opacity=0.2, row=1, col=1)

        data = self.rel_vortex.copy()
        for n, col in enumerate(data.columns):
            d = data[col].dropna()
            fig.add_trace(go.Scatter(
                name=f'VORTEX: {col}', x=d.index, y=d, mode='lines', line=dict(color=colors[n]),
                meta=[f'{_.year}/{_.month}/{_.day}' for _ in d.index],
                hovertemplate='날짜: %{meta}<br>' + col + ': %{y:.2f}[-]<extra></extra>'
            ), row=2, col=1)

        fig.update_layout(
            title=f'CCI / Vortex',
            plot_bgcolor='white',
            xaxis=dict(title='', showgrid=True, gridcolor='lightgrey', autorange=True, rangeselector=rangeselector),
            xaxis2=dict(title='날짜', showgrid=True, gridcolor='lightgrey', autorange=True),
            yaxis=dict(title='CCI[%]', showgrid=True, gridcolor='lightgrey', autorange=True,
                       zeroline=True, zerolinecolor='grey', zerolinewidth=0.5),
            yaxis2=dict(title='Vortex[-]', showgrid=True, gridcolor='lightgrey', autorange=True,
                        zeroline=True, zerolinecolor='grey', zerolinewidth=0.5)
        )
        return fig

    @property
    def fig_mfi_bb(self) -> go.Figure:
        """ MFI / Bollinger 비교 """
        fig = make_subplots(
            rows=2, cols=1, vertical_spacing=0.11, subplot_titles=("MFI", "Bollinger Signal"), shared_xaxes=True,
            specs=[[{"type": "xy"}], [{"type": "xy"}]]
        )

        data = self.rel_mfi.copy()
        for n, col in enumerate(data.columns):
            d = data[col].dropna()
            fig.add_trace(go.Scatter(
                name=f'MFI: {col}', x=d.index, y=d, mode='lines', line=dict(color=colors[n]),
                meta=[f'{_.year}/{_.month}/{_.day}' for _ in d.index],
                hovertemplate='날짜: %{meta}<br>' + col + ': %{y:.2f}[%]<extra></extra>'
            ), row=1, col=1)
        fig.add_hrect(y0=80, y1=100, line_width=0, fillcolor='red', opacity=0.2, row=1, col=1)
        fig.add_hline(y=90, line_width=0.5, line_dash="dash", line_color="black", row=1, col=1)
        fig.add_hrect(y0=0, y1=20, line_width=0, fillcolor='lightgreen', opacity=0.4, row=1, col=1)
        fig.add_hline(y=10, line_width=0.5, line_dash="dash", line_color="black", row=1, col=1)

        data = self.rel_bb.copy()
        for n, col in enumerate(data.columns):
            d = data[col].dropna()
            fig.add_trace(go.Scatter(
                name=f'BB-Sig: {col}', x=d.index, y=d, mode='lines', line=dict(color=colors[n]),
                meta=[f'{_.year}/{_.month}/{_.day}' for _ in d.index],
                hovertemplate='날짜: %{meta}<br>' + col + ': %{y:.2f}[-]<extra></extra>'
            ), row=2, col=1)
        fig.add_hrect(y0=1, y1=1.5, line_width=0, fillcolor='red', opacity=0.2, row=2, col=1)
        fig.add_hrect(y0=-0.5, y1=0, line_width=0, fillcolor='lightgreen', opacity=0.4, row=2, col=1)

        fig.update_layout(
            title=f'MFI / Bollinger-Signal',
            plot_bgcolor='white',
            xaxis=dict(title='', showgrid=True, gridcolor='lightgrey', autorange=True, rangeselector=rangeselector),
            xaxis2=dict(title='날짜', showgrid=True, gridcolor='lightgrey', autorange=True),
            yaxis=dict(title='MFI[%]', showgrid=True, gridcolor='lightgrey', autorange=True,
                       zeroline=True, zerolinecolor='grey', zerolinewidth=0.5),
            yaxis2=dict(title='BB-Sig[-]', showgrid=True, gridcolor='lightgrey', autorange=True)
        )
        return fig

    @property
    def fig_sharpe_ratio(self) -> go.Figure:
        """ 샤프 비율 비교 """
        fig = go.Figure()

        gaps = ['3M', '6M', '1Y', '2Y', '3Y', '5Y']
        tags = ['3개월', '6개월', '1년', '2년', '3년', '5년']
        data = self.rel_sharpe_ratio.copy()
        for t, gap in enumerate(gaps):
            for n, name in enumerate(self.names):
                d = data[name]
                fig.add_trace(go.Scatter(
                    name=name, x=[d.loc[gap, 'risk']], y=[d.loc[gap, 'cagr']], mode='markers',
                    visible=False if t else True, showlegend=True,
                    marker=dict(color=colors[n], size=d.loc[gap, 'cap'], symbol='circle'),
                    hovertemplate=name + '<br>변동성: %{x:.2f}%<br>CAGR: %{y:.2f}%<br><extra></extra>'
                ))

            loc = [data[name].loc[gap, 'risk'] for name in self.names]
            x = [0.8*min(loc), 1.2 * max(loc)]
            fig.add_trace(go.Scatter(
                name='기준선', x=x, y=[0.8 * x[0], 0.8 * x[1]], mode='lines',
                line=dict(color='black', dash='dot', width=0.5), hoverinfo='skip',
                visible=False if t else True, showlegend=False
            ))

        steps = []
        for i in range(len(gaps)):
            step = dict(
                method="update",
                args=[{"visible": [False] * len(fig.data)}, {"title": f"{tags[i]}({gaps[i]}) 샤프비율 비교"}],
                label=tags[i]
            )
            for j in range(len(self.tickers) + 1):
                step["args"][0]["visible"][(len(self.tickers) + 1) * i + j] = True
            steps.append(step)
        sliders = [dict(active=0, currentvalue={"prefix": "비교 기간: "}, pad={"t": 50}, steps=steps)]
        fig.update_layout(
            title=f'{tags[0]}({gaps[0]}) 수익률 비교',
            plot_bgcolor='white',
            sliders=sliders,
            xaxis=dict(title='변동성[%]', showgrid=True, gridcolor='lightgrey', autorange=True),
            yaxis=dict(title='CAGR[%]', showgrid=True, gridcolor='lightgrey', autorange=True,
                       zeroline=True, zerolinecolor='grey', zerolinewidth=1)
        )
        return fig

    @property
    def fig_profit(self) -> go.Figure:
        """ 발표 기준 수익성 비교 """
        fig = make_subplots(
            rows=2, cols=2, vertical_spacing=0.11, horizontal_spacing=0.1,
            subplot_titles=("영업이익률", "배당수익률", "ROA(Return On Asset)", "ROE(Return On Equity)"),
            specs=[[{"type": "bar"}, {"type": "bar"}], [{"type": "bar"}, {"type": "bar"}]]
        )

        profit = self.rel_profit.copy()
        for n, col in enumerate(profit.columns):
            fig.add_trace(go.Bar(
                name=col, x=profit.index, y=profit[col], visible=True, showlegend=False,
                texttemplate='%{y:.2f}%', hoverinfo='skip'
            ), row=1 if n < 2 else 2, col=2 if n % 2 else 1)
        fig.update_layout(dict(title=f'[발표 기준] 수익성 비교', plot_bgcolor='white'))
        fig.update_yaxes(title_text="[%]", showgrid=True, gridcolor='lightgrey')
        return fig

    @property
    def fig_profit_estimate(self) -> go.Figure:
        """ 전망치 수익성 비교 """
        fig = make_subplots(
            rows=2, cols=2, vertical_spacing=0.11, horizontal_spacing=0.1,
            subplot_titles=("영업이익률", "배당수익률", "ROA(Return On Asset)", "ROE(Return On Equity)"),
            specs=[[{"type": "bar"}, {"type": "bar"}], [{"type": "bar"}, {"type": "bar"}]]
        )

        profit = self.rel_profit_estimate.copy()
        for n, col in enumerate(profit.columns):
            fig.add_trace(go.Bar(
                name=col, x=profit.index, y=profit[col], visible=True, showlegend=False,
                texttemplate='%{y:.2f}%', hoverinfo='skip'
            ), row=1 if n < 2 else 2, col=2 if n % 2 else 1)
        fig.update_layout(dict(title=f'[전망치] 수익성 비교', plot_bgcolor='white'))
        fig.update_yaxes(title_text="[%]", showgrid=True, gridcolor='lightgrey')
        return fig



if __name__ == "__main__":
    from datetime import datetime
    from tdatlib import archive
    import os

    # t_tickers = ['TSLA', 'MSFT', 'GOOG', 'ZM']
    # t_tickers = ['1028', '005930', '000660', '058470', '000990']
    # t_tickers = ['005930', '000660', '058470', '000990']
    t_tickers = ['005930', '000660', '000990', '058470', '005290', '357780']

    t_compare = compare(tickers=t_tickers, period=5)
    # t_compare.fig_returns.show()


    path = os.path.join(archive.desktop, f'tdat/{datetime.today().strftime("%Y-%m-%d")}')
    if not os.path.isdir(path):
        os.makedirs(path)

    # t_compare.save(t_compare.fig_returns, title='수익률 비교', path=path)
    # t_compare.save(t_compare.fig_drawdown, title='낙폭 비교', path=path)
    # t_compare.save(t_compare.fig_rsi, title='RSI 비교', path=path)
    # t_compare.save(t_compare.fig_cci_vortex, title='CCI_VORTEX', path=path)
    # t_compare.save(t_compare.fig_mfi_bb, title='MFI_B-Sig', path=path)
    # t_compare.save(t_compare.fig_sharpe_ratio, title='샤프비율 비교', path=path)
    # t_compare.save(t_compare.fig_profit, title='발표기준_수익성 비교', path=path)
    t_compare.save(t_compare.fig_profit_estimate, title='전망치_수익성 비교', path=path)