from pykrx.stock import get_index_portfolio_deposit_file
import plotly.graph_objects as go
import pandas as pd
import numpy as np


class treemap(object):
    scale = ['#F63538', '#BF4045', '#8B444E', '#414554', '#35764E', '#2F9E4F', '#30CC5A']  # Low <---> High
    bound = {
        'R1Y': ([-30, -20, -10, 0, 10, 20, 30], [-25, -15, -5, 5, 15, 25]),
        'R6M': ([-24, -16, -8, 0, 8, 16, 24], [-20, -12, -4, 4, 12, 20]),
        'R3M': ([-18, -12, -6, 0, 6, 12, 18], [-15, -9, 3, 3, 9, 15]),
        'R1M': ([-10, -6.7, -3.3, 0, 3.3, 6.7, 10], [-8.35, -5, -1.65, 1.65, 5, 8.35]),
        'R1W': ([-6, -4, -2, 0, 2, 4, 6], [-5, -3, -1, 1, 3, 5]),
        'R1D': ([-3, -2, -1, 0, 1, 2, 3], [-2.5, -1.5, -0.5, 0.5, 1.5, 2.5])
    }

    def __init__(
        self,
        baseline:pd.DataFrame,
        name:str,
        tag:str=str(),
        kosdaq:list or pd.Series or np.array=None,
    ):
        self.__b = baseline.copy()
        self.name, self.tag = name, f'_{tag}' if tag else tag
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
                obj['종목코드'] = layer[l] + f'_{self.name}{self.tag}'
                obj['종목명'] = layer[l]
                obj['분류'] = layer[lvl[n + 1]] if n < len(lvl) - 1 else self.name
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
            data=[[f'{self.name}{self.tag}', self.name, '', _b['크기'].sum()]],
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
        colored = pd.DataFrame(index=aligned.index)
        for c, (na, bins) in self.bound.items():
            color = aligned[c].apply(
                lambda n:
                self.scale[3] if str(n) == 'nan' else \
                self.scale[0] if n <= bins[0] else \
                self.scale[1] if bins[0] < n <= bins[1] else \
                self.scale[2] if bins[1] < n <= bins[2] else \
                self.scale[3] if bins[2] < n <= bins[3] else \
                self.scale[4] if bins[3] < n <= bins[4] else \
                self.scale[5] if bins[4] < n <= bins[5] else \
                self.scale[6]
            )
            color.name = f'C{c}'
            colored = colored.join(color.astype(str), how='left')

        if not self.name == 'ETF':
            for f in ['PBR', 'PER', 'DIV']:
                re_scale = self.scale if f == 'DIV' else self.scale[::-1].copy()
                value = aligned[aligned[f] != 0][f].dropna().sort_values(ascending=False)

                v = value.tolist()
                limit = [v[int(len(value) / 7) * i] for i in range(len(re_scale))] + [v[-1]]
                _color = pd.cut(value, bins=limit[::-1], labels=re_scale, right=True)
                _color.name = f"C{f}"
                colored = colored.join(_color.astype(str), how='left').fillna(re_scale[0 if f == 'DIV' else -1])
                colored = colored.replace('nan', re_scale[0 if f == 'DIV' else -1])

        colored = colored.fillna(self.scale[3])
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
    def mapdata(self) -> pd.DataFrame:
        aligned = self._align(baseline=self.__b)
        colored = self._coloring(aligned=aligned)
        mapdata = self._post(colored=colored)
        return mapdata

    @property
    def bardata(self) -> pd.DataFrame:
        columns = [
            '종목코드', '종목명', '분류',
            'PER', 'PBR', 'DIV', 'R1D', 'R1W', 'R1M', 'R3M', 'R6M', 'R1Y', 'R2Y',
            'CPBR', 'CPER', 'CDIV', 'CR1Y', 'CR6M', 'CR3M', 'CR1M', 'CR1W', 'CR1D'
        ] if not self.name == 'ETF' else [
            '종목코드', '종목명', '분류',
            'R1D', 'R1W', 'R1M', 'R3M', 'R6M', 'R1Y', 'R2Y',
            'CR1Y', 'CR6M', 'CR3M', 'CR1M', 'CR1W', 'CR1D'
        ]

        data = self.mapdata.copy()
        data = data[data['종목코드'].str.contains('_')]
        data = data[columns]
        if self.name == 'WICS':
            data = data[data['종목명'].isin([
                'IT', '건강관리', '경기관련소비재', '금융', '산업재', '소재', '에너지', '유틸리티',
                '커뮤니케이션서비스', '필수소비재'
            ])]
        elif self.name == 'ETF':
            data = data[data['종목명'].isin([
                '국고채', '회사채', '귀금속', '원자재',
                '독일', '미국', '선진국', '신흥국', '원유', '일본', '중국'
            ])]
        else: pass
        return data

    def maptrace(self, key:str='R1D') -> go.Treemap:
        data = self.mapdata
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
    # krse.insist = True

    # base = krse.wi26.join(krse.overview.drop(columns=['종목명']), how='left')
    # base = base.sort_values(by='시가총액', ascending=False).head(500)
    # base = pd.concat(objs=[base, krse.performance(base.index)], axis=1)
    # tmap = treemap(baseline=base, name='WI26')

    # etf.islatest()
    base = etf.group.join(etf.overview.drop(columns=['종목명']), how='left')
    base = base.join(etf.returns, how='left')
    tmap = treemap(baseline=base, name='ETF')

    print(tmap.bardata)
    # fig = go.Figure()
    # fig.add_trace(tmap.maptrace(key='PER'))
    # fig.show()

