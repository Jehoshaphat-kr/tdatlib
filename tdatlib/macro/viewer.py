import plotly.graph_objects as go


class viewer(object):
    def __init__(self, src):
        self._s = src
        return

    @property
    def 미국금리(self) -> go.Figure:
        fig = go.Figure()


        fig.add_trace(trace=self._s.trace.미국채10Y)
        fig.add_trace(trace=self._s.trace.미국채2Y)
        fig.add_trace(trace=self._s.trace.미국채10Y2Y금리차)
        fig.update_layout(

        )
        return fig