from tdatlib.market.core import krse, etf
from tdatlib.market.index import index
from tdatlib.tools.treemap import treemap
from tqdm import tqdm
import pandas as pd
import codecs, os, jsmin


class market(object):
    _dir = os.path.join(os.path.dirname(__file__), f'archive/common/suffix.js')
    _tag = [
        '종목명', '종가', '시가총액', '크기',
        'R1D', 'R1W', 'R1M', 'R3M', 'R6M', 'R1Y',
        'PER', 'PBR', 'DIV',
        'CR1D', 'CR1W', 'CR1M', 'CR3M', 'CR6M', 'CR1Y',
        'CPER', 'CPBR', 'CDIV'
    ]
    def __init__(self):
        kq = index.deposit('2001')

        wics = krse.wics.join(krse.overview.drop(columns=['종목명']), how='left').sort_values(by='시가총액', ascending=False)
        wi26 = krse.wi26.join(krse.overview.drop(columns=['종목명']), how='left').sort_values(by='시가총액', ascending=False)
        etfs = etf.group.join(etf.overview.drop(columns=['종목명']), how='left').join(etf.returns, how='left')

        wics_largecap = wics.head(500).copy()
        wics_largecap = wics_largecap.join(krse.performance(wics_largecap.index), how='left')
        wics_midcap = wics[~wics.index.isin(wics_largecap.index)].head(300)
        wics_midcap = wics_midcap.join(krse.performance(wics_midcap.index), how='left')

        wi26_largecap = wi26.head(500).copy()
        wi26_largecap = wi26_largecap.join(krse.performance(wi26_largecap.index), how='left')
        wi26_midcap = wi26[~wi26.index.isin(wi26_largecap.index)].head(300)
        wi26_midcap = wi26_midcap.join(krse.performance(wi26_midcap.index), how='left')

        self._kwargs = [
            (dict(baseline=wics_largecap, name='WICS', tag='LCap', kosdaq=kq), 'indful'),
            (dict(baseline=wics_midcap, name='WICS', tag='MCap', kosdaq=kq), 'indksm'),
            (dict(baseline=wi26_largecap, name='WI26', tag='LCap', kosdaq=kq), 'secful'),
            (dict(baseline=wi26_midcap, name='WI26', tag='MCap', kosdaq=kq), 'secksm'),
            (dict(baseline=etfs, name='ETF', tag='', kosdaq=kq), 'etfful'),
        ]

        self._datum = pd.DataFrame(columns=['종목코드'])
        self._labels, self._covers, self._ids, self._bars = dict(), dict(), dict(), dict()
        return

    def collect(self):
        proc = tqdm(self._kwargs)
        for kwarg, var in proc:
            mm = treemap(**kwarg)
            proc.set_description(desc=f'{mm.name}{mm.tag}')

            mdata = mm.data.copy()
            self._labels[var] = mdata['종목코드'].tolist()
            self._covers[var] = mdata['분류'].tolist()
            self._ids[var] = mdata['ID'].tolist()
            # self._bars[var] = mdata
            self._datum = pd.concat(
                objs=[self._datum, mdata[~mdata['종목코드'].isin(self._datum['종목코드'])]],
                axis=0, ignore_index=True
            )
        self._datum = self._datum.set_index(keys=['종목코드'])
        return

    def pd2js(self):
        td = krse.rdate
        suffix = codecs.open(self._dir, mode='r', encoding='utf-8').read()
        syntax = str()

        _ct = 1
        _js = os.path.join(os.path.dirname(__file__), f'archive/deploy/{td[2:]}MAP-r{_ct}.js')
        while os.path.isfile(_js):
            _ct += 1
            _js = os.path.join(os.path.dirname(__file__), f'archive/deploy/{td[2:]}MAP-r{_ct}.js')

        # proc = [('labels', self._labels), ('covers', self._covers), ('ids', self._ids), ('bar', self._bars)]
        proc = [('labels', self._labels), ('covers', self._covers), ('ids', self._ids)]
        for name, data in proc:
            syntax += 'const %s = {\n' % name
            for var, val in data.items():
                syntax += f'\t{var}: {str(val)},\n'
            syntax += '}\n'

        _frm = self._datum[self._tag].copy()
        _frm.fillna('-', inplace=True)
        js = _frm.to_json(orient='index', force_ascii=False)

        group = self._datum[self._datum.index.isin([c for c in self._datum.index if '_' in c])]['종목명'].tolist()
        syntax += f"const frm = {js}\n"
        syntax += f"const group_data = {str(group)}\n"
        with codecs.open(filename=_js, mode='w', encoding='utf-8') as file:
            file.write(jsmin.jsmin(syntax + suffix))
            # file.write(syntax + suffix)

        log = os.path.join(os.path.dirname(__file__), f'archive/deploy/log.csv')
        with codecs.open(filename=log, mode='w', encoding='utf-8') as file:
            file.write(
                f'https://cdn.jsdelivr.net/gh/Jehoshaphat-kr/tdatlib/tdatlib/market/archive/deploy/map-{td[2:]}r{_ct}.js'
            )
        return


if __name__ == "__main__":
    m = market()
    m.collect()
    m.pd2js()
