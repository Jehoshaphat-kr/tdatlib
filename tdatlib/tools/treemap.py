from pykrx.stock import get_index_portfolio_deposit_file
import plotly.graph_objects as go
import pandas as pd
import numpy as np


class treemap(object):

    __n = str()
    scale = ['#F63538', '#BF4045', '#8B444E', '#414554', '#35764E', '#2F9E4F', '#30CC5A']  # Low <---> High
    bound = {
        'R1Y': [-30, -20, -10, 0, 10, 20, 30],
        'R6M': [-24, -16, -8, 0, 8, 16, 24],
        'R3M': [-18, -12, -6, 0, 6, 12, 18],
        'R1M': [-10, -6.7, -3.3, 0, 3.3, 6.7, 10],
        'R1W': [-6, -4, -2, 0, 2, 4, 6],
        'R1D': [-3, -2, -1, 0, 1, 2, 3]
    }

    def __init__(
        self,
        baseline:pd.DataFrame,
        name:str,
        tag:str=str(),
        kosdaq:list or pd.Series or np.array=None,
    ):
        self.__b = baseline.copy()
        self.__n, self.__tag = name, f'_{tag}' if tag else tag
        self.__kq = kosdaq if kosdaq else get_index_portfolio_deposit_file('2001')
        return

    def _align(self, baseline:pd.DataFrame) -> pd.DataFrame:
        _b = baseline.reset_index(level=0).copy()
        _b['크기'] = _b['시가총액'] / 100000000

        lvl = [col for col in ['종목코드', '섹터', '산업'] if col in _b.columns]
        ftr = [col for col in _b.columns if any([col.startswith(key) for key in ['R', 'B', 'P', 'D']])]

        objs = list()
        for n, l in enumerate(lvl):
            obj = pd.DataFrame() if n else _b.rename(columns={'섹터': '분류'})
            if not n and '산업' in obj.columns:
                obj = obj.drop(columns=['산업'])
            if n:
                layer = _b.groupby(by=lvl[n:]).sum().reset_index()
                obj['종목코드'] = layer[l] + f'_{self.__n}{self.__tag}'
                obj['종목명'] = layer[l]
                obj['분류'] = layer[lvl[n + 1]] if n < len(lvl) - 1 else self.__n
                obj['크기'] = layer['크기']
                for name in obj['종목명']:
                    df = _b[_b[l] == name]
                    for f in ftr:
                        if f == 'DIV':
                            obj.loc[obj['종목명'] == name, f] = 0 if df.empty else df[f].mean()
                        else:
                            num = df[df['PER'] != 0].copy() if f == 'PER' else df
                            obj.loc[obj['종목명'] == name, f] = (num[f] * num['크기'] / num['크기'].sum()).sum()
            objs.append(obj)
        objs.append(pd.DataFrame(
            data=[[f'{self.__n}{self.__tag}', self.__n, '', _b['크기'].sum()]],
            columns=['종목코드', '종목명', '분류', '크기'], index=['Cover']
        ))
        aligned = pd.concat(objs=objs, axis=0, ignore_index=True)
        dropper = [c for c in ['IPO', '거래량', '시가총액', '상장주식수', 'BPS', 'DPS', 'EPS'] if c in aligned.columns]
        aligned = aligned.drop(columns=dropper)

        key = aligned[aligned['종목명'] == aligned['분류']].copy()
        if not key.empty:
            aligned = aligned.drop(index=key.index)
        return aligned

    def _coloring(self, aligned:pd.DataFrame) -> pd.DataFrame:
        middle, colored = self.scale.pop(3), pd.DataFrame(index=aligned.index)
        for c, bins in self.bound.items():
            mid = aligned[aligned[c] == 0]
            if mid.empty:
                color = pd.cut(x=aligned[c], bins=bins, labels=self.scale, right=True)
            else:
                x = aligned[~aligned.index.isin(mid.index)][c]
                m = pd.Series(data=[middle] * len(mid), index=mid.index)
                o = pd.Series(pd.cut(x=x, bins=bins, labels=self.scale, right=True))
                color = pd.concat(objs=[m, o], axis=0)
            color.name = f'C{c}'
            colored = colored.join(color.astype(str), how='left')
        colored.fillna(middle, inplace=True)
        for col in colored.columns:
            colored.at[colored.index[-1], col] = '#C8C8C8'
        return aligned.join(colored, how='left')

    def _post(self, colored:pd.DataFrame) -> pd.DataFrame:
        kq = self.__kq
        def rename(x):
            return x['종목명'] + "*" if x['종목코드'] in kq else x['종목명']

        def reform_price(x):
            return '-' if x['종가'] == '-' else '{:,}원'.format(int(x['종가']))

        def reform_cap(x):
            return f"{x['크기']}억원" if len(x['크기']) < 5 else f"{x['크기'][:-4]}조 {x['크기'][-4:]}억원"

        tree = colored.copy()
        tree['종가'].fillna('-', inplace=True)
        tree['크기'] = tree['크기'].astype(int).astype(str)
        tree['종목명'] = tree.apply(rename, axis=1)
        tree['종가'] = tree.apply(reform_price, axis=1)
        tree['시가총액'] = tree.apply(reform_cap, axis=1)

        ns, cs = tree['종목명'].values, tree['분류'].values
        tree['ID'] = [f'{name}[{cs[n]}]' if name in ns[n + 1:] or name in ns[:n] else name for n, name in enumerate(ns)]

        for col in tree.columns:
            if col.startswith('P') or col.startswith('D') or col.startswith('R'):
                tree[col] = tree[col].apply(lambda v: round(v, 2))
                if col == 'PER':
                    tree['PER'] = tree['PER'].apply(lambda val: val if not val == 0 else 'N/A')
        return tree

    @property
    def data(self) -> pd.DataFrame:
        aligned = self._align(baseline=self.__b)
        colored = self._coloring(aligned=aligned)
        mapdata = self._post(colored=colored)
        return mapdata

    def trace(self, key:str='R1D') -> go.Treemap:
        data = self.data
        unit = '' if key.startswith('P') else '%'
        return go.Treemap(
            ids=data.ID,
            labels=data.종목명,
            parents=data.분류,
            values=data.크기,
            marker=dict(
                colors=data[f'C{key}']
            ),
            textfont=dict(
                color='#ffffff'
            ),
            text=data[key],
            textposition='middle center',
            texttemplate='%{label}<br>%{text}' + unit,
            meta=data.시가총액,
            customdata=data.종가,
            hovertemplate='%{label}<br>시총: %{meta}<br>종가: %{customdata}<br>' + key + ': %{text}' + unit + '<extra></extra>',
            branchvalues='total',
            opacity=0.9,
        )


if __name__ == "__main__":
    from tdatlib.market.core import *


    # base = krse.wics.join(krse.overview.drop(columns=['종목명']), how='left')
    # base = base[base.시가총액 >= 300000000000]
    # base = pd.concat(objs=[base, krse.performance(base.index)], axis=1)
    # tmap = treemap(baseline=base, name='WICS')

    # etf.islatest()
    base = etf.group.join(etf.overview.drop(columns=['종목명']), how='left')
    base = base.join(etf.returns, how='left')
    tmap = treemap(baseline=base, name='ETF')

    fig = go.Figure()
    fig.add_trace(tmap.trace())
    fig.show()

