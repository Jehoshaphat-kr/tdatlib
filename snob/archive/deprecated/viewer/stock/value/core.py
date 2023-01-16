from tdatlib.archive.deprecated.dataset.stock import KR
import plotly.graph_objects as go


CD_COLORS = [
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf'   # blue-teal
]


class chart(object):

    def __init__(self, src:KR):
        self.src = src

    @property
    def trace_product(self) -> go.Pie:
        if not hasattr(self, f'__pie'):
            self.__setattr__(
                f'__pie',
                go.Pie(
                    name='Product',
                    labels=self.src.basis_products.index,
                    values=self.src.basis_products,
                    visible=True,
                    showlegend=False,
                    textfont=dict(color='white'),
                    textinfo='label+percent',
                    insidetextorientation='radial',
                    hoverinfo='label+percent'
                )
            )
        return self.__getattribute__('__pie')

    @property
    def trace_factor(self) -> dict:
        if not hasattr(self, f'__multifactor'):
            scatters = {
                col : go.Scatterpolar(
                    name=col,
                    r=self.src.basis_multifactor[col],
                    theta=self.src.basis_multifactor.index,
                    visible=True,
                    showlegend=True,
                    legendgrouptitle=dict(text='멀티팩터') if not n else None,
                    fill='toself',
                    hovertemplate=col + '<br>팩터: %{theta}<br>값: %{r}<extra></extra>'
                ) for n, col in enumerate(self.src.basis_multifactor.columns)
            }
            self.__setattr__(f'__multifactor', scatters)
        return self.__getattribute__('__multifactor')

    @property
    def trace_asset(self) -> dict:
        if not hasattr(self, '__asset'):
            scatters = {
                '자산' : go.Bar(
                    name='자산',
                    x=self.src.basis_asset.index,
                    y=self.src.basis_asset.자산총계,
                    visible=True,
                    showlegend=False,
                    marker=dict(color='green'),
                    opacity=0.9,
                    text=self.src.basis_asset.자산총계LB,
                    meta=self.src.basis_asset.부채총계LB,
                    customdata=self.src.basis_asset.자본총계LB,
                    offsetgroup=0,
                    texttemplate='',
                    hovertemplate='자산: %{text}<br>부채: %{meta}<br>자본: %{customdata}<extra></extra>'
                ),
                '부채' : go.Bar(
                    name='부채',
                    x=self.src.basis_asset.index,
                    y=self.src.basis_asset.부채총계,
                    visible=True,
                    showlegend=False,
                    marker=dict(color='red'),
                    opacity=0.8,
                    offsetgroup=0,
                    hoverinfo='skip'
                )
            }
            self.__setattr__('__asset', scatters)
        return self.__getattribute__('__asset')

    @property
    def trace_profit(self) -> dict:
        if not hasattr(self, '__profit'):
            scatters = {
                col : go.Bar(
                    name=f'연간{col}',
                    x=self.src.basis_profit.index,
                    y=self.src.basis_profit[col],
                    marker=dict(
                        color=CD_COLORS[n]
                    ),
                    opacity=0.9,
                    legendgroup=col,
                    legendgrouptitle=dict(
                        text='연간실적'
                    ) if not n else None,
                    showlegend=True,
                    meta=self.src.basis_profit[f'{col}LB'],
                    hovertemplate=col + ': %{meta}<extra></extra>',
                ) for n, col in enumerate(self.src.basis_profit.columns) if not col.endswith('LB')
            }
            self.__setattr__('__profit', scatters)
        return self.__getattribute__('__profit')

    @property
    def trace_rr(self) -> dict:
        if not hasattr(self, '__relativereturn'):
            scatters = dict()
            for n, gap in enumerate(['3M', '1Y']):
                df = self.src.basis_benchmark_return[gap].dropna()
                for m, col in enumerate(df.columns):
                    scatters[f'{gap}_{col}'] = go.Scatter(
                        name=f'{gap} {col}',
                        x=df.index,
                        y=df[col].astype(float),
                        visible=True if not n else 'legendonly',
                        showlegend=True,
                        legendgroup=f'{gap}',
                        legendgrouptitle=dict(text='수익률 비교') if not n else None,
                        xhoverformat='%Y/%m/%d',
                        hovertemplate='%{x}<br>' + f'{col}: ' + '%{y:.2f}%<extra></extra>'
                    )
            self.__setattr__('__relativereturn', scatters)
        return self.__getattribute__('__relativereturn')

    @property
    def trace_rp(self) -> dict:
        if not hasattr(self, '__relativeper'):
            df = self.src.basis_benchmark_multiple.PER.astype(float)
            scatters = {
                col : go.Bar(
                    name=col,
                    x=df[col].index,
                    y=df[col],
                    marker=dict(color=CD_COLORS[n]),
                    visible=True,
                    showlegend=True,
                    legendgrouptitle=dict(text='PER 비교') if not n else None,
                    texttemplate='%{y:.2f}',
                    textfont=dict(color='white'),
                    hovertemplate='%{x}<br>' + col + ': %{y:.2f}<extra></extra>'
                ) for n, col in enumerate(df.columns)
            }
            self.__setattr__('__relativeper', scatters)
        return self.__getattribute__('__relativeper')

    @property
    def trace_re(self) -> dict:
        if not hasattr(self, '__relativeebitda'):
            df = self.src.basis_benchmark_multiple['EV/EBITDA'].astype(float)
            scatters = {
                col : go.Bar(
                    name=col,
                    x=df[col].index,
                    y=df[col],
                    marker=dict(color=CD_COLORS[n]),
                    visible=True,
                    showlegend=True,
                    legendgrouptitle=dict(text='EV/EBITDA 비교') if not n else None,
                    texttemplate='%{y:.2f}',
                    textfont=dict(color='white'),
                    hovertemplate='%{x}<br>' + col + ': %{y:.2f}<extra></extra>'
                ) for n, col in enumerate(df.columns)
            }
            self.__setattr__('__relativeebitda', scatters)
        return self.__getattribute__('__relativeebitda')

    @property
    def trace_roe(self) -> dict:
        if not hasattr(self, '__relativeroe'):
            df = self.src.basis_benchmark_multiple.ROE.astype(float)
            scatters = {
                col: go.Bar(
                    name=col,
                    x=df[col].index,
                    y=df[col],
                    marker=dict(color=CD_COLORS[n]),
                    visible=True,
                    showlegend=True,
                    legendgrouptitle=dict(text='ROE 비교') if not n else None,
                    texttemplate='%{y:.2f}',
                    textfont=dict(color='white'),
                    hovertemplate='%{x}<br>' + col + ': %{y:.2f}%<extra></extra>'
                ) for n, col in enumerate(df.columns)
            }
            self.__setattr__('__relativeroe', scatters)
        return self.__getattribute__('__relativeroe')

    @property
    def trace_consensus(self) -> dict:
        if not hasattr(self, '__consensus'):
            scatters = {
                col : go.Scatter(
                    name=col,
                    x=self.src.basis_consensus.index,
                    y=self.src.basis_consensus[col],
                    mode='lines',
                    line=dict(
                        color='royalblue' if col.endswith('종가') else 'green',
                        dash='dot' if col.endswith('종가') else 'solid'
                    ),
                    visible=True,
                    showlegend=True,
                    legendgrouptitle=dict(text='컨센서스') if col == '목표주가' else None,
                    xhoverformat='%Y/%m/%d',
                    hovertemplate='%{x}<br>' + col + '%{y:,}원<extra></extra>'
                ) for n, col in enumerate(self.src.basis_consensus.columns) if not col == '투자의견'
            }
            self.__setattr__('__consensus', scatters)
        return self.__getattribute__('__consensus')

    @property
    def trace_foreign(self) -> dict:
        if not hasattr(self, '__foreign'):
            form = lambda x : ': %{y:,d}원' if x == '종가' else ': %{y:.2f}%'
            df = self.src.basis_foreign_rate[self.src.basis_foreign_rate != '']
            scatters = {
                f'{gap}_{label}' : go.Scatter(
                    name=f'{gap.replace("M", "개월").replace("Y", "년")}: {label}',
                    x=df[gap][label].dropna().index,
                    y=df[gap][label].dropna(),
                    line=dict(
                        color='royalblue' if label.endswith('종가') else 'brown',
                        dash='dot' if label.endswith('종가') else 'solid'
                    ),
                    visible=True if gap == '1Y' else 'legendonly',
                    showlegend=True,
                    legendgroup=gap,
                    legendgrouptitle=dict(text='외인비중') if not n else None,
                    xhoverformat='%Y/%m/%d',
                    hovertemplate='%{x}<br>' + label + form(label) + '<extra></extra>'
                ) for n, (gap, label) in enumerate(df.columns)
            }
            self.__setattr__('__foreign', scatters)
        return self.__getattribute__('__foreign')

    @property
    def trace_short(self) -> dict:
        if not hasattr(self, '__short'):
            form = lambda x: ': %{y:,d}원' if x.endswith('종가') else ': %{y:.2f}%'
            scatters = {
                col : go.Scatter(
                    name=f'공매도: {col.replace("공매도", "")}',
                    x=self.src.basis_short_sell.index,
                    y=self.src.basis_short_sell[col],
                    mode='lines',
                    line=dict(
                        color='royalblue' if col.endswith('종가') else 'red',
                        dash='dot' if col.endswith('종가') else 'solid'
                    ),
                    visible=True,
                    showlegend=True,
                    legendgrouptitle=dict(text='차입공매도 비중') if not n else None,
                    xhoverformat='%Y/%m/%d',
                    hovertemplate='%{x}<br>' + col + form(col) + '<extra></extra>'
                ) for n, col in enumerate(self.src.basis_short_sell)
            }
            self.__setattr__('__short', scatters)
        return self.__getattribute__('__short')

    @property
    def trace_balance(self) -> dict:
        if not hasattr(self, '__balance'):
            form = lambda x: ': %{y:,d}원' if x.endswith('종가') else ': %{y:.2f}%'
            scatters = {
                col: go.Scatter(
                    name=f'대차잔고: {col.replace("대차잔고", "")}',
                    x=self.src.basis_short_balance.index,
                    y=self.src.basis_short_balance[col],
                    mode='lines',
                    line=dict(
                        color='royalblue' if col.endswith('종가') else '#e377c2',
                        dash='dot' if col.endswith('종가') else 'solid'
                    ),
                    visible=True,
                    showlegend=True,
                    legendgrouptitle=dict(text='대차잔고 비중') if not n else None,
                    xhoverformat='%Y/%m/%d',
                    hovertemplate='%{x}<br>' + col + form(col) + '<extra></extra>'
                ) for n, col in enumerate(self.src.basis_short_balance)
            }
            self.__setattr__('__balance', scatters)
        return self.__getattribute__('__balance')

    @property
    def trace_cost(self) -> dict:
        if not hasattr(self, '__cost'):
            df = self.src.basis_expenses.copy()
            scatters = {
                col : go.Scatter(
                    name=col,
                    x=df[col].dropna().index,
                    y=df[col].dropna(),
                    mode='lines+markers+text',
                    text=df[col].dropna(),
                    textposition='top center',
                    texttemplate='%{y:.2f}%',
                    hovertemplate='%{x}<br>' + col + ': %{y:.2f}%<extra></extra>'
                ) for n, col in enumerate(['매출원가율', '판관비율', 'R&D투자비중'])
            }
            self.__setattr__('__cost', scatters)
        return self.__getattribute__('__cost')

    @property
    def trace_debt(self) -> go.Scatter:
        if not hasattr(self, '__debt'):
            df = self.src.basis_annual['부채비율'].dropna()
            self.__setattr__(
                '__debt',
                go.Scatter(
                    name='부채비율',
                    x=df.index,
                    y=df,
                    mode='lines+markers+text',
                    text=df,
                    textposition='top center',
                    texttemplate='%{y:.2f}%',
                    hovertemplate='%{x}<br>부채비율: %{y:.2f}%<extra></extra>'
                )
            )
        return self.__getattribute__('__debt')

    @property
    def trace_per(self) -> dict:
        if not hasattr(self, '__per'):
            form = lambda x : ': %{y:.2f}' if x == 'PER' else ': %{y:,d}원'
            scatters = {
                col : go.Scatter(
                    name=col,
                    x=self.src.basis_multiple_series.index,
                    y=self.src.basis_multiple_series[col],
                    visible=True,
                    showlegend=True,
                    legendgroup='PER',
                    legendgrouptitle=dict(
                        text='PER / EPS'
                    ) if not n else None,
                    xhoverformat='%Y/%m/%d',
                    hovertemplate='%{x}<br>' + col + form(col) + '<extra></extra>'
                ) for n, col in enumerate(['PER', 'EPS'])
            }
            self.__setattr__('__per', scatters)
        return self.__getattribute__('__per')

    @property
    def trace_pbr(self) -> dict:
        if not hasattr(self, '__pbr'):
            form = lambda x: ': %{y:.2f}' if x == 'PBR' else ': %{y:,d}원'
            scatters = {
                col: go.Scatter(
                    name=col,
                    x=self.src.basis_multiple_series.index,
                    y=self.src.basis_multiple_series[col],
                    visible=True,
                    showlegend=True,
                    legendgroup='PBR',
                    legendgrouptitle=dict(
                        text='PBR / BPS'
                    ) if not n else None,
                    xhoverformat='%Y/%m/%d',
                    hovertemplate='%{x}<br>' + col + form(col) + '<extra></extra>'
                ) for n, col in enumerate(['PBR', 'BPS'])
            }
            self.__setattr__('__pbr', scatters)
        return self.__getattribute__('__pbr')

    @property
    def trace_perband(self) -> dict:
        if not hasattr(self, '__perband'):
            per, _ = self.src.basis_multiple_band
            per = per.astype(float)
            scatters = {
                col : go.Scatter(
                    name=col,
                    x=per.index,
                    y=per[col],
                    visible=True,
                    showlegend=True,
                    line=dict(
                        color='black' if col.endswith('가') else CD_COLORS[n],
                        dash='solid' if col.endswith('가') else 'dot'
                    ),
                    legendgroup='PERBand',
                    legendgrouptitle=dict(text='PER BAND') if not n else None,
                    xhoverformat='%Y/%m/%d',
                    hovertemplate='%{x}<br>' + col +  ': %{y:,.2f}원<extra></extra>'
                ) for n, col in enumerate(per.columns)
            }
            self.__setattr__('__perband', scatters)
        return self.__getattribute__('__perband')

    @property
    def trace_pbrband(self) -> dict:
        if not hasattr(self, '__pbrband'):
            _, pbr = self.src.basis_multiple_band
            pbr = pbr.astype(float)
            scatters = {
                col: go.Scatter(
                    name=col,
                    x=pbr.index,
                    y=pbr[col],
                    visible=True,
                    showlegend=True,
                    line=dict(
                        color='black' if col.endswith('가') else CD_COLORS[n],
                        dash='solid' if col.endswith('가') else 'dot'
                    ),
                    legendgroup='PBRBand',
                    legendgrouptitle=dict(text='PBR BAND') if not n else None,
                    xhoverformat='%Y/%m/%d',
                    hovertemplate='%{x}<br>' + col + ': %{y:,d}원<extra></extra>'
                ) for n, col in enumerate(pbr.columns)
            }
            self.__setattr__('__pbrband', scatters)
        return self.__getattribute__('__pbrband')