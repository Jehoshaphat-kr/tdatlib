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
    def tag(self) -> str:
        return f'{self.src.ticker}({self.src.label})'

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

    @property
    def fig_relative(self) -> go.Figure:
        fig = make_subplots(
            rows=2,
            cols=2,
            vertical_spacing=0.12,
            horizontal_spacing=0.1,
            subplot_titles=("상대 수익률", "PER", "EV/EBITDA", "ROE"),
            specs=[
                [{"type": "xy"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "bar"}]
            ]
        )

        # Relative Benchmark
        for trace in self.relative_return.values():
            fig.add_trace(trace=trace, row=1, col=1)

        # Relative PER
        for trace in self.relative_per.values():
            fig.add_trace(trace=trace, row=1, col=2)

        # Relative EV/EBITDA
        for trace in self.relative_ebitda.values():
            fig.add_trace(trace=trace, row=2, col=1)

        # Relative ROE
        for trace in self.relative_roe.values():
            fig.add_trace(trace=trace, row=2, col=2)

        fig.update_layout(dict(
            title=f'<b>{self.src.label}[{self.src.ticker}]</b> : 벤치마크 대비 지표',
            plot_bgcolor='white',
            legend=dict(groupclick="toggleitem")
        ))
        fig.update_yaxes(title_text="상대 수익률[%]", gridcolor='lightgrey', row=1, col=1)
        fig.update_yaxes(title_text="PER[-]", gridcolor='lightgrey', row=1, col=2)
        fig.update_yaxes(title_text="EV/EBITDA[-]", gridcolor='lightgrey', row=2, col=1)
        fig.update_yaxes(title_text="ROE[%]", gridcolor='lightgrey', row=2, col=2)
        fig.update_xaxes(gridcolor='lightgrey')
        for n, annotation in enumerate(fig['layout']['annotations']):
            annotation['x'] = 0 + 0.55 * (n % 2)
            annotation['xanchor'] = 'center'
            annotation['xref'] = 'paper'
        return fig

    @property
    def fig_supply(self) -> go.Figure:
        fig = make_subplots(
            rows=2,
            cols=2,
            vertical_spacing=0.11,
            horizontal_spacing=0.1,
            subplot_titles=("컨센서스", "외국인 보유비중", "차입공매도 비중", "대차잔고 비중"),
            specs=[
                [{"type": "xy"}, {"type": "xy", "secondary_y": True}],
                [{"type": "xy", "secondary_y": True}, {"type": "xy", 'secondary_y': True}]
            ]
        )

        # Consensus
        for trace in self.consensus.values():
            fig.add_trace(trace=trace, row=1, col=1)

        # Foreign Rate
        for key, trace in self.foreign.items():
            fig.add_trace(trace=trace, row=1, col=2, secondary_y=False if key.endswith('비중') else True)

        # Short Sell
        for key, trace in self.short.items():
            fig.add_trace(trace=trace, row=2, col=1, secondary_y=True if key.endswith('종가') else False)

        # Short Balance
        for key, trace in self.balance.items():
            fig.add_trace(trace=trace, row=2, col=2, secondary_y=True if key.endswith('종가') else False)

        fig.update_layout(
            title=f'<b>{self.src.label}[{self.src.ticker}]</b> : 수급 현황',
            plot_bgcolor='white',
            legend=dict(
                # groupclick="toggleitem",
                tracegroupgap=5
            )
        )
        fig.update_yaxes(title_text="주가[원]", showgrid=True, gridcolor='lightgrey', row=1, col=1)
        for row, col in ((1, 2), (2, 1), (2, 2)):
            fig.update_yaxes(title_text="주가[원]", showgrid=True, gridcolor='lightgrey', row=row, col=col,
                             secondary_y=True)
            fig.update_yaxes(title_text="비중[%]", showgrid=False, row=row, col=col, secondary_y=False)
        for n, annotation in enumerate(fig['layout']['annotations']):
            annotation['x'] = 0 + 0.55 * (n % 2)
            annotation['xanchor'] = 'center'
            annotation['xref'] = 'paper'
        return fig



if __name__ == "__main__":
    from tdatlib.dataset.stock import KR

    path = r'\\kefico\keti\ENT\Softroom\Temp\J.H.Lee'
    # path = str()

    data = KR(ticker='010060', period=3)

    viewer = value(src = data)


    save(fig=viewer.fig_overview, filename=f'{viewer.tag}-V1_제품_팩터_자산_수익', path=path)
    save(fig=viewer.fig_relative, filename=f'{viewer.tag}-V2_상대지표', path=path)
    save(fig=viewer.fig_supply, filename=f'{viewer.tag}-V3_수급', path=path)


    # for ticker in ["011370", "104480", "048550", "130660", "052690", "045660", "091590", "344820", "014970", "063440", "069540"]:
    #     viewer = technical(ticker=ticker, period=2)
    #     save(fig=viewer.fig_basis, filename=f'{viewer.ticker}({viewer.name})-01_기본_차트', path=path)
    #     save(fig=viewer.fig_bollinger_band, filename=f'{viewer.ticker}({viewer.name})-02_볼린저_밴드', path=path)