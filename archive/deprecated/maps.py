from tdatlib.market import metadata
from datetime import datetime
from pykrx import stock as krx
import plotly.graph_objects as go
import plotly.offline as of
import pandas as pd
import os, time, codecs, jsmin, tdatlib


class toolbox:
    __progress, __map_type, __map_index = str(), str(), str()
    __tickers, __bar, __kosdaq = list(), list(), krx.get_index_portfolio_deposit_file(ticker='2001')
    __archive = archive = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'archive')
    __multiples, __returns = pd.DataFrame(), pd.DataFrame()

    def __init__(self, market:metadata):
        self.__market = market
        return

    def set_progress(self, progress:str):
        self.__progress = progress

    def get_progress(self) -> str:
        return self.__progress

    def set_type(self, map_type:str) -> None:
        self.__map_type = map_type

    def get_type(self) -> str:
        return self.__map_type

    def set_index(self, map_index:str) -> None:
        self.__map_index = map_index

    def get_index(self) -> str:
        return self.__map_index

    def set_tickers(self, tickers:list):
        self.__tickers = list(set(self.__tickers + tickers))

    @property
    def multiples(self) -> pd.DataFrame:
        """
        PER / PBR / EPS / BPS ...
        """
        if self.__multiples.empty:
            self.__multiples = self.__market.properties(
                tickers=self.__tickers,
                keys=['종가', '시가총액', 'PER', 'PBR', 'DIV']
            )
        return self.__multiples

    @property
    def returns(self) -> pd.DataFrame:
        """
        대상 종목코드별 기간별 수익률
        """
        __dir = os.path.join(self.__archive, f'bin/{datetime.today().strftime("%Y%m%d")}_returns.csv')
        if os.path.isfile(__dir):
            self.__returns = pd.read_csv(__dir, index_col='종목코드')
            self.__returns.index = self.__returns.index.astype(str).str.zfill(6)
        tickers = list(set([ticker for ticker in self.__tickers if not ticker in self.__returns.index]))
        if tickers:
            self.__returns = self.__returns.append(self.__market.returns(tickers=self.__tickers))
            self.__returns.drop_duplicates(keep='first', inplace=True)
            if self.get_progress() == 'print':
                self.__returns.index.name = '종목코드'
                self.__returns.to_csv(__dir)
        return self.__returns

    @property
    def bar(self) -> list:
        return self.__bar

    def __calc_pre(self, frm: pd.DataFrame) -> pd.DataFrame:
        """
        데이터 전처리
        """
        _base = frm.drop(index=frm.loc[frm['종가'].isna()].index)
        _base['종가'] = _base['종가'].apply(lambda p: '{:,}원'.format(int(p)))
        _base["크기"] = _base["시가총액"] / 100000000
        _base_ks = _base[~_base.index.isin(self.__kosdaq)].copy()
        _base_kq = _base[_base.index.isin(self.__kosdaq)].copy()
        if not _base_kq.empty:
            _base_kq['종목명'] = _base_kq['종목명'].astype(str) + '*'
        return pd.concat(objs=[_base_ks, _base_kq], axis=0).sort_values(by='섹터')

    def __calc_reduction(self, frm: pd.DataFrame):
        """
        지도용 차원 축소
        """
        m_type, m_group = self.get_type(), self.get_index()
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
            neg_bin = [neg_val[int((len(neg_val) - 1) * _ / 3)] for _ in range(0, 4)]
            pos_bin = [pos_val[int((len(pos_val) - 1) * _ / 3)] for _ in range(0, 4)]
            n_color = pd.cut(neg[t], bins=3 if len(neg_val) < 3 else neg_bin, labels=scale[:3], right=True)
            n_color.fillna(scale[0], inplace=True)
            p_color = pd.cut(pos[t], bins=3 if len(pos_val) < 3 else pos_bin, labels=scale[4:], right=True)
            u_color = pd.Series(dtype=str) if neu.empty else pd.Series(data=[scale[3]] * len(neu), index=neu.index)
            colors = pd.concat([n_color, u_color, p_color], axis=0)
            colors.name = f'C{t}'
            colored = colored.join(colors.astype(str), how='left')
            colored.fillna(scale[3], inplace=True)

        if not self.get_type() == 'ETF':
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

        if not self.get_type() == 'ETF':
            _frm['PER'] = _frm['PER'].apply(lambda val: val if not val == 0 else 'N/A')
        return _frm

    def is_etf_latest(self):
        """
        로컬 ETF 관리 파일 최신 여부 확인
        """
        prev = pd.read_excel(os.path.join(self.__archive, 'hdlr/TDATETF.xlsx'), index_col='종목코드')
        prev.index = prev.index.astype(str).str.zfill(6)
        curr = tdatlib.etf.list

        to_be_delete = prev[~prev.index.isin(curr.index)]
        to_be_update = curr[~curr.index.isin(prev.index)]
        if to_be_delete.empty and to_be_update.empty:
            pass
        else:
            for kind, frm in [('삭제', to_be_delete), ('추가', to_be_update)]:
                if not frm.empty:
                    print("-" * 70, f"\n▷ ETF 분류 {kind} 필요 항목: {'없음' if frm.empty else '있음'}")
                    print(frm)
            os.startfile(os.path.join(self.__archive, 'hdlr'))
        return

    def calc_frame(self, basis:pd.DataFrame) -> pd.DataFrame:
        """
        지도 데이터프레임 생성
        """
        return self.__calc_post(
            frm=self.__calc_color(
                frm=self.__calc_reduction(
                    frm=self.__calc_pre(
                        frm=basis
        ))))

    def show_frame(self, frame:pd.DataFrame, key:str='R1D', save:bool=False):
        """
        지도 Treemap
        """
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
            of.plot(fig, filename=rf'./{self.get_type()}_{self.get_index()}.html', auto_open=False)
        fig.show()
        return


