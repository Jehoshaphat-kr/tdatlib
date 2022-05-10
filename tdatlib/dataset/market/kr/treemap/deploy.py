from datetime import datetime
from pytz import timezone
import pandas as pd
import codecs, jsmin, os


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DIR_SUFFIX = f'{ROOT}/_archive/treemap/suffix.js'
DIR_DEPLOY = f'{ROOT}/_archive/treemap/deploy/js'
CD_DATE = datetime.now(timezone('Asia/Seoul')).strftime("%Y%m%d")
CD_CATEGORY = [
    ["WICS", '', "indful"],
    ["WICS", '1028', "indks2"],
    ["WICS", '1003', "indksm"],
    ["WICS", '1004', "indkss"],
    ["WICS", '2203', "indkq1"],
    ["WICS", '2003', "indkqm"],
    ["WI26", '', "secful"],
    ["WI26", '1028', "secks2"],
    ["WI26", '1003', "secksm"],
    ["WI26", '1004', "seckss"],
    ["WI26", '2203', "seckq1"],
    ["WI26", '2003', "seckqm"],
    ["ETF", '', "etfful"],
    ["THEME", '', "thmful"]
]
CD_LABEL = [
    '종목명', '종가', '시가총액', '크기',
    'R1D', 'R1W', 'R1M', 'R3M', 'R6M', 'R1Y',
    'PER', 'PBR', 'DIV',
    'CR1D', 'CR1W', 'CR1M', 'CR3M', 'CR6M', 'CR1Y',
    'CPER', 'CPBR', 'CDIV'
]

class treemap_deploy(object):
    __labels, __covers, __ids, __bars = dict(), dict(), dict(), dict()
    __cover, __datum = list(), pd.DataFrame(columns=['종목코드'])

    def __init__(self, market):
        self.market = market
        for n, (c, s, var) in enumerate(CD_CATEGORY):
            print(f'[{n + 1}/{len(CD_CATEGORY)}] {c} / {s}')
            mymap = self.market.treemap(category=c, sub_category=s)
            mybar = self.market.sectors(category=c, sub_category=s)['종목코드']

            self.__labels[var] = mymap['종목코드'].tolist()
            self.__covers[var] = mymap['분류'].tolist()
            self.__ids[var] = mymap['ID'].tolist()
            self.__bars[var] = mybar

            self.__datum = pd.concat(
                objs=[self.__datum, mymap[~mymap['종목코드'].isin(self.__datum['종목코드'])]],
                axis=0, ignore_index=True
            )
        self.__datum.set_index(keys=['종목코드'], inplace=True)
        self.__cover = self.__datum[
            self.__datum.index.isin([code for code in self.__datum.index if '_' in code])
        ]['종목명'].tolist()
        return

    def to_js(self):
        """
        javascript 파일 출력
        :return:
        """
        td = self.market.trading_date
        yy, mm, dd = td[:4], td[4:6], td[6:]
        suffix = codecs.open(filename=DIR_SUFFIX, mode='r', encoding='utf-8').read()
        syntax = f'document.getElementsByClassName("date")[0].innerHTML="{yy}년 {mm}월 {dd}일 종가 기준";'

        _cnt = 1
        _js = os.path.join(DIR_DEPLOY, f"{td[2:]}MM-r{_cnt}.js")
        while os.path.isfile(_js):
            _cnt += 1
            _js = os.path.join(DIR_DEPLOY, f"{td[2:]}MM-r{_cnt}.js")

        proc = [('labels', self.__labels), ('covers', self.__covers), ('ids', self.__ids), ('bar', self.__bars)]
        for name, data in proc:
            syntax += 'const %s = {\n' % name
            for var, val in data.items():
                syntax += f'\t{var}: {str(val)},\n'
            syntax += '}\n'

        _frm = self.__datum[CD_LABEL].copy()
        _frm.fillna('-', inplace=True)
        js = _frm.to_json(orient='index', force_ascii=False)

        syntax += f"const frm = {js}\n"
        syntax += f"const group_data = {str(self.__cover)}\n"
        with codecs.open(filename=_js, mode='w', encoding='utf-8') as file:
            file.write(jsmin.jsmin(syntax + suffix))
        return
