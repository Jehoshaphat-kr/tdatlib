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
            vertical_spacing=0,
            horizontal_spacing=0
        )

        x_data = self.get_axis_data(col=x, axis='x')
        y_data = self.get_axis_data(col=y, axis='y')
        data = self.baseline.copy()

        trace_main = go.Scatter(
            name='main',
            x=data[x], y=data[y],
            mode='markers',
            marker=dict(
                color=data.섹터색상,
                size=data.시가총액/4,
                symbol='circle', 
                line=dict(width=0)
            ),
            opacity=1.0,
            visible=True,
            showlegend=False,
            meta=data.종목명,
            customdata=data.섹터,
            text=data.index,
            hovertemplate='%{meta}(%{text})<br>업종: %{customdata}<br>' + x + ': %{x:.2f}%<br>' + y + ': %{y:.2f}%<extra></extra>'
        )

        trace_x = go.Scatter(
            name='x',
            x=x_data[x], y=x_data.xnorm,
            mode='markers',
            marker=dict(
                color=x_data.섹터색상,
                line=dict(width=0)
            ),
            visible=True,
            showlegend=False,
            meta=x_data.종목명,
            customdata=x_data.섹터,
            text=x_data.index,
            hovertemplate='%{meta}(%{text})<br>업종: %{customdata}<br>' + x + ': %{x:.2f}%<extra></extra>'
        )

        trace_y = go.Scatter(
            name='y',
            x=y_data.ynorm, y=y_data[y],
            mode='markers',
            marker=dict(
                color=y_data.섹터색상,
                line=dict(width=0)
            ),
            visible=True,
            showlegend=False,
            meta=y_data.종목명,
            customdata=y_data.섹터,
            text=y_data.index,
            hovertemplate='%{meta}(%{text})<br>업종: %{customdata}<br>' + y + ': %{y:.2f}%<extra></extra>'
        )

        fig.add_trace(trace_main, row=1, col=2)
        fig.add_trace(trace_y, row=1, col=1)
        fig.add_trace(trace_x, row=2, col=2)
        fig.update_layout(
            title=f'시장 산포도 x: {x} / y: {y}',
            plot_bgcolor='white',
            yaxis=dict(
                title=f'{y}',
                autorange=True,
                showticklabels=True,
                showgrid=True,
                gridcolor='lightgrey',
                gridwidth=0.5,
                zeroline=True,
                zerolinecolor='lightgrey',
                zerolinewidth=0.5,
            ),
            xaxis2=dict(
                autorange=True,
                showgrid=True,
                gridcolor='lightgrey',
                gridwidth=0.5,
                zeroline=True,
                zerolinecolor='lightgrey',
                zerolinewidth=0.5,
                showline=True,
                linewidth=1,
                linecolor='grey',
                mirror=False
            ),
            yaxis2=dict(
                autorange=True,
                showgrid=True,
                gridcolor='lightgrey',
                gridwidth=0.5,
                zeroline=True,
                zerolinecolor='lightgrey',
                zerolinewidth=0.5,
                linewidth=1,
                linecolor='grey',
                mirror=False
            ),
            xaxis4=dict(
                title=f'{x}',
                showticklabels=True,
                showgrid=True,
                gridcolor='lightgrey',
                gridwidth=0.5,
                zeroline=True,
                zerolinecolor='lightgrey',
                zerolinewidth=0.5,
                autorange=True,
            ),
        )
        return fig

if __name__ == "__main__":

    viewer = view_market()

    viewer.view(x='PER', y='R1D').show()