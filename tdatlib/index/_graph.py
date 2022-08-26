import plotly.graph_objects as go


class _trace(object):

    def __init__(self, src):
        self._s = src

    @property
    def bank(self) -> go.Scatter:
        _ = self._s.bank
        return go.Scatter(
            name='KRX은행업',
            x=_.index,
            y=_.종가,
            mode='lines',
            line=dict(
                dash='solid',
            ),
            visible=True,
            showlegend=True,
            xhoverformat='%Y/%m/%d',
            hovertemplate='%{y:.2f} @%{x}'
        )

    @property
    def financial(self) -> go.Scatter:
        _ = self._s.financial
        return go.Scatter(
            name='KRX금융업',
            x=_.index,
            y=_.종가,
            mode='lines',
            line=dict(
                dash='solid',
            ),
            visible=True,
            showlegend=True,
            xhoverformat='%Y/%m/%d',
            hovertemplate='%{y:.2f} @%{x}'
        )

