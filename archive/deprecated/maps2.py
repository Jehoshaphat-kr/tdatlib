from tdatlib.market import metadata
from datetime import datetime
from pykrx import stock as krx
import plotly.graph_objects as go
import plotly.offline as of
import pandas as pd
import os, time, codecs, jsmin, tdatlib


class map_box:
    __group, __tickers, __name, __bar = str(), list(), str(), list()
    __frame, __returns, __kq = pd.DataFrame(), pd.DataFrame(), krx.get_index_portfolio_deposit_file(ticker='2001')

    def __init__(self, meta:metadata):
        self.meta= meta
        self.debug = True if self.meta.prog == 'print' else False
        self.archive = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'archive')

        self.f_returns = os.path.join(self.archive, f'bin/{datetime.today().strftime("%Y%m%d")}_returns.csv')
        if os.path.isfile(self.f_returns):
            self.__returns = pd.read_csv(self.f_returns, index_col='종목코드')
            self.__returns.index = self.__returns.index.astype(str).str.zfill(6)
            self.__returns.drop_duplicates(inplace=True)
        return

    @property
    def frame(self) -> pd.DataFrame:
        return self.__frame

    @property
    def bar(self) -> list:
        return self.__bar

    def set_basis(self, group:str):
        """
        기저(BASIS) 시장 지도 분류 데이터프레임
        """
        self.__group = group
        if group == 'WICS':
            self.__frame = tdatlib.corporate.wics
        elif group == 'WI26':
            self.__frame = tdatlib.corporate.wi26
        elif group == 'THEME' or group == 'ETF':
            self.__frame = pd.read_csv(os.path.join(self.archive, f'{group}.csv'), index_col='종목코드')
            self.__frame.index = self.__frame.index.astype(str).str.zfill(6)
        if self.debug and group.startswith('WI'):
            file = os.path.join(self.archive, f'bin/{datetime.today().strftime("%Y%m%d")}_{group.lower()}.csv')
            if not os.path.isfile(file):
                self.__frame.to_csv(file)
        return

    def set_tickers(self, tickers:list):
        """
        기저 데이터프레임 구속 조건(대상 종목) 설정
        """
        self.__tickers = tickers
        if tickers:
            self.__frame = self.__frame[self.__frame.index.isin(tickers)].copy()
        return

    def set_name(self, name:str):
        self.__name = name
        return

    def set_returns(self):
        """
        기저 데이터프레임 수익률 병합
        """
        add = [ticker for ticker in self.__frame.index if not ticker in self.__returns.index]
        if add:
            returns = self.meta.returns(tickers=add)
            self.__returns = pd.concat(objs=[self.__returns, returns], axis=0)
            self.__returns.drop_duplicates(inplace=True)

        self.__frame = self.__frame.join(self.__returns, how='left')
        if self.debug:
            self.__returns.index.name = '종목코드'
            self.__returns.to_csv(self.f_returns)
        return

    def set_multiples(self):
        """
        기저 데이터프레임 투자 배수 병합
        """
        if self.__group == 'ETF':
            multiples = tdatlib.etf.list[['종가', '시가총액']]
        else:
            multiples = self.meta.market[['종가', '시가총액', 'PER', 'PBR', 'DIV']]
        self.__frame = self.__frame.join(multiples, how='left')
        return

    def calc_pre(self):
        """
        데이터 전처리
        """
        _base = self.__frame.drop(index=self.__frame.loc[self.__frame['종가'].isna()].index)
        _base['종가'] = _base['종가'].apply(lambda p: '{:,}원'.format(int(p)))
        _base["크기"] = _base["시가총액"] / 100000000
        _base_ks = _base[~_base.index.isin(self.__kq)].copy()
        _base_kq = _base[_base.index.isin(self.__kq)].copy()
        if not _base_kq.empty:
            _base_kq['종목명'] = _base_kq['종목명'].astype(str) + '*'
        self.__frame = pd.concat(objs=[_base_ks, _base_kq], axis=0).sort_values(by='섹터')
        return

    def calc_reduction(self):
        """
        지도용 차원 축소
        """
        m_type, m_group = self.__group, self.__name
        if not self.__frame.index.name == '종목코드':
            self.__frame.index.name = '종목코드'
        _frm = self.__frame.reset_index(level=0)
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
        self.__frame = parent
        return

    def calc_color(self):
        _frm = self.__frame.copy()
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

        if not self.__group == 'ETF':
            for f in ['PBR', 'PER', 'DIV']:
                _scale = scale if f == 'DIV' else scale[::-1]
                value = _frm[_frm[f] != 0][f].dropna().sort_values(ascending=False)

                _val = value.tolist()
                limit = [_val[int(len(value) / 7) * i] for i in range(len(_scale))] + [_val[-1]]
                _color = pd.cut(value, bins=limit[::-1], labels=_scale, right=True)
                _color.name = f"C{f}"
                colored = colored.join(_color.astype(str), how='left')
                colored[_color.name].fillna(scale[0] if f == "DIV" else scale[3], inplace=True)

        _frm = self.__frame.join(colored, how='left')
        for col in colored.columns:
            _frm.at[_frm.index[-1], col] = '#C8C8C8'
        self.__frame = _frm
        return

    def calc_post(self):
        _frm = self.__frame.copy()
        _frm['시가총액'] = _frm["크기"].astype(int).astype(str).apply(
            lambda v: v + "억" if len(v) < 5 else v[:-4] + '조 ' + v[-4:] + '억'
        )
        for col in _frm.columns:
            if col.startswith('P') or col.startswith('D') or col.startswith('R'):
                _frm[col] = _frm[col].apply(lambda v: round(v, 2))

        assets, covers = _frm['종목명'].values, _frm['분류'].values
        _frm['ID'] = [
            f'{asset}_{covers[n]}' if asset in assets[n+1:] or asset in assets[:n] else asset
            for n, asset in enumerate(assets)
        ]

        if not self.__group == 'ETF':
            _frm['PER'] = _frm['PER'].apply(lambda val: val if not val == 0 else 'N/A')
        self.__frame = _frm
        return

    def is_etf_latest(self):
        """
        로컬 ETF 관리 파일 최신 여부 확인
        """
        prev = pd.read_excel(os.path.join(self.archive, 'hdlr/TDATETF.xlsx'), index_col='종목코드')
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
            os.startfile(os.path.join(self.archive, 'hdlr'))
        return


