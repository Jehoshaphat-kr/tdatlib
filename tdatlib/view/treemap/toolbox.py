import pandas as pd
from tdatlib import archive, market_kr
from pykrx import stock


market = market_kr()
class toolbox:

    def __init__(self, category:str, sub_category:str=str(), kq:list=None):
        if not category in ['WICS', 'WI26', 'ETF', 'THEME']:
            raise KeyError(f'입력 가능한 category: WICS, WI26, ETF, THEME')
        if not sub_category in [str(), '1028', '1003', '1004', '2203', '2003']:
            raise KeyError(f'입력 가능한 sub_category: 1028, 1003, 1004, 2203, 2003')

        self.cat, self.sub = category, sub_category
        self.kq = kq if kq else stock.get_index_portfolio_deposit_file(ticker='2001')

        if self.cat == 'WICS':
            self.group =  market.wics
        if self.cat == 'WI26':
            self.group =  market.wi26
        if self.cat == 'ETF':
            self.group =  market.etf_group
        if self.cat == 'THEME':
            self.group =  market.theme
        return

    def _get_mapname(self) -> str:
        """ 시장지도 분류 명 """
        if self.sub:
            # 코스피200(1028), 코스피 중형주(1003), 코스피 소형주(1004), 코스닥150(2203), 코스닥 중형주(2003)
            return archive.index_code[self.sub]
        if self.cat.startswith('WI'):
            return '전체'
        if self.cat == 'THEME':
            return '테마'
        return self.cat

    def _get_baseline(self):
        """ 분류, 기본 정보 및 sub_category(시가총액) 별 종목 제한 """
        base = self.group
        line = market.etfs[['종목명', '종가', '시가총액']] if self.cat == 'ETF' else market.icm
        baseline = base.join(other=line.drop(columns=['종목명']), how='left')

        if self.cat.startswith('WI'):
            if self.sub:
                baseline = baseline[baseline.index.isin(stock.get_index_portfolio_deposit_file(ticker=self.sub))]
            else:
                baseline = baseline[baseline['시가총액'] > 300000000000]
        perf = market.update_perf(tickers=baseline.index)
        return baseline.join(other=perf, how='left')

    def _get_mapframe(self):
        """ 시장지도 데이터 """
        return self.__calc_post().copy()

    def __calc_reduction(self) -> pd.DataFrame:
        """ 차원축소 - 1차원 지도 데이터 """
        frame = self._get_baseline().copy().reset_index(level=0)
        frame['크기'] = frame['시가총액'] / 100000000
        levels = [col for col in ['종목코드', '섹터', '산업'] if col in frame.columns]
        factors = [col for col in frame.columns if any([col.startswith(keyword) for keyword in ['R', 'B', 'P', 'D']])]
        map_name = self._get_mapname()

        parent = pd.DataFrame()
        for n, level in enumerate(levels):
            if not n:
                child = frame.rename(columns={'섹터': '분류'})
                if '산업' in child.columns:
                    child.drop(columns=['산업'], inplace=True)
            else:
                child = pd.DataFrame()
                layer = frame.groupby(levels[n:]).sum().reset_index()
                child["종목코드"] = layer[level] + f'_{self.cat}_{map_name}'
                child["종목명"] = layer[level]
                child["분류"] = layer[levels[n + 1]] if n < len(levels) - 1 else map_name
                child["크기"] = layer[["크기"]]

                for name in child['종목명']:
                    frm = frame[frame[level] == name]
                    for f in factors:
                        if f == "DIV":
                            child.loc[child['종목명'] == name, f] = frm[f].mean() if not frm.empty else 0
                        else:
                            _t = frm[frm['PER'] != 0].copy() if f == 'PER' else frm
                            child.loc[child["종목명"] == name, f] = (_t[f] * _t['크기'] / _t['크기'].sum()).sum()
                if level == "섹터":
                    self.__setattr__('_bar', child["종목코드"].tolist())
            parent = pd.concat(objs=[parent, child], axis=0, ignore_index=True)

        cover = pd.DataFrame(
            data={'종목코드': f'{self.cat}_{map_name}', '종목명': map_name, '분류': '', '크기': frame['크기'].sum()},
            index=['Cover']
        )
        map_data = pd.concat(objs=[parent, cover], axis=0, ignore_index=True)

        _t = map_data[map_data['종목명'] == map_data['분류']].copy()
        if not _t.empty:
            map_data.drop(index=_t.index, inplace=True)
        return map_data

    def __calc_colors(self) -> pd.DataFrame:
        """ 각 펙터 별 색상 결정(상대 비율) """
        _ = 2.0  # 연간 무위험 수익
        limiter = {'R1Y': _, 'R6M': 0.5 * _, 'R3M': 0.25 * _, 'R1M': 0.08 * _, 'R1W': 0.02 * _, 'R1D': 0.005 * _}
        scale = ['#F63538', '#BF4045', '#8B444E', '#414554', '#35764E', '#2F9E4F', '#30CC5A']  # Low <---> High

        frm = self.__calc_reduction().copy()
        colored = pd.DataFrame(index=frm.index)
        for t, lim in limiter.items():
            neu = frm[(-lim <= frm[t]) & (frm[t] < lim)].copy()
            neg, pos = frm[frm[t] < -lim].copy(), frm[lim <= frm[t]].copy()
            neg_val, pos_val = neg[t].sort_values(ascending=True).tolist(), pos[t].sort_values(ascending=True).tolist()
            neg_bin = 3 if len(neg_val) < 3 else [neg_val[int((len(neg_val) - 1) * _ / 3)] for _ in range(0, 4)]
            pos_bin = 3 if len(pos_val) < 3 else [pos_val[int((len(pos_val) - 1) * _ / 3)] for _ in range(0, 4)]
            n_color = pd.cut(neg[t], bins=neg_bin, labels=scale[:3], right=True)
            n_color.fillna(scale[0], inplace=True)
            p_color = pd.cut(pos[t], bins=pos_bin, labels=scale[4:], right=True)
            p_color.fillna(scale[4], inplace=True)
            u_color = pd.Series(dtype=str) if neu.empty else pd.Series(data=[scale[3]] * len(neu), index=neu.index)
            colors = pd.concat([n_color, u_color, p_color], axis=0)
            colors.name = f'C{t}'
            colored = colored.join(colors.astype(str), how='left')
            colored.fillna(scale[3], inplace=True)

        if not self.cat == 'ETF':
            for f in ['PBR', 'PER', 'DIV']:
                re_scale = scale if f == 'DIV' else scale[::-1]
                value = frm[frm[f] != 0][f].dropna().sort_values(ascending=False)

                v = value.tolist()
                limit = [v[int(len(value) / 7) * i] for i in range(len(re_scale))] + [v[-1]]
                _color = pd.cut(value, bins=limit[::-1], labels=re_scale, right=True)
                _color.fillna(re_scale[0], inplace=True)
                _color.name = f"C{f}"
                colored = colored.join(_color.astype(str), how='left')

        frm = frm.join(colored, how='left')
        for col in colored.columns:
            frm.at[frm.index[-1], col] = '#C8C8C8'
        return frm

    def __calc_post(self):
        """ 지도 데이터 후처리 """
        def rename(x):
            return x['종목명'] + "*" if x['종목코드'] in self.kq else x['종목명']
        def reform_price(x):
            return '-' if x['종가'] == '-' else '{:,}원'.format(int(x['종가']))
        def reform_cap(x):
            return f"{x['크기']}억원" if len(x['크기']) < 5 else f"{x['크기'][:-4]}조 {x['크기'][-4:]}억원"

        frame = self.__calc_colors().copy()
        frame['종가'].fillna('-', inplace=True)
        frame['크기'] = frame['크기'].astype(int).astype(str)

        frame['종목명'] = frame.apply(rename, axis=1)
        frame['종가'] = frame.apply(reform_price, axis=1)
        frame['시가총액'] = frame.apply(reform_cap, axis=1)

        ns, cs = frame['종목명'].values, frame['분류'].values
        frame['ID'] = [f'{name}[{cs[n]}]' if name in ns[n + 1:] or name in ns[:n] else name for n, name in enumerate(ns)]

        for col in frame.columns:
            if col.startswith('P') or col.startswith('D') or col.startswith('R'):
                frame[col] = frame[col].apply(lambda v: round(v, 2))

        if not self.cat == 'ETF':
            frame['PER'] = frame['PER'].apply(lambda val: val if not val == 0 else 'N/A')
        return frame