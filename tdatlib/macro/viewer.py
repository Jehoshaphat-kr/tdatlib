import plotly.graph_objects as go
from tdatlib.macro.core import data


class viewer(object):

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

    def __init__(self, src:data):
        self._s = src
        return

    @property
    def 미국금리(self) -> go.Figure:
        fig = go.Figure()

        fig.add_trace(trace=self._s.trace.미국기준금리)
        fig.add_trace(trace=self._s.trace.미국채3M)
        fig.add_trace(trace=self._s.trace.미국채2Y)
        fig.add_trace(trace=self._s.trace.미국채10Y)
        fig.add_trace(trace=self._s.trace.미국채10Yw인플레이션)
        fig.add_trace(trace=self._s.trace.미국채10Y3M금리차)
        fig.add_trace(trace=self._s.trace.미국채10Y2Y금리차)
        fig.update_layout(
            title=f'미국 기준/시중 금리 및 장단기 금리차',
            plot_bgcolor='white',
            xaxis=dict(
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
                mirror=False,
                rangeselector=self.rangeselector
            ),
            yaxis=dict(
                title='[%]',
                showticklabels=True,
                zeroline=True,
                zerolinewidth=1.2,
                zerolinecolor='grey',
                showgrid=True,
                gridcolor='lightgrey',
                autorange=True,
                showline=True,
                linewidth=0.5,
                linecolor='grey',
                mirror=False
            ),
            xaxis_rangeslider=dict(visible=False)
        )
        return fig