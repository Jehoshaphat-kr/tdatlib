from tdatlib.macro.freq.data import data
import plotly.graph_objects as go


class trace(object):

    def __init__(self, _src:data):
        self._src = _src
        return

    def add_recession(self, fig:go.Figure, market:str='kr') -> go.Figure:
        xs = [f['x'][0] for f in fig['data']]
        for elem in self._src.recession_kr if market.lower() == 'kr' else self._src.recession_us:
            if elem['to'] < min(xs):
                continue
            fig.add_vrect(
                x0=elem['from'].strftime('%Y-%m-%d'), x1=elem['to'].strftime('%Y-%m-%d'), row='all', col='all',
                fillcolor="grey", opacity=0.25, line_width=0)
        return fig

    @property
    def us10y_treasury(self) -> go.Scatter:
        _ = self._src.fred(symbols=self._src.US10년물금리)
        return go.Scatter(
            name='US-10년물금리',
            x=_.index,
            y=_[self._src.US10년물금리],
            visible='legendonly',
            showlegend=True,
            xhoverformat='%Y/%m/%d',
            hovertemplate='%{x}<br>%{y}<extra></extra>'
        )

    @property
    def us2y_treasury(self) -> go.Scatter:
        _ = self._src.fred(symbols=self._src.US2년물금리)
        return go.Scatter(
            name='US-2년물금리',
            x=_.index,
            y=_[self._src.US2년물금리],
            visible='legendonly',
            showlegend=True,
            xhoverformat='%Y/%m/%d',
            hovertemplate='%{x}<br>%{y:.2f}%<extra></extra>'
        )

    @property
    def us10y2y_treasury(self) -> go.Scatter:
        _ = self._src.fred(symbols=self._src.US장단기금리차10Y2Y)
        return go.Scatter(
            name='US-장단기금리차10Y2Y',
            x=_.index,
            y=_[self._src.US장단기금리차10Y2Y],
            showlegend=True,
            xhoverformat='%Y/%m/%d',
            hovertemplate='%{x}<br>%{y:.2f}%<extra></extra>'
        )



if __name__ == "__main__":

    trace = trace()
    trace.period = 90

    fig = go.Figure()

    fig.add_trace(trace=trace.us10y_treasury)
    fig.add_trace(trace=trace.us2y_treasury)
    fig.add_trace(trace=trace.us10y2y_treasury)
    fig = trace.add_recession(fig=fig, market='us')

    fig.show()