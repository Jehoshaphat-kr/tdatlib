from tdatlib.fetch.market.series import raw
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.offline as of
import numpy as np


class series(raw):

    def __init__(self, tickers:list or np.array, period:int):
        super().__init__(tickers=tickers, period=period)
        return

    @property
    def fig_returns(self) -> go.Figure:
        fig = go.Figure()

        gaps = ['3M', '6M', '1Y', '2Y', '3Y', '5Y']
        names, data = self.names, self.rel_yield.copy()
        for col in gaps:
            _data = data[col].dropna()
            meta = [f'{d.year}/{d.month}/{d.day}' for d in _data.index]
            for name in names:
                fig.add_trace(go.Scatter(
                    name=name, x=_data.index, y=_data[name], mode='lines', visible=False, showlegend=True,
                    meta=meta, hovertemplate='날짜: %{meta}<br>' + name + ': %{y:.2f}%<extra></extra>'
                ))

        for i in range(len(self.tickers)):
            fig.data[i]['visible'] = True
            fig.data[i]['showlegend'] = True

        steps = []
        for i in range(len(gaps)):
            step = dict(
                method="update",
                args=[{"visible": [False] * len(fig.data)},
                      {"title": f"{gaps[i]} 수익률 비교"}],
                label=gaps[i]
            )
            for j in range(len(self.tickers)):
                step["args"][0]["visible"][len(self.tickers) * i + j] = True
            steps.append(step)

        sliders = [dict(
            name="ddd",
            active=0,
            currentvalue={"prefix": "비교 기간: "},
            pad={"t": 50},
            steps=steps
        )]

        fig.update_layout(
            sliders=sliders
        )

        return fig



if __name__ == "__main__":
    # t_tickers = ['TSLA', 'MSFT', 'GOOG', 'ZM']
    t_tickers = ['005930', '000660', '058470', '000990']

    displayer = series(tickers=t_tickers, period=5)
    displayer.fig_returns.show()