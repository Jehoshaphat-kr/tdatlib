from tdatlib.interface.treemap.frame import interface_treemap
from tdatlib.interface.market import interface_market
from tdatlib.viewer.common import save
from plotly.subplots import make_subplots
import plotly.graph_objects as go


class view_market(interface_market):

    def treemap(
            self,
            category:str,
            sub_category:str,
            key:str='R1D',
    ):
        """
        :param category     : 지도 종류
        :param sub_category : 하위 분류
        :param key          : 키 값
        :param save         : 저장 여부
        :return:
        """
        unit = '' if key in ['PER', 'PBR'] else '%'
        hdlr = interface_treemap(category=category, sub_category=sub_category)
        frame = hdlr.mapframe

        fig = go.Figure()
        fig.add_trace(go.Treemap(
            ids=frame['ID'],
            labels=frame['종목명'],
            parents=frame['분류'],
            values=frame['크기'],
            marker=dict(colors=frame[f'C{key}']),
            textfont=dict(color='#ffffff'),
            textposition='middle center',
            texttemplate='%{label}<br>%{text}' + unit,
            meta=frame['시가총액'],
            customdata=frame['종가'],
            text=frame[key],
            branchvalues='total',
            opacity=0.9,
            hovertemplate='%{label}<br>시총: %{meta}<br>종가: %{customdata}<br>' + key + ': %{text}' + unit + '<extra></extra>'
        ))

        title = f'[{hdlr.cat} / {hdlr.mapname}]: {self.td_date} 종가 기준 {key}'
        fig.update_layout(title=title)
        return fig

    def scatter(self, x:str, y:str) -> go.Figure:
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
        fig.add_vline(x=x_data[x].mean(), row=1, col=2, line_width=0.5, line_dash="dash", line_color="black")
        fig.add_hline(y=y_data[y].mean(), row=1, col=2, line_width=0.5, line_dash="dash", line_color="black")
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

    def scatter2x2(
            self,
            x1:str, y1:str, x1u:str, y1u:str,
            x2:str, y2:str, x2u:str, y2u:str,
            x3:str, y3:str, x3u:str, y3u:str,
            x4:str, y4:str, x4u:str, y4u:str,
    ) -> go.Figure:
        fig = make_subplots(
            rows=2, cols=2,
            row_width=[0.5, 0.5],
            column_width=[0.5, 0.5],
            vertical_spacing=0.1,
            horizontal_spacing=0.1
        )
        hov = '%{meta}(%{text})<br>업종: %{customdata}<br>'

        data = self.baseline.copy()
        trace_nw = go.Scatter(
            name='nw',
            x=data[x1], y=data[y1],
            mode='markers',
            marker=dict(
                color=data.섹터색상,
                size=data.시가총액 / 4,
                symbol='circle',
                line=dict(width=0)
            ),
            opacity=1.0,
            visible=True,
            showlegend=False,
            meta=data.종목명,
            customdata=data.섹터,
            text=data.index,
            hovertemplate=hov + x1 + ': %{x:.2f}' + x1u + '<br>' + y1 + ': %{y:.2f}' + y1u + '<extra></extra>'
        )

        trace_ne = go.Scatter(
            name='ne',
            x=data[x2], y=data[y2],
            mode='markers',
            marker=dict(
                color=data.섹터색상,
                size=data.시가총액 / 4,
                symbol='circle',
                line=dict(width=0)
            ),
            opacity=1.0,
            visible=True,
            showlegend=False,
            meta=data.종목명,
            customdata=data.섹터,
            text=data.index,
            hovertemplate=hov + x2 + ': %{x:.2f}' + x2u + '<br>' + y2 + ': %{y:.2f}' + y2u + '<extra></extra>'
        )

        fig.add_trace(trace=trace_nw, row=1, col=1)
        fig.add_trace(trace=trace_ne, row=1, col=2)
        return fig

if __name__ == "__main__":
    # '1028': '코스피200',
    # '1003': '코스피 중형주',
    # '1004': '코스피 소형주',
    # '2203': '코스닥150',
    # '2003': '코스닥 중형주'

    viewer = view_market()

    # save(
    #     fig=viewer.treemap(
    #         category='WICS',
    #         sub_category=str(),
    #         key='PER',
    #     ),
    #     filename=f'{viewer.td_date}_시장지도'
    # )

    # from tdatlib import normalize, fit_timeseries
    # from tqdm import tqdm
    # import pandas as pd
    #
    # def attr(obj: object, target: list):
    #     attribs = list()
    #     proc = tqdm(target)
    #     for ticker in proc:
    #         proc.set_description(desc=f'Set Attribute ... {ticker}')
    #         attr = getattr(obj, f'A{ticker}')
    #
    #         # This is where you put external attributs
    #         data = dict()
    #         for lb, n in (('S1W', 5), ('S2W', 10), ('S1M', 20), ('S2M', 40), ('S3M', 60), ('S6M', 80)):
    #             price = attr.ohlcv[-(n+1):]
    #             series = 0.25 * (price.시가 + price.종가 + price.고가 + price.저가)
    #             _, s = fit_timeseries(series=series, rel=True)
    #             data[lb] = s
    #         attribs.append(pd.DataFrame(data=data, index=[ticker]))
    #     # return pd.Series(data=attribs, index=target, name='pt_mfi')
    #     return pd.concat(objs=attribs, axis=0)
    # viewer.append(func=attr)
    #
    # save(fig=viewer.scatter(x='S2W', y='S1W'), filename=f'산포도_S2W_S1W')
    # save(fig=viewer.scatter(x='S1M', y='S1W'), filename=f'산포도_S1M_S1W')
    # save(fig=viewer.scatter(x='S2M', y='S1W'), filename=f'산포도_S2M_S1W')
    # save(fig=viewer.scatter(x='S3M', y='S2W'), filename=f'산포도_S3M_S2W')
    # save(fig=viewer.scatter(x='S6M', y='S2W'), filename=f'산포도_S6M_S2W')