from datetime import datetime
import plotly.graph_objects as go
import pandas as pd


class _settings(object):
    obj = None

    @property
    def legend(self) -> bool:
        return self.obj['showlegend']

    @legend.setter
    def legend(self, on_off:bool):
        self.obj['showlegend'] = on_off

    @property
    def visible(self) -> bool:
        return self.obj['visible']

    @visible.setter
    def visible(self, on_off_legendonly: bool or str):
        self.obj['visible'] = on_off_legendonly

    @property
    def width(self) -> float or int:
        return self.obj['line']['width']

    @width.setter
    def width(self, width:float or int):
        self.obj['line'].update(dict(width=width))

    @property
    def color(self) -> str:
        return self.obj['line']['color']

    @color.setter
    def color(self, color:str):
        self.obj['line'].update(dict(color=color))

    @property
    def dash(self) -> str:
        return self.obj['line']['dash']

    @dash.setter
    def dash(self, dash:str):
        self.obj['line'].update(dict(dash=dash))

    @property
    def hover(self) -> str:
        return self.obj['hovertemplate']

    @hover.setter
    def hover(self, hover:str):
        self.obj['hovertemplate'] = hover

    @property
    def yhoverformat(self) -> str:
        return self.obj['yhoverformat']

    @yhoverformat.setter
    def yhoverformat(self, yhoverformat:str):
        self.obj['yhoverformat'] = yhoverformat

    @property
    def xhoverformat(self) -> str:
        return self.obj['xhoverformat']

    @xhoverformat.setter
    def xhoverformat(self, xhoverformat: str):
        self.obj['xhoverformat'] = xhoverformat


class draw_line(_settings):
    def __init__(self, data:pd.Series, name:str=str()):
        self.obj = go.Scatter(
            name=name if name else data.name,
            x=data.index, y=data,
            visible=True, showlegend=True, line=dict(),
            yhoverformat='.2f', xhoverformat='%Y/%m/%d', hovertemplate='%{x}<br>%{y}'
        )

    def __call__(self):
        return self.obj


class draw_candle(_settings):
    def __init__(self, data:pd.DataFrame, name:str=str()):
        self.obj = go.Candlestick(
            name=name if name else data.name,
            x=data.index,
            open=data.시가,
            high=data.고가,
            low=data.저가,
            close=data.종가,
            visible=True,
            showlegend=True,
            increasing_line=dict(color='red'),
            decreasing_line=dict(color='royalblue'),
            xhoverformat='%Y/%m/%d',
            yhoverformat='.2f',
        )

    def __call__(self):
        return self.obj


def draw_recession(fig:go.Figure, market:str):
    recession = [
        {'label': 'blank#01', 'from': datetime(1994, 11, 8), 'to': datetime(1995, 5, 27)},
        {'label': 'blank#02', 'from': datetime(1996, 5, 7), 'to': datetime(1997, 1, 7)},
        {'label': 'blank#03', 'from': datetime(1997, 8, 11), 'to': datetime(1997, 12, 12)},
        {'label': 'blank#04', 'from': datetime(1998, 3, 2), 'to': datetime(1998, 6, 16)},
        {'label': 'blank#05', 'from': datetime(1999, 1, 11), 'to': datetime(1999, 2, 24)},
        {'label': 'blank#06', 'from': datetime(1999, 7, 19), 'to': datetime(1999, 10, 5)},
        {'label': 'blank#07', 'from': datetime(2000, 1, 4), 'to': datetime(2000, 12, 22)},
        {'label': 'blank#08', 'from': datetime(2002, 4, 17), 'to': datetime(2003, 3, 17)},
        {'label': 'blank#09', 'from': datetime(2004, 4, 23), 'to': datetime(2004, 8, 2)},
        {'label': 'blank#10', 'from': datetime(2007, 11, 1), 'to': datetime(2008, 10, 24)},
        {'label': 'blank#11', 'from': datetime(2011, 5, 2), 'to': datetime(2011, 9, 26)},
        {'label': 'blank#12', 'from': datetime(2018, 1, 29), 'to': datetime(2019, 1, 3)},
        {'label': 'blank#13', 'from': datetime(2020, 1, 22), 'to': datetime(2020, 3, 19)},
        {'label': 'blank#14', 'from': datetime(2021, 7, 6), 'to': datetime(2022, 10, 5)},
    ] if market.lower().startswith('k') else [
        {'label': 'The Own Goal Recession', 'from': datetime(1937, 5, 1), 'to': datetime(1938, 6, 1)},
        {'label': 'The V-Day Recession', 'from': datetime(1945, 2, 1), 'to': datetime(1945, 10, 1)},
        {'label': 'The Post-War Brakes Tap Recession', 'from': datetime(1948, 11, 1), 'to': datetime(1949, 10, 1)},
        {'label': 'Post-Korean War Recession', 'from': datetime(1953, 7, 1), 'to': datetime(1954, 5, 1)},
        {'label': 'The Investment Bust Recession', 'from': datetime(1957, 8, 1), 'to': datetime(1958, 4, 1)},
        {'label': 'The Rolling Adjustment Recession', 'from': datetime(1960, 4, 1), 'to': datetime(1961, 2, 1)},
        {'label': 'The Guns and Butter Recession', 'from': datetime(1969, 12, 1), 'to': datetime(1970, 11, 1)},
        {'label': 'The Oil Embargo Recession', 'from': datetime(1973, 11, 1), 'to': datetime(1975, 3, 1)},
        {'label': 'The Iran and Volcker Recession', 'from': datetime(1980, 1, 1), 'to': datetime(1980, 7, 1)},
        {'label': 'Double-Dip Recession', 'from': datetime(1981, 7, 1), 'to': datetime(1982, 11, 1)},
        {'label': 'The Gulf War Recession', 'from': datetime(1990, 7, 1), 'to': datetime(1991, 3, 1)},
        {'label': 'The Dot-Bomb Recession', 'from': datetime(2001, 3, 1), 'to': datetime(2001, 11, 1)},
        {'label': 'The Great Recession', 'from': datetime(2007, 12, 1), 'to': datetime(2009, 6, 1)},
        {'label': 'The COVID-19 Recession', 'from': datetime(2020, 2, 1), 'to': datetime(2020, 4, 1)},
    ]
    start = min([d['x'][0] for d in fig['data']])
    for d in recession:
        x0, x1 = d['from'], d['to']
        if x1 < start:
            continue
        if x0 < start:
            x0 = start
        fig.add_vrect(x0=x0, x1=x1, fillcolor='grey', opacity=0.2, line_width=0)
    return fig


if __name__ == "__main__":
    from tdatlib.macro.ecos import ecos

    raw = ecos()
    trace = draw_line(raw.CD금리91D)

    print(trace())
