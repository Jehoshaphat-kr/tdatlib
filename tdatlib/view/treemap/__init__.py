from tdatlib.view.treemap.toolbox import market, toolbox
from tdatlib import archive
from datetime import datetime
from pytz import timezone
from inspect import currentframe as inner
from pykrx import stock
import pandas as pd
import plotly.graph_objects as go
import plotly.offline as of
import codecs, jsmin, os


class treemap(toolbox):
    def __init__(self, category:str, sub_category:str=str(), kq:list=None):
        super().__init__(category=category, sub_category=sub_category, kq=kq)
        return

    def __checkattr__(self, name:str) -> str:
        if not hasattr(self, f'__{name}'):
            _func = self.__getattribute__(f'_get_{name}')
            self.__setattr__(f'__{name}', _func())
        return f'__{name}'

    @property
    def mapname(self) -> str:
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def baseline(self) -> pd.DataFrame:
        """
        :return:
                         종목명      섹터        IPO    종가  ...    R1M    R3M    R6M     R1Y
        종목코드                                              ...
        096770     SK이노베이션    에너지 2007-07-25  209000  ...   0.96  -0.94 -12.29    4.21
        010950            S-Oil    에너지 1987-05-27   87800  ...   6.81   0.57 -13.50    9.48
        267250   현대중공업지주    에너지 2017-05-10   52700  ...   6.45  -8.65 -20.00   -6.38
        ...                 ...       ...        ...     ...  ...    ...    ...    ...     ...
        017390         서울가스  유틸리티 1995-08-18  186000  ...  -3.13  14.15   9.12  108.90
        117580       대성에너지  유틸리티 2010-12-24   12100  ...  23.08  17.65  31.29  124.30
        071320     지역난방공사  유틸리티 2010-01-29   36300  ...   4.46  -5.84 -13.78   -4.10
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def mapframe(self) -> pd.DataFrame:
        """
        :return:
                          종목코드          종목명    분류  ...     CPER     CDIV              ID
        0                   096770    SK이노베이션  에너지  ...      NaN      NaN    SK이노베이션
        1                   010950          S-Oil   에너지  ...      NaN      NaN           S-Oil
        2                   267250  현대중공업지주  에너지  ...      NaN  #30CC5A  현대중공업지주
        ..                     ...            ...      ...  ...      ...      ...             ...
        748  화장품,의류_WI26_전체     화장품,의류    전체  ...  #F63538  #414554     화장품,의류
        749         화학_WI26_전체            화학    전체  ...  #F63538  #8B444E            화학
        750              WI26_전체            전체          ...  #C8C8C8  #C8C8C8            전체
        """
        return self.__getattribute__(self.__checkattr__(inner().f_code.co_name))

    @property
    def bar(self) -> pd.DataFrame:
        """
        :return:
        ['IT가전_WI26_전체', 'IT하드웨어_WI26_전체', ... , '화장품,의류_WI26_전체', '화학_WI26_전체']
        """
        if not hasattr(self, '_bar'):
            _ = self.mapframe
        return self.__getattribute__('_bar')

    def show(self, key:str='R1D', save:bool=False):
        """
        :param key: 지도 표시 펙터
        :param save: 저장 여부
        :return:
        """
        frame = self.mapframe.copy()
        fig = go.Figure()
        unit = '%' if not key in ['PER', 'PBR'] else ''
        fig.add_trace(go.Treemap(
            ids=frame['ID'], labels=frame['종목명'], parents=frame['분류'], values=frame['크기'],
            marker=dict(colors=frame[f'C{key}']),
            textfont=dict(color='#ffffff'), textposition='middle center', texttemplate='%{label}<br>%{text}%<br>',
            meta=frame['시가총액'], customdata=frame['종가'], text=frame[key],
            branchvalues='total', opacity=0.9,
            hovertemplate='%{label}<br>시총: %{meta}<br>종가: %{customdata}<br>' + key + ': %{text}' + unit + '<extra></extra>'
        ))
        title = f'[{self.cat} / {self.mapname}]: {market.tddate} 종가 기준 {key}'
        fig.update_layout(title=title)
        if save:
            of.plot(fig, filename=rf'./{self.cat}_{self.mapname}.html', auto_open=False)
        fig.show()
        return

class treemap_deploy:
    __labels, __covers, __ids, __bars = dict(), dict(), dict(), dict()
    __cover, __datum = list(), pd.DataFrame(columns=['종목코드'])

    def __init__(self):
        categories = [
            ["WICS", '', "indful"],
            ["WICS", '1028', "indks2"], ["WICS", '1003', "indksm"], ["WICS", '1004', "indkss"],
            ["WICS", '2203', "indkq1"], ["WICS", '2003', "indkqm"],
            ["WI26", '', "secful"],
            ["WI26", '1028', "secks2"], ["WI26", '1003', "secksm"], ["WI26", '1004', "seckss"],
            ["WI26", '2203', "seckq1"], ["WI26", '2003', "seckqm"],
            ["ETF", '', "etfful"],
            ["THEME", '', "thmful"]
        ]
        kq = stock.get_index_portfolio_deposit_file(ticker='2001')
        for n, (c, s, var) in enumerate(categories):
            tmap = treemap(category=c, sub_category=s, kq=kq)
            print(f'[{n + 1}/{len(categories)}] {c} / {tmap.mapname}')

            frame = tmap.mapframe.copy()
            self.__labels[var] = frame['종목코드'].tolist()
            self.__covers[var] = frame['분류'].tolist()
            self.__ids[var] = frame['ID'].tolist()
            self.__bars[var] = tmap.bar

            self.__datum = pd.concat(
                objs=[self.__datum, frame[~frame['종목코드'].isin(self.__datum['종목코드'])]],
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
        t = datetime.now(timezone('Asia/Seoul')).strftime("%Y%m%d")
        yy, mm, dd = t[:4], t[4:6], t[6:]
        suffix = codecs.open(filename=os.path.join(archive.map_js), mode='r', encoding='utf-8').read()
        syntax = f'document.getElementsByClassName("date")[0].innerHTML="{yy}년 {mm}월 {dd}일 종가 기준";'
        _dir = os.path.join(archive.root, 'deploy/js')
        _cnt = 1
        _js = os.path.join(_dir, f"{t[2:]}MM-r{_cnt}.js")
        while os.path.isfile(_js):
            _cnt += 1
            _js = os.path.join(_dir, f"{t[2:]}MM-r{_cnt}.js")

        proc = [('labels', self.__labels), ('covers', self.__covers), ('ids', self.__ids), ('bar', self.__bars)]
        for name, data in proc:
            syntax += 'const %s = {\n' % name
            for var, val in data.items():
                syntax += f'\t{var}: {str(val)},\n'
            syntax += '}\n'

        _frm = self.__datum[archive.map_label].copy()
        _frm.fillna('-', inplace=True)
        js = _frm.to_json(orient='index', force_ascii=False)

        syntax += f"const frm = {js}\n"
        syntax += f"const group_data = {str(self.__cover)}\n"
        with codecs.open(filename=_js, mode='w', encoding='utf-8') as file:
            file.write(jsmin.jsmin(syntax + suffix))
        return


if __name__ == "__main__":
    # 코스피200(1028), 코스피 중형주(1003), 코스피 소형주(1004), 코스닥150(2203), 코스닥 중형주(2003)

    # t_treemap = treemap(category='WICS')
    # t_treemap = treemap(category='WICS', sub_category='1028')
    # t_treemap = treemap(category='WICS', sub_category='1003')
    # t_treemap = treemap(category='WICS', sub_category='1004')
    # t_treemap = treemap(category='WICS', sub_category='2203')
    # t_treemap = treemap(category='WICS', sub_category='2003')

    t_treemap = treemap(category='WI26')
    # t_treemap = treemap(category='WI26', sub_category='1028')
    # t_treemap = treemap(category='WI26', sub_category='1003')
    # t_treemap = treemap(category='WI26', sub_category='1004')
    # t_treemap = treemap(category='WI26', sub_category='2203')
    # t_treemap = treemap(category='WI26', sub_category='2003')

    # t_treemap = treemap(category='THEME')
    # t_treemap = treemap(category='ETF')

    print(t_treemap.baseline)
    print(t_treemap.mapframe)
    print(t_treemap.bar)

    t_treemap.show(save=True)
    # t_treemap.show(key='PER')
    # t_treemap.show(key='PBR')
    # t_treemap.show(key='DIV')



