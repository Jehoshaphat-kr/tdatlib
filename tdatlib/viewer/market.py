from tdatlib.interface.market import interface_market
from plotly.subplots import make_subplots
import plotly.graph_objects as go


class view_market(interface_market):

    def view(self, x:str, y:str) -> go.Figure:
        fig = make_subplots(
            rows=2, cols=2,
            row_width=[0.12, 0.88],
            column_width=[0.05, 0.95],
            shared_xaxes='columns',
            shared_yaxes='rows',
            vertical_spacing=0.02,
            horizontal_spacing=0.01
        )

        x_data = self.get_axis_data(col=x, axis='x')
        y_data = self.get_axis_data(col=y, axis='y')
        data = self.baseline.copy()

        trace_main = go.Scatter(
            x=data[x], y=data[y],
            mode='markers',
            marker=dict(color='green', size=frame['size'], symbol='circle', line=dict(width=0)),
            visible=True, showlegend=False, opacity=1.0,
            meta=frame['종목명'], text=frame.index,
            hovertemplate='%{meta}(%{text})<br>' + xlabel + ': %{x:.2f}%<br>' + ylabel + ': %{y:.2f}%<extra></extra>'
        )


        fig.add_trace(trace_main, row=1, col=2)

        return fig