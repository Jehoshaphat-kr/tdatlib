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