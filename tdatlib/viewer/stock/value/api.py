from tdatlib.viewer.stock.value.core import (
    chart
)
from tdatlib.viewer.tools import CD_RANGER, save
from tdatlib.dataset import tools
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd


class value(chart):

    @property
    def fig_overview(self) -> go.Figure:
        fig = make_subplots(
            rows=2,
            cols=2,
            vertical_spacing=0.12,
            horizontal_spacing=0.1,
            subplot_titles=("제품 구성", "멀티 팩터", "자산", "연간 실적"),
            specs=[
                [{"type": "pie"}, {"type": "polar"}],
                [{"type": "bar"}, {"type": "bar"}]
            ]
        )

        # Products
        fig.add_trace(trace=self.pie, row=1, col=1)

        # Multi-Factor
        for trace in self.multi_factor.values():
            fig.add_trace(trace=trace, row=1, col=2)

        # Asset
        for trace in self.asset.values():
            fig.add_trace(trace=trace, row=2, col=1)

        # Profit
        for trace in self.profit.values():
            fig.add_trace(trace=trace, row=2, col=2)

        fig.update_layout(dict(
            title=f'{self.src.label}[{self.src.ticker}] : 제품, 자산 및 실적',
            plot_bgcolor='white',
            margin=dict(l=20, r=20),
            legend=dict(groupclick="toggleitem")
        ))
        fig.update_yaxes(title_text="억원", gridcolor='lightgrey', row=2, col=1)
        fig.update_yaxes(title_text="억원", gridcolor='lightgrey', row=2, col=2)
        for n, annotation in enumerate(fig['layout']['annotations']):
            annotation['x'] = 0 + 0.55 * (n % 2)
            annotation['xanchor'] = 'center'
            annotation['xref'] = 'paper'
        return fig



if __name__ == "__main__":
    from tdatlib.dataset.stock import KR

    path = r'\\kefico\keti\ENT\Softroom\Temp\J.H.Lee'
    # path = str()

    data = KR(ticker='185750', period=3)

    viewer = value(src = data)


    save(fig=viewer.fig_overview, filename=f'{viewer.src.ticker}({viewer.src.label})-V1_제품_팩터_자산_수익', path=path)
    # save(fig=viewer.fig_bollinger_band, filename=f'{viewer.ticker}({viewer.name})-02_볼린저_밴드', path=path)
    # save(fig=viewer.fig_macd, filename=f'{viewer.ticker}({viewer.name})-03_MACD', path=path)
    # save(fig=viewer.fig_rsi, filename=f'{viewer.ticker}({viewer.name})-04_RSI', path=path)


    # for ticker in ["011370", "104480", "048550", "130660", "052690", "045660", "091590", "344820", "014970", "063440", "069540"]:
    #     viewer = technical(ticker=ticker, period=2)
    #     save(fig=viewer.fig_basis, filename=f'{viewer.ticker}({viewer.name})-01_기본_차트', path=path)
    #     save(fig=viewer.fig_bollinger_band, filename=f'{viewer.ticker}({viewer.name})-02_볼린저_밴드', path=path)