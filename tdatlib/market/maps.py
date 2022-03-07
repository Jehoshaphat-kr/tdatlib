import os, time, codecs, jsmin, tdatlib
import pandas as pd
import plotly.graph_objects as go
import plotly.offline as of
from tdatlib.market import market
from pykrx import stock as krx


class treemap(market):
    __tickers, __category, __kq, __name = list(), pd.DataFrame(), list(), str()
    __cat, __idx, __bar = str(), str(), list()
    __labels, __covers, __ids, __bars = dict(), dict(), dict(), dict()
    __cover, __datum = list(), pd.DataFrame(columns=['종목코드'])
    def __init__(self, progress:str=str()):
        super().__init__(progress=progress)
        return

    def set_option(self, category:str, index:str=str()):
        self.__cat, self.__idx = category, index
        if not index in [str(), '1028', '1003', '1004', '2203', '2003']:
            raise KeyError(f'지수(Index):{index} 입력 오류: 코스피[200/중형주/소형주] 및 코스닥[150/중형주]만 가능!')
        if category == 'WICS':
            self.__category, self.__name = self.wics.copy(), '전체'
        elif category == 'WI26':
            self.__category, self.__name = self.wi26.copy(), '전체'
        elif category == 'THEME':
            self.__category, self.__name = self.theme.copy(), '테마'
        elif category == 'ETF':
            self.__category, self.__name = self.etf.copy(), 'ETF'

        self.__name = krx.get_index_ticker_name(index) if index else self.__name
        return

    def show(self, key:str='R1D', save:bool=False):
        """
        지도 Treemap
        """
        frame = self.map_frame.copy()
        fig = go.Figure()
        fig.add_trace(go.Treemap(
            ids=frame['ID'], labels=frame['종목명'], parents=frame['분류'], values=frame['크기'],
            marker=dict(colors=frame[f'C{key}']),
            textfont=dict(color='#ffffff'), textposition='middle center', texttemplate='%{label}<br>%{text}%<br>',
            meta=frame['시가총액'], customdata=frame['종가'], text=frame[key],
            branchvalues='total', opacity=0.9,
            hovertemplate='%{label}<br>시총: %{meta}<br>종가: %{customdata}<br>' + key + ': %{text}%<extra></extra>',
        ))
        if save:
            of.plot(fig, filename=rf'./{self.__cat}_{self.__idx}.html', auto_open=False)
        fig.show()
        return

    def to_js(self):
        """
        시장 지도 데이터프레임 JavaScript 데이터 변환
        """
        self.__collect()

        yy, mm, dd = self.today[:4], self.today[4:6], self.today[6:]
        suffix = codecs.open(
            filename=os.path.join(self.archive, 'deploy/src/map-suffix.js'), mode='r', encoding='utf-8'
        ).read()

        syntax = f'document.getElementsByClassName("date")[0].innerHTML="{yy}년 {mm}월 {dd}일 종가 기준";'
        _dir = os.path.join(self.archive, 'deploy/js')
        _cnt = 1
        _js = os.path.join(_dir, f"{self.today[2:]}MM-r{_cnt}.js")
        while os.path.isfile(_js):
            _cnt += 1
            _js = os.path.join(_dir, f"{self.today[2:]}MM-r{_cnt}.js")

        for name, data in [('labels', self.__labels), ('covers', self.__covers), ('ids', self.__ids), ('bar', self.__bars)]:
            syntax += 'const %s = {\n' % name
            for var, val in data.items():
                syntax += f'\t{var}: {str(val)},\n'
            syntax += '}\n'

        _frm = self.__datum[['종목명', '종가', '시가총액', '크기',
                              'R1D', 'R1W', 'R1M', 'R3M', 'R6M', 'R1Y', 'PER', 'PBR', 'DIV',
                              'CR1D', 'CR1W', 'CR1M', 'CR3M', 'CR6M', 'CR1Y', 'CPER', 'CPBR', 'CDIV']].copy()
        _frm.fillna('-', inplace=True)
        js = _frm.to_json(orient='index', force_ascii=False)

        syntax += f"const frm = {js}\n"
        syntax += f"const group_data = {str(self.__cover)}\n"
        with codecs.open(filename=_js, mode='w', encoding='utf-8') as file:
            file.write(jsmin.jsmin(syntax + suffix))
        return

    @property
    def kosdaq(self) -> list:
        if not self.__kq:
            self.__kq = krx.get_index_portfolio_deposit_file(ticker='2001')
        return self.__kq

    @property
    def tickers(self) -> list:
        """
        시장 지도 대상 종목 선정
        """

        # 시가총액 3천억 이상 종목
        if self.__cat.startswith('WI') and not self.__idx:
            self.__tickers += self.icm[self.icm['시가총액'] >= 300000000000].index.tolist()

        # 코스피200(1028), 코스피 중형주(1003), 코스피 소형주(1004), 코스닥150(2203), 코스닥 중형주(2003)
        elif self.__cat.startswith('WI') and self.__idx:
            self.__tickers += self.deposit[self.deposit['지수코드'].astype(str) == self.__idx].index.tolist()

        # 테마 분류 종목
        elif self.__cat == 'THEME':
            self.__tickers += self.theme.index.tolist()

        # ETF
        elif self.__cat == 'ETF':
            self.__tickers += self.etf.index.tolist()

        self.__tickers = list(set(self.__tickers))
        category = list(set(self.__category.index.tolist()))
        self.__tickers = [ticker for ticker in self.__tickers if ticker in category]
        return self.__tickers

    @property
    def perform(self) -> pd.DataFrame:
        """
        종목 기간별 수익률
                 R1D   R1W    R1M    R3M    R6M    R1Y
        종목코드
        031330 -2.64 -3.37  -1.27 -18.42 -21.24  38.39
        042670 -2.85 -1.37   2.05 -15.65 -45.68  -6.20
        122870 -1.62  6.84  18.25  -2.56   3.75  29.85
        ...      ...   ...    ...    ...    ...    ...
        302440 -6.80 -7.43 -25.95 -42.80 -59.17    NaN
        006400 -6.01 -7.36 -24.56 -29.99 -33.59 -34.60
        002790 -0.94  1.40  12.65   2.39 -13.87 -25.08
        """
        _file = os.path.join(self.archive, f'market/{self.today}/perf.csv')
        if os.path.isfile(_file):
            perf = pd.read_csv(_file, index_col='종목코드')
            perf.index = perf.index.astype(str).str.zfill(6)
        else:
            perf = pd.DataFrame()

        tickers = [ticker for ticker in self.tickers if not ticker in perf.index]
        for n, ticker in enumerate(tickers):
            if self.prog == 'print':
                print(f"{(n+1)}/{len(tickers)} ({round(100 * (n+1)/len(tickers), 2)}%) ... {ticker}")
            while True:
                try:
                    other = tdatlib.stock(ticker=ticker, period=2, meta=self.icm).returns
                    perf = perf.append(other=other, ignore_index=False)
                    perf.index.name = '종목코드'
                    break
                except ConnectionError as e:
                    time.sleep(1.5)

            if n and not n % 200:
                perf.to_csv(_file)
        if tickers:
            perf.to_csv(_file)
        return perf

    @property
    def baseline(self) -> pd.DataFrame:
        """
        시장 지도 분류별 요소 취합
        """
        baseline = self.__category.join(self.perform, how='left')
        if self.__cat.startswith('WI') or self.__cat == 'THEME':
            baseline = baseline.join(self.icm[['종가', '시가총액', 'PER', 'PBR', 'DIV']], how='left')
            if self.__cat.startswith('WI') and not self.__idx:
                baseline = baseline[baseline['시가총액'] >= 300000000000]
            elif self.__cat.startswith('WI') and self.__idx:
                samples = self.deposit[self.deposit['지수코드'].astype(str) == self.__idx]
                baseline = baseline[baseline.index.isin(samples.index)]
            return baseline
        elif self.__cat == 'ETF':
            return baseline.join(self.icm[['종가', '시가총액']], how='left')

    @property
    def map_frame(self) -> pd.DataFrame:
        """
        지도 데이터프레임 생성
        """
        return self.__calc_post(
            frm=self.__calc_color(
                frm=self.__calc_reduction(
                    frm=self.__calc_pre(
                        frm=self.baseline
        ))))

    def __calc_pre(self, frm: pd.DataFrame) -> pd.DataFrame:
        """
        데이터 전처리
        """
        _base = frm.drop(index=frm.loc[frm['종가'].isna()].index)
        _base['종가'] = _base['종가'].apply(lambda p: '{:,}원'.format(int(p)))
        _base["크기"] = _base["시가총액"] / 100000000
        _base_ks = _base[~_base.index.isin(self.kosdaq)].copy()
        _base_kq = _base[_base.index.isin(self.kosdaq)].copy()
        if not _base_kq.empty:
            _base_kq['종목명'] = _base_kq['종목명'].astype(str) + '*'
        return pd.concat(objs=[_base_ks, _base_kq], axis=0).sort_values(by='섹터')

    def __calc_reduction(self, frm: pd.DataFrame):
        """
        지도용 차원 축소
        """
        m_type, m_group = self.__cat, self.__name
        if not frm.index.name == '종목코드':
            frm.index.name = '종목코드'
        _frm = frm.reset_index(level=0)
        levels = [col for col in ['종목코드', '섹터', '산업'] if col in _frm.columns]
        factors = [col for col in _frm.columns if any([col.startswith(keyword) for keyword in ['R', 'B', 'P', 'D']])]

        parent = pd.DataFrame()
        for n, level in enumerate(levels):
            child = pd.DataFrame() if n > 0 else _frm.copy().rename(columns={'섹터': '분류'})
            if '산업' in child.columns:
                child.drop(columns=['산업'], inplace=True)
            if child.empty:
                layer = _frm.groupby(levels[n:]).sum().reset_index()
                child["종목코드"] = layer[level] + f'_{m_type}_{m_group}'
                child["종목명"] = layer[level]
                child["분류"] = layer[levels[n + 1]] if n < len(levels) - 1 else m_group
                child["크기"] = layer[["크기"]]

                for _name in child['종목명']:
                    _set = _frm[_frm[level] == _name]
                    for f in factors:
                        if f == "DIV":
                            child.loc[child['종목명'] == _name, f] = _set[f].mean() if not _set.empty else 0
                        else:
                            _t = _set[_set['PER'] != 0].copy() if f == 'PER' else _set
                            child.loc[child["종목명"] == _name, f] = (_t[f] * _t['크기'] / _t['크기'].sum()).sum()
                if level == "섹터":
                    self.__bar = child["종목코드"].tolist()
            parent = parent.append(child, ignore_index=True)
            if n == len(levels) - 1:
                data = {'종목코드': f'{m_type}_{m_group}', '종목명': f'{m_group}', '분류': '', '크기': _frm['크기'].sum()}
                parent = parent.append(other=pd.DataFrame(data=data, index=[0]), ignore_index=True)

        _t = parent[parent['종목명'] == parent['분류']].copy()
        if not _t.empty:
            parent.drop(index=_t.index, inplace=True)
        return parent

    def __calc_color(self, frm:pd.DataFrame):
        _frm = frm.copy()
        _ = 2.0  # 연간 무위험 수익
        limiter = {'R1Y': _, 'R6M': 0.5 * _, 'R3M': 0.25 * _, 'R1M': 0.08 * _, 'R1W': 0.02 * _, 'R1D': 0.005 * _}
        scale = ['#F63538', '#BF4045', '#8B444E', '#414554', '#35764E', '#2F9E4F', '#30CC5A']  # Low <---> High

        colored = pd.DataFrame(index=_frm.index)
        for t, lim in limiter.items():
            neu = _frm[(-lim <= _frm[t]) & (_frm[t] < lim)].copy()
            neg, pos = _frm[_frm[t] < -lim].copy(), _frm[lim <= _frm[t]].copy()
            neg_val, pos_val = neg[t].sort_values(ascending=True).tolist(), pos[t].sort_values(ascending=True).tolist()
            neg_bin = 3 if len(neg_val) < 3 else [neg_val[int((len(neg_val) - 1) * _ / 3)] for _ in range(0, 4)]
            pos_bin = 3 if len(pos_val) < 3 else [pos_val[int((len(pos_val) - 1) * _ / 3)] for _ in range(0, 4)]
            n_color = pd.cut(neg[t], bins=neg_bin, labels=scale[:3], right=True)
            n_color.fillna(scale[0], inplace=True)
            p_color = pd.cut(pos[t], bins=pos_bin, labels=scale[4:], right=True)
            u_color = pd.Series(dtype=str) if neu.empty else pd.Series(data=[scale[3]] * len(neu), index=neu.index)
            colors = pd.concat([n_color, u_color, p_color], axis=0)
            colors.name = f'C{t}'
            colored = colored.join(colors.astype(str), how='left')
            colored.fillna(scale[3], inplace=True)

        if not self.__cat == 'ETF':
            for f in ['PBR', 'PER', 'DIV']:
                _scale = scale if f == 'DIV' else scale[::-1]
                value = _frm[_frm[f] != 0][f].dropna().sort_values(ascending=False)

                _val = value.tolist()
                limit = [_val[int(len(value) / 7) * i] for i in range(len(_scale))] + [_val[-1]]
                _color = pd.cut(value, bins=limit[::-1], labels=_scale, right=True)
                _color.name = f"C{f}"
                colored = colored.join(_color.astype(str), how='left')
                colored[_color.name].fillna(scale[0] if f == "DIV" else scale[3], inplace=True)

        _frm = frm.join(colored, how='left')
        for col in colored.columns:
            _frm.at[_frm.index[-1], col] = '#C8C8C8'
        return _frm

    def __calc_post(self, frm:pd.DataFrame):
        _frm = frm.copy()
        _frm['시가총액'] = _frm["크기"].astype(int).astype(str).apply(
            lambda v: v + "억" if len(v) < 5 else v[:-4] + '조 ' + v[-4:] + '억'
        )
        for col in _frm.columns:
            if col.startswith('P') or col.startswith('D') or col.startswith('R'):
                _frm[col] = _frm[col].apply(lambda v: round(v, 2))

        assets, covers = _frm['종목명'].values, _frm['분류'].values
        _frm['ID'] = [
            asset + f'[{covers[n]}]' if asset in assets[n+1:] or asset in assets[:n] else asset
            for n, asset in enumerate(assets)
        ]

        if not self.__cat == 'ETF':
            _frm['PER'] = _frm['PER'].apply(lambda val: val if not val == 0 else 'N/A')
        return _frm

    def __collect(self):
        targets = [
            ["WICS", '', "indful"],
            ["WICS", '1028', "indks2"], ["WICS", '1003', "indksm"], ["WICS", '1004', "indkss"],
            ["WICS", '2203', "indkq1"], ["WICS", '2003', "indkqm"],
            ["WI26", '', "secful"],
            ["WI26", '1028', "secks2"], ["WI26", '1003', "secksm"], ["WI26", '1004', "seckss"],
            ["WI26", '2203', "seckq1"], ["WI26", '2003', "seckqm"],
            ["ETF", '', "etfful"],
            ["THEME", '', "thmful"]
        ]

        for group, index, var in targets:
            self.set_option(category=group, index=index)
            print(f"Proc... 시장 지도: {group}({self.__name}) 수집 중... ")

            self.__labels[var] = self.map_frame['종목코드'].tolist()
            self.__covers[var] = self.map_frame['분류'].tolist()
            self.__ids[var] = self.map_frame['ID'].tolist()
            self.__bars[var] = self.__bar

            self.__datum = self.__datum.append(
                other=self.map_frame[~self.map_frame['종목코드'].isin(self.__datum['종목코드'])],
                ignore_index=True
            )
        self.__datum.set_index(keys=['종목코드'], inplace=True)
        self.__cover = self.__datum[
            self.__datum.index.isin([code for code in self.__datum.index if '_' in code])
        ]['종목명'].tolist()
        return



if __name__ == "__main__":
    # 코스피200(1028), 코스피 중형주(1003), 코스피 소형주(1004), 코스닥150(2203), 코스닥 중형주(2003)

    marketMap = treemap(progress='print')

    # marketMap.set_option(category='WICS')
    # marketMap.set_option(category='WICS', index='1028')
    # marketMap.set_option(category='WICS', index='1003')
    # marketMap.set_option(category='WICS', index='1004')
    # marketMap.set_option(category='WICS', index='2203')
    # marketMap.set_option(category='WICS', index='2003')
    # marketMap.set_option(category='WI26')
    # marketMap.set_option(category='WI26', index='1028')
    # marketMap.set_option(category='WI26', index='1003')
    # marketMap.set_option(category='WI26', index='1004')
    # marketMap.set_option(category='WI26', index='2203')
    # marketMap.set_option(category='WI26', index='2003')
    # marketMap.set_option(category='THEME')
    # marketMap.set_option(category='ETF')

    # print(marketMap.category)
    # print(marketMap.perform)
    # print(marketMap.baseline)
    # print(marketMap.map_frame)
    # marketMap.show()

    marketMap.to_js()