class marketMap:
    class __group:
        def __init__(self, tool, group:str):
            self.__tool, self.__group = tool, group
            self.__basis = pd.DataFrame()
            if group.startswith('WI'):
                _file = os.path.join(
                    self.__tool.archive,
                    f'bin/{datetime.today().strftime("%Y%m%d")}_{group.lower()}.csv'
                )
                if os.path.isfile(_file):
                    self.__basis = pd.read_csv(_file, index_col='종목코드')
                    self.__basis.index = self.__basis.index.astype(str).str.zfill(6)
                if self.__basis.empty:
                    self.__basis = tdatlib.corporate.wics if group == 'WICS' else tdatlib.corporate.wi26
                if self.__tool.get_progress() == 'print' and not os.path.isfile(_file):
                    self.__basis.to_csv(_file)
            else:
                self.__basis = pd.read_csv(os.path.join(self.__tool.archive, f'{group}.csv'), index_col='종목코드')
                self.__basis.index = self.__basis.index.astype(str).str.zfill(6)

            return

        def frame(self, index:str=str()) -> pd.DataFrame:
            self.__tool.set_type(map_type=self.__group)
            __basis = self.__basis.copy()
            if self.__group == 'THEME':
                name = '테마'
            elif self.__group == 'ETF':
                name = self.__group
            else:
                if index:
                    __basis = __basis[__basis.index.isin(krx.get_index_portfolio_deposit_file(ticker=index))]
                    name = krx.get_index_ticker_name(ticker=index)
                else:
                    __basis = __basis.join(tdatlib.corporate.market_cap['시가총액'], how='left')
                    __basis = __basis[__basis['시가총액'] >= 300000000000].drop(columns=['시가총액'])
                    name = '전체'
            self.__tool.set_index(map_index=name)
            self.__tool.set_tickers(tickers=__basis.index.tolist())
            tail = tdatlib.etf.list[['종가', '시가총액']] if self.__group == 'ETF' else self.__tool.multiples
            __basis = __basis.join(tail, how='left')
            return self.__tool.calc_frame(__basis.join(self.__tool.returns, how='left'))

        def bar(self) -> list:
            return self.__tool.bar

        def show(self, index:str=str(), key:str='R1D', save:bool=False):
            self.__tool.show_frame(frame=self.frame(index=index), key=key, save=save)
            return

    def __init__(self, progress:str=str(), group:str='ALL'):
        self.__market = metadata(progress=progress)
        self.__toolbox = toolbox(market=self.__market)
        self.archive = self.__toolbox.archive
        if progress == 'print':
            self.__toolbox.set_progress(progress=progress)
            self.__toolbox.is_etf_latest()

        if group == 'ALL' or group == 'THEME':
            self.theme = self.__group(tool=self.__toolbox, group='THEME')
        if group == 'ALL' or group == 'ETF':
            self.etf = self.__group(tool=self.__toolbox, group='ETF')
        if group == 'ALL' or group == 'WICS':
            self.wics = self.__group(tool=self.__toolbox, group='WICS')
            time.sleep(3)
        if group == 'ALL' or group == 'WI26':
            self.wi26 = self.__group(tool=self.__toolbox, group='WI26')
            time.sleep(3)

        self.__labels, self.__covers, self.__ids, self.__bar = dict(), dict(), dict(), dict()
        self.__cover = list()
        self.__datum = pd.DataFrame(columns=['종목코드'])
        return

    def __collect__(self):
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

        for t, i, var in targets:
            self.__toolbox.set_type(map_type=t), self.__toolbox.set_index(map_index=i)
            print(f"Proc... 시장 지도: {t}({i}) 수집 중... ")

            obj = self.wics if t == 'WICS' else self.wi26 if t == 'WI26' else self.etf if t == 'ETF' else self.theme
            map_frame = obj.frame(index=i).copy()

            self.__labels[var] = map_frame['종목코드'].tolist()
            self.__covers[var] = map_frame['분류'].tolist()
            self.__ids[var] = map_frame['ID'].tolist()
            self.__bar[var] = obj.bar()

            self.__datum = self.__datum.append(
                other=map_frame[~map_frame['종목코드'].isin(self.__datum['종목코드'])],
                ignore_index=True
            )
        self.__datum.set_index(keys=['종목코드'], inplace=True)
        self.__cover = self.__datum[
            self.__datum.index.isin([code for code in self.__datum.index if '_' in code])
        ]['종목명'].tolist()
        return

    def to_js(self):
        """
        시장 지도 데이터프레임 JavaScript 데이터 변환
        :return:
        """
        self.__collect__()

        print("Proc... JavaScript 변환 중...")
        date = datetime.today()
        suffix = codecs.open(
            filename=os.path.join(self.__toolbox.archive, 'deploy/src/map-suffix.js'), mode='r', encoding='utf-8'
        ).read()

        syntax = f'document.getElementsByClassName("date")[0].innerHTML="{date.year}년 {date.month}월 {date.day}일 종가 기준";'
        _dir = os.path.join(self.__toolbox.archive, 'deploy/js')
        _cnt = 1
        _js = os.path.join(_dir, f"marketmap-{date.strftime('%Y%m%d')[2:]}-r{_cnt}.js")
        while os.path.isfile(_js):
            _cnt += 1
            _js = os.path.join(_dir, f"marketmap-{date.strftime('%Y%m%d')[2:]}-r{_cnt}.js")

        for name, data in [('labels', self.__labels), ('covers', self.__covers), ('ids', self.__ids), ('bar', self.__bar)]:
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



if __name__ == "__main__":
    pd.set_option('display.expand_frame_repr', False)

    # test = marketMap(progress='print')
    # print(test.theme.frame())
    # print(test.etf.frame())
    # print(test.wics.frame())
    # print(test.wics.frame(index='1004'))
    # print(test.wi26.frame())
    # test.wics.frame().to_csv(r'./test.csv', encoding='euc-kr')

    # test.theme.show(key='R1D', save=False)
    # test.etf.show(key='R1D', save=False)
    # test.wics.show(key='R1D', save=False)
    # test.wics.show(index='1028', key='R1W', save=False)
    # test.wi26.show(key='R1M', save=False)
    # test.wi26.show(index='2001', key='R3M', save=False)
    # test.to_js()

    myMap = marketMap(progress='print', group='WICS')
    myMap.wics.show(key='R1D')