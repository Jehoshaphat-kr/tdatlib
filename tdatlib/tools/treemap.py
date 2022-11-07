import pandas as pd


class _treemap(object):

    __n = str()

    def __init__(self, baseline:pd.DataFrame, name:str, tag:str=str()):
        self.__b = baseline.copy()
        self.__n, self.__tag = name, f'_{tag}' if tag else tag

    def align(self):
        _b = self.__b.reset_index(level=0).copy()
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
        aligned = pd.concat(objs=objs, axis=0, ignore_index=True)[
            ['종목코드', '종목명', '분류', '종가', '크기', 'PER', 'PBR', 'DIV']
        ]

        key = aligned[aligned['종목명'] == aligned['분류']].copy()
        if not key.empty:
            aligned = aligned.drop(index=key.index)
        return aligned


if __name__ == "__main__":
    from tdatlib.market.core import *

    base = krse.wics.join(krse.overview.drop(columns=['종목명']), how='left')
    base = base[base.시가총액 >= 300000000000]

    tmap = _treemap(baseline=base, name='WICS')
    df = tmap.align()
    print(df)
    df.to_csv(r'C:\Users\Administrator\Desktop\Temp\test.csv', index=False, encoding='euc-kr')

