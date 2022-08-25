import plotly.graph_objects as go


class _trace(object):

    def __init__(self, _src):
        self._src = _src
        return

    # def add_recession(self, fig:go.Figure, market:str='kr') -> go.Figure:
    #     xs = [f['x'][0] for f in fig['data']]
    #     for elem in self._src.recession_kr if market.lower() == 'kr' else self._src.recession_us:
    #         if elem['to'] < min(xs):
    #             continue
    #         fig.add_vrect(
    #             x0=elem['from'].strftime('%Y-%m-%d'), x1=elem['to'].strftime('%Y-%m-%d'), row='all', col='all',
    #             fillcolor="grey", opacity=0.25, line_width=0)
    #     return fig

    @property
    def 미국기준금리(self) -> go.Scatter:
        _ = self._src.미국금리
        return go.Scatter(
            name='US-기준금리',
            x=_.index,
            y=_["기준금리"],
            mode='lines',
            line=dict(
                dash='solid',
            ),
            visible=True,
            showlegend=True,
            xhoverformat='%Y/%m/%d',
            hovertemplate='%{x}<br>%{y:.2f}%<extra></extra>'
        )

    @property
    def 미국채3M(self) -> go.Scatter:
        _ = self._src.미국금리
        return go.Scatter(
            name='US-3개월물금리',
            x=_.index,
            y=_["3개월물"],
            mode='lines',
            line=dict(
                dash='dot',
            ),
            visible='legendonly',
            showlegend=True,
            xhoverformat='%Y/%m/%d',
            hovertemplate='%{x}<br>%{y:.2f}%<extra></extra>'
        )

    @property
    def 미국채2Y(self) -> go.Scatter:
        _ = self._src.미국금리
        return go.Scatter(
            name='US-2년물금리',
            x=_.index,
            y=_["2년물"],
            mode='lines',
            line=dict(
                dash='dot',
            ),
            visible='legendonly',
            showlegend=True,
            xhoverformat='%Y/%m/%d',
            hovertemplate='%{x}<br>%{y:.2f}%<extra></extra>'
        )

    @property
    def 미국채10Y(self) -> go.Scatter:
        _ = self._src.미국금리
        return go.Scatter(
            name='US-10년물금리',
            x=_.index,
            y=_["10년물"],
            mode='lines',
            line=dict(
                dash='dot',
            ),
            visible='legendonly',
            showlegend=True,
            xhoverformat='%Y/%m/%d',
            hovertemplate='%{x}<br>%{y:.2f}%<extra></extra>'
        )

    @property
    def 미국채10Yw인플레이션(self) -> go.Scatter:
        _ = self._src.미국금리
        return go.Scatter(
            name='US-10년물금리(w인플레이션)',
            x=_.index,
            y=_["10년물w기대인플레이션"],
            mode='lines',
            line=dict(
                dash='dot',
            ),
            visible='legendonly',
            showlegend=True,
            xhoverformat='%Y/%m/%d',
            hovertemplate='%{x}<br>%{y:.2f}%<extra></extra>'
        )

    @property
    def 미국채10Y3M금리차(self) -> go.Scatter:
        _ = self._src.미국금리
        return go.Scatter(
            name='US-10년-3개월물금리차',
            x=_.index,
            y=_["10년-3개월금리차"],
            mode='lines',
            line=dict(
                color='#2a344d',
                width=0.8
            ),
            visible=True,
            showlegend=True,
            xhoverformat='%Y/%m/%d',
            hovertemplate='%{x}<br>%{y:.2f}%<extra></extra>'
        )

    @property
    def 미국채10Y2Y금리차(self) -> go.Scatter:
        _ = self._src.미국금리
        return go.Scatter(
            name='US-10년-2년물금리차',
            x=_.index,
            y=_["10년-2년금리차"],
            mode='lines',
            line=dict(
                color='#000000',
                width=0.8
            ),
            visible=True,
            showlegend=True,
            xhoverformat='%Y/%m/%d',
            hovertemplate='%{x}<br>%{y:.2f}%<extra></extra>'
        )