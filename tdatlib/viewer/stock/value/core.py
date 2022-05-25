from tdatlib.dataset.stock import KR
from tdatlib.viewer.tools import CD_RANGER
import plotly.graph_objects as go


CD_COLORS = [
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf'   # blue-teal
]


class chart(object):

    def __init__(self, src:KR):
        self.src = src

    @property
    def pie(self) -> go.Pie:
        if not hasattr(self, f'__pie'):
            self.__setattr__(
                f'__pie',
                go.Pie(
                    name='Product',
                    labels=self.src.basis_products.index,
                    values=self.src.basis_products,
                    visible=True,
                    showlegend=False,
                    textfont=dict(color='white'),
                    textinfo='label+percent',
                    insidetextorientation='radial',
                    hoverinfo='label+percent'
                )
            )
        return self.__getattribute__('__pie')

    @property
    def multi_factor(self) -> dict:
        if not hasattr(self, f'__multifactor'):
            scatters = {
                col : go.Scatterpolar(
                    name=col,
                    r=self.src.basis_multifactor[col],
                    theta=self.src.basis_multifactor.index,
                    visible=True,
                    showlegend=True,
                    legendgrouptitle=dict(text='멀티팩터') if not n else None,
                    fill='toself',
                    hovertemplate=col + '<br>팩터: %{theta}<br>값: %{r}<extra></extra>'
                ) for n, col in enumerate(self.src.basis_multifactor.columns)
            }
            self.__setattr__(f'__multifactor', scatters)
        return self.__getattribute__('__multifactor')

    @property
    def asset(self) -> dict:
        if not hasattr(self, '__asset'):
            scatters = {
                '자산' : go.Bar(
                    name='자산',
                    x=self.src.basis_asset.index,
                    y=self.src.basis_asset.자산총계,
                    visible=True,
                    showlegend=False,
                    marker=dict(color='green'),
                    opacity=0.9,
                    text=self.src.basis_asset.자산총계LB,
                    meta=self.src.basis_asset.부채총계LB,
                    customdata=self.src.basis_asset.자본총계LB,
                    offsetgroup=0,
                    texttemplate='',
                    hovertemplate='자산: %{text}<br>부채: %{meta}<br>자본: %{customdata}<extra></extra>'
                ),
                '부채' : go.Bar(
                    name='부채',
                    x=self.src.basis_asset.index,
                    y=self.src.basis_asset.부채총계,
                    visible=True,
                    showlegend=False,
                    marker=dict(color='red'),
                    opacity=0.8,
                    offsetgroup=0,
                    hoverinfo='skip'
                )
            }
            self.__setattr__('__asset', scatters)
        return self.__getattribute__('__asset')

    @property
    def profit(self) -> dict:
        if not hasattr(self, '__profit'):
            scatters = {
                col : go.Bar(
                    name=f'연간{col}',
                    x=self.src.basis_profit.index,
                    y=self.src.basis_profit[col],
                    marker=dict(
                        color=CD_COLORS[n]
                    ),
                    opacity=0.9,
                    legendgroup=col,
                    legendgrouptitle=dict(
                        text='연간실적'
                    ) if not n else None,
                    showlegend=True,
                    meta=self.src.basis_profit[f'{col}LB'],
                    hovertemplate=col + ': %{meta}<extra></extra>',
                ) for n, col in enumerate(self.src.basis_profit.columns) if not col.endswith('LB')
            }
            self.__setattr__('__profit', scatters)
        return self.__getattribute__('__profit')




# class sketch(object):
#     def __init__(self):
#         self.__x_axis = dict(
#             showticklabels=False,
#             tickformat='%Y/%m/%d',
#             zeroline=False,
#             showgrid=True,
#             gridcolor='lightgrey',
#             autorange=True,
#             showline=True,
#             linewidth=1,
#             linecolor='grey',
#             mirror=False,
#         )
#         self.__y_axis = dict(
#             showticklabels=True,
#             zeroline=False,
#             showgrid=True,
#             gridcolor='lightgrey',
#             autorange=True,
#             showline=True,
#             linewidth=0.5,
#             linecolor='grey',
#             mirror=False
#         )
#
#     def x_axis(self, title:str=str(), showticklabels:bool=False, rangeselector:bool=False) -> dict:
#         _ = self.__x_axis.copy()
#         if title:
#             _['title'] = title
#         if showticklabels:
#             _['showticklabels'] = True
#         if rangeselector:
#             _['rangeselector'] = CD_RANGER
#         return _
#
#     def y_axis(self, title:str=str()) -> dict:
#         _ = self.__y_axis.copy()
#         if title:
#             _['title'] = title
#         return _

