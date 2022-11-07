import pandas as pd


class _treemap(object):

    __n = str()

    def __init__(self, baseline:pd.DataFrame, name:str):
        self.__b = baseline.copy()
        self.__n = name

    def align(self):
        _b = self.__b.reset_index(level=0).copy()
        _b['크기'] = _b['시가총액'] / 100000000

        lvl = [col for col in ['종목코드', '섹터', '산업'] if col in _b.columns]
        ftr = [col for col in _b.columns if any([col.startswith(key) for key in ['R', 'B', 'P', 'D']])]

        objs = list()
        for n, l in enumerate(lvl):
            if not n:
                child = _b.rename(columns={'섹터':'분류'})
                if '산업' in child.columns:
                    child = child.drop(columns=['산업'])
                objs.append(child)
                continue

            child = pd.DataFrame()
            layer = _b.groupby(by=lvl[n:]).sum().reset_index()