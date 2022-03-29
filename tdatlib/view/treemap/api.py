from tdatlib.view.treemap.tools import *
from datetime import datetime
from pytz import timezone
import plotly.graph_objects as go
import plotly.offline as of
import codecs, jsmin


class mapping:
    __baseline, __reduced, __colored = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    __frame, __bar = pd.DataFrame(), list()
    def __init__(self, category:str, sub_category:str=str(), kq:list=None):
        self.cat, self.sub = category, sub_category
        self.kq = kq if not kq else krx.get_index_portfolio_deposit_file(ticker='2001')
        return

    @property
    def baseline(self) -> pd.DataFrame:
        if self.__baseline.empty:
            self.__baseline = getBaseline(category=self.cat, sub_category=self.sub)
        return self.__baseline

    @property
    def reduced(self) -> pd.DataFrame:
        if self.__reduced.empty:
            self.__reduced, self.__bar = calcReduction(baseline=self.baseline, category=self.cat, sub_category=self.sub)
        return self.__reduced

    @property
    def colored(self) -> pd.DataFrame:
        if self.__colored.empty:
            self.__colored = calcColors(frame=self.reduced, category=self.cat)
        return self.__colored

    @property
    def frame(self) -> pd.DataFrame:
        if self.__frame.empty:
            self.__frame = calcPost(frame=self.colored, category=self.cat)
        return self.__frame

    @property
    def bar(self) -> pd.DataFrame:
        if not self.__bar:
            self.__reduced, self.__bar = calcReduction(baseline=self.baseline, category=self.cat, sub_category=self.sub)
        return self.__bar

    def show(self, key:str='R1D', save:bool=False):
        """
        :param key: 지도 표시 펙터
        :param save: 저장 여부
        :return:
        """
        frame = self.frame.copy()
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
        tdt = krx.get_nearest_business_day_in_a_week(date=datetime.today().strftime("%Y%m%d"))
        title = f'[{self.cat} / {getMapName(category=self.cat, sub_category=self.sub)}]: {tdt} 종가 기준 {key}'
        fig.update_layout(title=title)
        if save:
            of.plot(fig, filename=rf'./{self.cat}_{self.sub}.html', auto_open=False)
        fig.show()
        return

class concat:
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
        kq = krx.get_index_portfolio_deposit_file(ticker='2001')
        for n, (c, s, var) in enumerate(categories):
            print(f'[{n + 1}/{len(categories)}] {c} / {getMapName(category=c, sub_category=s)}')
            treemap = mapping(category=c, sub_category=s, kq=kq)
            frame = treemap.frame.copy()
            self.__labels[var] = frame['종목코드'].tolist()
            self.__covers[var] = frame['분류'].tolist()
            self.__ids[var] = frame['ID'].tolist()
            self.__bars[var] = treemap.bar

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

    # t_treemap = mapping(category='WICS')
    # t_treemap = mapping(category='WICS', sub_category='1028')
    # t_treemap = mapping(category='WICS', sub_category='1003')
    # t_treemap = mapping(category='WICS', sub_category='1004')
    # t_treemap = mapping(category='WICS', sub_category='2203')
    # t_treemap = mapping(category='WICS', sub_category='2003')

    t_treemap = mapping(category='WI26')
    # t_treemap = mapping(category='WI26', sub_category='1028')
    # t_treemap = mapping(category='WI26', sub_category='1003')
    # t_treemap = mapping(category='WI26', sub_category='1004')
    # t_treemap = mapping(category='WI26', sub_category='2203')
    # t_treemap = mapping(category='WI26', sub_category='2003')

    # t_treemap = mapping(category='THEME')
    # t_treemap = mapping(category='ETF')

    print(t_treemap.baseline)
    print(t_treemap.reduced)

    t_treemap.show()
    # t_treemap.show(key='PER')
    # t_treemap.show(key='PBR')
    # t_treemap.show(key='DIV')

    # from tdatlib import archive
    # from os import path
    # t_treemap.frame.to_csv(path.join(archive.desktop, f'test.csv'), encoding='euc-kr', index=False)