class market_map(map_box):
    __labels, __covers, __ids, __bars = dict(), dict(), dict(), dict()
    __cover, __datum = list(), pd.DataFrame(columns=['종목코드'])
    def __init__(self, meta:metadata):
        super().__init__(meta=meta)

    def set_frame(self, group:str, index:str):
        """
        시장 지도 데이터프레임 생성
        """
        if group == 'ETF':
            self.is_etf_latest()

        if group == 'ETF' or group == 'THEME':
            tickers = index
            name = group
        else:
            if index:
                tickers = krx.get_index_portfolio_deposit_file(ticker=index)
                name = krx.get_index_ticker_name(ticker=index)
            else:
                tickers = self.meta.market[self.meta.market['시가총액'] >= 300000000000].index.tolist()
                name = group
        self.set_basis(group=group)
        self.set_tickers(tickers=tickers)
        self.set_name(name=name)
        self.set_returns()
        self.set_multiples()

        self.calc_pre()
        self.calc_reduction()
        self.calc_color()
        self.calc_post()
        return

    def show(self, group:str, index:str=str(), key:str='R1D', save:bool=False):
        """
        지도 Treemap
        """
        self.set_frame(group=group, index=index)
        fig = go.Figure()
        fig.add_trace(go.Treemap(
            ids=self.frame['ID'], labels=self.frame['종목명'], parents=self.frame['분류'], values=self.frame['크기'],
            marker=dict(colors=self.frame[f'C{key}']),
            textfont=dict(color='#ffffff'), textposition='middle center', texttemplate='%{label}<br>%{text}%<br>',
            meta=self.frame['시가총액'], customdata=self.frame['종가'], text=self.frame[key],
            branchvalues='total', opacity=0.9,
            hovertemplate='%{label}<br>시총: %{meta}<br>종가: %{customdata}<br>' + key + ': %{text}%<extra></extra>',
        ))
        if save:
            of.plot(fig, filename=rf'./{group}_{index}.html', auto_open=False)
        fig.show()
        return

    def __collect_maps(self):
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
            print(f"Proc... 시장 지도: {group}({index}) 수집 중... ")
            self.set_frame(group=group, index=index)

            self.__labels[var] = self.frame['종목코드'].tolist()
            self.__covers[var] = self.frame['분류'].tolist()
            self.__ids[var] = self.frame['ID'].tolist()
            self.__bars[var] = self.bar

            self.__datum = self.__datum.append(
                other=self.frame[~self.frame['종목코드'].isin(self.__datum['종목코드'])],
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
        self.__collect_maps()

        print("Proc... JavaScript 변환 중...")
        date = datetime.today()
        suffix = codecs.open(
            filename=os.path.join(self.archive, 'deploy/src/map-suffix.js'), mode='r', encoding='utf-8'
        ).read()

        syntax = f'document.getElementsByClassName("date")[0].innerHTML="{date.year}년 {date.month}월 {date.day}일 종가 기준";'
        _dir = os.path.join(self.archive, 'deploy/js')
        _cnt = 1
        _js = os.path.join(_dir, f"marketmap-{date.strftime('%Y%m%d')[2:]}-r{_cnt}.js")
        while os.path.isfile(_js):
            _cnt += 1
            _js = os.path.join(_dir, f"marketmap-{date.strftime('%Y%m%d')[2:]}-r{_cnt}.js")

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


if __name__ == "__main__":
    pd.set_option('display.expand_frame_repr', False)

    metadata = metadata(progress='print')
    myMap = market_map(meta=metadata)
    # myMap.show(group='THEME', index=str(), key='R1D', save=False)
    # myMap.show(group='ETF', index=str(), key='R1D', save=False)
    # myMap.show(group='WI26', index=str(), key='R1D', save=False)
    # myMap.show(group='WICS', index=str(), key='R1D', save=False)
    myMap.show(group='WICS', index='1028', key='R1D', save=False)

    myMap.to_js()
