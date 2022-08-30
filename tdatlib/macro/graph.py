import plotly.graph_objects as go
import pandas as pd


class trace(object):

    def __init__(self, src):
        self.__ = src
        for _ in self.__.properties:
            self.__setattr__(_, None)
        return

    def __call__(self, prop:str, **kwargs):
        if not hasattr(self, prop):
            raise AttributeError

        if not getattr(self, prop):
            src = getattr(self.__, prop).copy()
            key = kwargs.keys()
            setattr(
                self,
                prop,
                go.Scatter(
                    name=kwargs['name'] if 'name' in key else prop,
                    x=src.index,
                    y=src[kwargs['key']] if 'key' in key else src,
                    mode='lines',
                    line=dict(
                        dash=kwargs['dash'] if 'dash' in key else 'solid',
                        width=kwargs['width'] if 'width' in key else 1
                    ),
                    visible=kwargs['visible'] if 'visible' in key else True,
                    showlegend=kwargs['showlegend'] if 'showlegend' in key else True,
                    xhoverformat='%Y/%m/%d',
                    yhoverformat=kwargs['yhovertemplate'] if 'yhovertemplate' in key else '%{.2f}',
                    hovertemplate=f"{kwargs['name'] if 'name' in key else prop}<br>" + \
                                  '%{y}' + (kwargs['unit'] if 'unit' in key else '') + ' @%{x}<extra></extra>'
                )
            )
        return self.__getattribute__(prop)

    # def add_recession(self, fig:go.Figure, market:str='kr') -> go.Figure:
    #     xs = [f['x'][0] for f in fig['data']]
    #     for elem in self._src.recession_kr if market.lower() == 'kr' else self._src.recession_us:
    #         if elem['to'] < min(xs):
    #             continue
    #         fig.add_vrect(
    #             x0=elem['from'].strftime('%Y-%m-%d'), x1=elem['to'].strftime('%Y-%m-%d'), row='all', col='all',
    #             fillcolor="grey", opacity=0.25, line_width=0)
    #     return fig

    # def add_us_recession(self, fig:go.Figure):
    #     xs = [f['x'][0] for f in fig['data']]
    #     for elem in self._src.US_recession:
    #         if elem['to'] < min(xs):
    #             continue
    #         fig.add_vrect(
    #             x0=elem['from'],
    #             x1=elem['to'],
    #             row='all',
    #             col='all',
    #             fillcolor='grey',
    #             opacity=0.2,
    #             line_width=0
    #         )
    #     return