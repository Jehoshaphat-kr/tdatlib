from tdatlib.viewer.stock.value.core import chart
from tdatlib.viewer.tools import save
from plotly.subplots import make_subplots
from tqdm import tqdm
import plotly.graph_objects as go


class value(chart):

    def saveall(self, path:str=str()):
        proc = tqdm([
            (self.fig_overview, '개요'),
            (self.fig_supply, '수급'),
            (self.fig_multiple, '투자배수'),
            (self.fig_relative, '상대지표'),
            (self.fig_cost, '주요비용')
        ])
        for n, (fig, name) in enumerate(proc):
            proc.set_description(desc=f'{self.tag}: {name}')
            save(fig=fig, filename=f'{self.tag}-F{str(n + 1).zfill(2)}_{name}', path=path)
        return

    @property
    def tag(self) -> str:
        return f'{self.src.label}({self.src.ticker})'

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
        fig.add_trace(trace=self.trace_product, row=1, col=1)

        # Multi-Factor
        for trace in self.trace_factor.values():
            fig.add_trace(trace=trace, row=1, col=2)

        # Asset
        for trace in self.trace_asset.values():
            fig.add_trace(trace=trace, row=2, col=1)

        # Profit
        for trace in self.trace_profit.values():
            fig.add_trace(trace=trace, row=2, col=2)

        fig.update_layout(dict(
            title=f'<b>{self.tag}</b> : 제품, 자산 및 실적',
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
        for trace in self.trace_rr.values():
            fig.add_trace(trace=trace, row=1, col=1)

        # Relative PER
        for trace in self.trace_rp.values():
            fig.add_trace(trace=trace, row=1, col=2)

        # Relative EV/EBITDA
        for trace in self.trace_re.values():
            fig.add_trace(trace=trace, row=2, col=1)

        # Relative ROE
        for trace in self.trace_roe.values():
            fig.add_trace(trace=trace, row=2, col=2)

        fig.update_layout(dict(
            title=f'<b>{self.tag}</b> : 벤치마크 대비 지표',
            plot_bgcolor='white',
            legend=dict(
                tracegroupgap=5,
                # groupclick="toggleitem"
            ),
            xaxis=dict(tickformat='%Y/%m/%d'),
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
        for trace in self.trace_consensus.values():
            fig.add_trace(trace=trace, row=1, col=1)

        # Foreign Rate
        for key, trace in self.trace_foreign.items():
            fig.add_trace(trace=trace, row=1, col=2, secondary_y=False if key.endswith('비중') else True)

        # Short Sell
        for key, trace in self.trace_short.items():
            fig.add_trace(trace=trace, row=2, col=1, secondary_y=True if key.endswith('종가') else False)

        # Short Balance
        for key, trace in self.trace_balance.items():
            fig.add_trace(trace=trace, row=2, col=2, secondary_y=True if key.endswith('종가') else False)

        fig.update_layout(
            title=f'<b>{self.tag}</b> : 수급 현황',
            plot_bgcolor='white',
            legend=dict(
                # groupclick="toggleitem",
                tracegroupgap=5
            ),
        )
        fig.update_xaxes(tickformat='%Y/%m/%d')
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

    @property
    def fig_cost(self) -> go.Figure:
        fig = make_subplots(
            rows=2,
            cols=2,
            vertical_spacing=0.11,
            horizontal_spacing=0.1,
            subplot_titles=("매출 원가", "판관비", "R&D투자 비중", "부채율"),
            specs=[
                [{"type": "xy", "secondary_y": True}, {"type": "xy", "secondary_y": True}],
                [{"type": "xy", "secondary_y": True}, {"type": "xy", 'secondary_y': True}]
            ]
        )

        # General Cost
        for n, trace in enumerate(self.trace_cost.values()):
            fig.add_trace(trace=trace, row = n // 2 + 1, col = n % 2 + 1)

        # Debt
        fig.add_trace(trace=self.trace_debt, row=2, col=2)

        fig.update_layout(dict(title=f'{self.tag}: 비용과 부채', plot_bgcolor='white'))
        for row, col in ((1, 1), (1, 2), (2, 1), (2, 2)):
            fig.update_yaxes(title_text="[%]", showgrid=True, gridcolor='lightgrey', row=row, col=col)
        for n, annotation in enumerate(fig['layout']['annotations']):
            annotation['x'] = 0 + 0.55 * (n % 2)
            annotation['xanchor'] = 'center'
            annotation['xref'] = 'paper'
        return fig

    @property
    def fig_multiple(self) -> go.Figure:
        fig = make_subplots(
            rows=2,
            cols=2,
            vertical_spacing=0.11,
            horizontal_spacing=0.1,
            subplot_titles=("EPS / PER(3Y)", "BPS / PBR(3Y)", "PER BAND", "PBR BAND"),
            specs=[
                [{"type": "xy", "secondary_y": True}, {"type": "xy", "secondary_y": True}],
                [{"type": "xy", "secondary_y": False}, {"type": "xy", 'secondary_y': False}]
            ]
        )

        # PER / EPS
        for key, trace in self.trace_per.items():
            fig.add_trace(trace=trace, row=1, col=1, secondary_y=True if key == 'PER' else False)

        # PBR / BPS
        for key, trace in self.trace_pbr.items():
            fig.add_trace(trace=trace, row=1, col=2, secondary_y=True if key == 'PBR' else False)

        # PER BAND
        for trace in self.trace_perband.values():
            fig.add_trace(trace=trace, row=2, col=1)

        # PBR BAND
        for trace in self.trace_pbrband.values():
            fig.add_trace(trace=trace, row=2, col=2)

        fig.update_layout(dict(
            title=f'<b>{self.tag}</b> : PER / PBR',
            plot_bgcolor='white',
            legend=dict(groupclick="toggleitem"),
            xaxis=dict(tickformat='%Y/%m/%d'),
            xaxis2=dict(tickformat='%Y/%m/%d')
        ))
        for row, col in ((1, 1), (1, 2), (2, 1), (2, 2)):
            fig.update_yaxes(title_text="KRW[원]", showgrid=True, gridcolor='lightgrey', row=row, col=col,
                             secondary_y=False)
            fig.update_yaxes(title_text="배수[-]", showgrid=False, row=row, col=col, secondary_y=True)
        for n, annotation in enumerate(fig['layout']['annotations']):
            annotation['x'] = 0 + 0.55 * (n % 2)
            annotation['xanchor'] = 'center'
            annotation['xref'] = 'paper'
        return fig



if __name__ == "__main__":
    from tdatlib.dataset.stock import KR

    # path = r'\\kefico\keti\ENT\Softroom\Temp\J.H.Lee'
    path = str()

    data = KR(ticker='253450', period=3)

    viewer = value(src = data)

    viewer.saveall()
    # save(fig=viewer.fig_overview, filename=f'{viewer.tag}-V1_제품_팩터_자산_수익', path=path)
    # save(fig=viewer.fig_relative, filename=f'{viewer.tag}-V2_상대지표', path=path)
    # save(fig=viewer.fig_supply, filename=f'{viewer.tag}-V3_수급', path=path)
    # save(fig=viewer.fig_cost, filename=f'{viewer.tag}-V4_비용_부채', path=path)
    # save(fig=viewer.fig_multiple, filename=f'{viewer.tag}-V5_투자배수', path=path)
