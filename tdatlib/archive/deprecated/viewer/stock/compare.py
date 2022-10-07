from tdatlib.dataset.stock import compare
from tdatlib.archive.deprecated.viewer.tools import CD_COLORS, sketch, save
from plotly.subplots import make_subplots
from tqdm import tqdm
import plotly.graph_objects as go


class view_compare(compare):
    _skh = sketch()

    def saveall(self, tag:str, path:str=str()):
        proc = tqdm([
            (self.fig_returns, '수익률'),
            (self.fig_drawdown, '낙폭'),
            (self.fig_rsi, 'RSI'),
            (self.fig_cci_roc, 'CCI&ROC'),
            (self.fig_mfi_bb, 'MFI&Bollinger'),
            (self.fig_sharpe_ratio, '샤프비율'),
            (self.fig_profit, '수익성'),
            (self.fig_growth, '성장성'),
            (self.fig_multiple, '투자배수'),
        ])
        for n, (fig, name) in enumerate(proc):
            proc.set_description(desc=f'{tag}: {name} 비교')
            save(fig=fig, tag=tag, filename=f'R{str(n + 1).zfill(2)}_{name}{self.name_suffix}', path=path)
        return

    @property
    def name_suffix(self) -> str:
        return f"_{','.join(self.names)}"

    @property
    def fig_returns(self) -> go.Figure:
        fig = go.Figure()

        gaps = ['3M', '6M', '1Y', '2Y', '3Y', '5Y']
        data, price = self.rel_yield.copy(), self.rel_price.copy()
        for c, col in enumerate(gaps):
            for n, name in enumerate(self.names):
                d = data[(col, name)].dropna()
                p = price[price.index >= d.index[0]][name]
                scatter = go.Scatter(
                    name=name,
                    x=d.index,
                    y=d,
                    visible=False if c else True,
                    showlegend=True,
                    mode='lines',
                    line=dict(color=CD_COLORS[n]),
                    customdata=p,
                    hovertemplate=name + '<br>%{y:.2f}% / %{customdata:,}원<extra></extra>'
                )
                fig.add_trace(scatter)

        steps = []
        for i, gap in enumerate(gaps):
            label = gap.replace('M', '개월').replace('Y', '년')
            step = dict(
                method="update",
                args=[{"visible": [False] * len(fig.data)}, {"title": f"{label} 수익률 비교"}],
                label=label
            )
            for j in range(len(self.tickers)):
                step["args"][0]["visible"][len(self.tickers) * i + j] = True
            steps.append(step)
        sliders = [dict(active=0, currentvalue={"prefix": "비교 기간: "}, pad={"t": 50}, steps=steps)]

        fig.update_layout(
            title=f'{gaps[0].replace("M", "개월").replace("Y", "년")} 수익률 비교',
            plot_bgcolor='white',
            sliders=sliders,
            hovermode="x",
            hoverlabel = dict(font=dict(color='white')),
            xaxis=self._skh.x_axis(
                title='날짜', showticklabels=True,
                showspikes=True,
                spikecolor="black",
                spikesnap="cursor",
                spikemode="across",
                spikethickness=0.5,
                showline=False
            ),
            yaxis=self._skh.y_axis(
                title='수익률[%]',
                zeroline=True,
                zerolinecolor='grey',
                zerolinewidth=1,
                # showline=False
            )
        )
        return fig

    @property
    def fig_drawdown(self) -> go.Figure:
        fig = go.Figure()

        gaps = ['3M', '6M', '1Y', '2Y', '3Y', '5Y']
        data, price = self.rel_drawdown.copy(), self.rel_price.copy()
        for c, col in enumerate(gaps):
            for n, name in enumerate(self.names):
                d = data[(col, name)].dropna()
                p = price[price.index >= d.index[0]][name]
                scatter = go.Scatter(
                    name=name,
                    x=d.index,
                    y=d,
                    visible=False if c else True,
                    showlegend=True,
                    mode='lines',
                    line=dict(color=CD_COLORS[n]),
                    customdata=p,
                    hovertemplate=name + '<br>%{y:.2f}% / %{customdata:,}원<extra></extra>'
                )
                fig.add_trace(scatter)

        steps = []
        for i, gap in enumerate(gaps):
            label = gap.replace('M', '개월').replace('Y', '년')
            step = dict(
                method="update",
                args=[{"visible": [False] * len(fig.data)}, {"title": f"{label} 낙폭 비교"}],
                label=label
            )
            for j in range(len(self.tickers)):
                step["args"][0]["visible"][len(self.tickers) * i + j] = True
            steps.append(step)
        sliders = [dict(active=0, currentvalue={"prefix": "비교 기간: "}, pad={"t": 50}, steps=steps)]

        fig.update_layout(
            title=f'{gaps[0].replace("M", "개월").replace("Y", "년")} 낙폭 비교',
            plot_bgcolor='white',
            sliders=sliders,
            hovermode="x",
            hoverlabel=dict(font=dict(color='white')),
            xaxis=self._skh.x_axis(
                title='날짜', showticklabels=True,
                showspikes=True,
                spikecolor="black",
                spikesnap="cursor",
                spikemode="across",
                spikethickness=0.5,
                showline=False
            ),
            yaxis=self._skh.y_axis(
                title='낙폭[%]',
                zeroline=True,
                zerolinecolor='grey',
                zerolinewidth=1,
                # showline=False
            )
        )
        return fig

    @property
    def fig_rsi(self) -> go.Figure:
        fig = make_subplots(
            rows=2, cols=1,
            vertical_spacing=0.1,
            subplot_titles=("RSI", "Stochastic-RSI"),
            shared_xaxes=True,
            specs=[[{"type": "xy"}], [{"type": "xy"}]]
        )

        data = self.rel_rsi.copy()
        for n, col in enumerate(data.columns):
            scatter = go.Scatter(
                name=f'{col}',
                x=data.index,
                y=data[col],
                mode='lines',
                line=dict(color=CD_COLORS[n]),
                legendgroup='RSI',
                legendgrouptitle=dict(text='RSI 비교') if not n else None,
                showlegend=True,
                visible=True,
                hovertemplate=col + ': %{y:.2f}%<extra></extra>'
            )
            fig.add_trace(scatter, row=1, col=1)
        fig.add_hrect(y0=70, y1=90, line_width=0, fillcolor='red', opacity=0.2, row=1, col=1)
        fig.add_hrect(y0=10, y1=30, line_width=0, fillcolor='green', opacity=0.2, row=1, col=1)
        fig.add_hline(y=80, line_width=0.5, line_dash="dash", line_color="black", row=1, col=1)
        fig.add_hline(y=20, line_width=0.5, line_dash="dash", line_color="black", row=1, col=1)

        data = self.rel_stoch.copy()
        for n, col in enumerate(data.columns):
            scatter = go.Scatter(
                name=f'{col}',
                x=data.index,
                y=data[col],
                mode='lines',
                line=dict(color=CD_COLORS[n]),
                legendgroup='Stochastic',
                legendgrouptitle=dict(text='Stochastic RSI 비교') if not n else None,
                showlegend=True,
                visible=True,
                hovertemplate=col + ': %{y:.2f}[%]<extra></extra>'
            )
            fig.add_trace(scatter, row=2, col=1)
        fig.add_hrect(y0=80, y1=100, line_width=0, fillcolor='red', opacity=0.2, row=2, col=1)
        fig.add_hrect(y0=0, y1=20, line_width=0, fillcolor='green', opacity=0.2, row=2, col=1)
        fig.add_hline(y=90, line_width=0.5, line_dash="dash", line_color="black", row=2, col=1)
        fig.add_hline(y=10, line_width=0.5, line_dash="dash", line_color="black", row=2, col=1)

        fig.update_layout(
            title=f'RSI 비교',
            plot_bgcolor='white',
            legend=dict(groupclick="toggleitem"),
            hovermode="x",
            hoverlabel=dict(font=dict(color='white')),
            xaxis=self._skh.x_axis(
                title='', showticklabels=True, rangeselector=True,
                showspikes=True,
                spikecolor="black",
                spikesnap="cursor",
                spikemode="across",
                spikethickness=0.5,
                showline=False
            ),
            xaxis2=self._skh.x_axis(
                title='날짜', showticklabels=True, rangeselector=False,
                showspikes=True,
                spikecolor="black",
                spikesnap="cursor",
                spikemode="across",
                spikethickness=0.5,
                showline=False
            ),
            yaxis=self._skh.y_axis(title='RSI[%]'),
            yaxis2=self._skh.y_axis(title='Stochastic-RSI[%]')
        )
        return fig

    @property
    def fig_cci_roc(self) -> go.Figure:
        fig = make_subplots(
            rows=2, cols=1,
            vertical_spacing=0.1,
            subplot_titles=("CCI", "ROC"),
            shared_xaxes=True,
            specs=[[{"type": "xy"}], [{"type": "xy"}]]
        )

        data = self.rel_cci.copy()
        for n, col in enumerate(data.columns):
            scatter = go.Scatter(
                name=f'{col}',
                x=data.index,
                y=data[col],
                mode='lines',
                line=dict(color=CD_COLORS[n]),
                showlegend=True,
                legendgrouptitle=dict(text='CCI 비교') if not n else None,
                visible=True,
                legendgroup='CCI',
                hovertemplate=col + ': %{y:.2f}%<extra></extra>'
            )
            fig.add_trace(scatter, row=1, col=1)
        fig.add_hrect(y0=200, y1=400, line_width=0, fillcolor='red', opacity=0.2, row=1, col=1)
        fig.add_hrect(y0=100, y1=200, line_width=0, fillcolor='brown', opacity=0.2, row=1, col=1)
        fig.add_hrect(y0=-200, y1=-100, line_width=0, fillcolor='lightgreen', opacity=0.4, row=1, col=1)
        fig.add_hrect(y0=-400, y1=-200, line_width=0, fillcolor='green', opacity=0.2, row=1, col=1)

        data = self.rel_roc.copy()
        for n, col in enumerate(data.columns):
            scatter = go.Scatter(
                name=f'{col}',
                x=data.index,
                y=data[col],
                mode='lines',
                line=dict(color=CD_COLORS[n]),
                showlegend=True,
                legendgrouptitle=dict(text='ROC 비교') if not n else None,
                visible=True,
                legendgroup='ROC',
                hovertemplate=col + ': %{y:.2f}%<extra></extra>'
            )
            fig.add_trace(scatter, row=2, col=1)
        fig.add_hrect(y0=20, y1=30, line_width=0, fillcolor='red', opacity=0.2, row=2, col=1)
        fig.add_hrect(y0=10, y1=20, line_width=0, fillcolor='brown', opacity=0.2, row=2, col=1)
        fig.add_hrect(y0=-20, y1=-10, line_width=0, fillcolor='lightgreen', opacity=0.4, row=2, col=1)
        fig.add_hrect(y0=-30, y1=-20, line_width=0, fillcolor='green', opacity=0.2, row=2, col=1)

        fig.update_layout(
            title=f'CCI / ROC 비교',
            plot_bgcolor='white',
            legend=dict(groupclick="toggleitem"),
            hovermode="x",
            hoverlabel=dict(font=dict(color='white')),
            xaxis=self._skh.x_axis(
                title='', showticklabels=True, rangeselector=True,
                showspikes=True,
                spikecolor="black",
                spikesnap="cursor",
                spikemode="across",
                spikethickness=0.5,
                showline=False
            ),
            xaxis2=self._skh.x_axis(
                title='날짜', showticklabels=True, rangeselector=False,
                showspikes=True,
                spikecolor="black",
                spikesnap="cursor",
                spikemode="across",
                spikethickness=0.5,
                showline=False
            ),
            yaxis=self._skh.y_axis(title='CCI'),
            yaxis2=self._skh.y_axis(title='ROC')
        )
        return fig

    @property
    def fig_mfi_bb(self) -> go.Figure:
        fig = make_subplots(
            rows=2, cols=1,
            vertical_spacing=0.11,
            subplot_titles=("MFI", "Bollinger-Band Signal"),
            shared_xaxes=True,
            specs=[[{"type": "xy"}], [{"type": "xy"}]]
        )

        data = self.rel_mfi.copy()
        for n, col in enumerate(data.columns):
            scatter = go.Scatter(
                name=f'{col}',
                x=data.index,
                y=data[col],
                visible=True,
                mode='lines',
                line=dict(color=CD_COLORS[n]),
                showlegend=True,
                legendgroup='MFI',
                legendgrouptitle=dict(text='MFI 비교') if not n else None,
                hovertemplate=col + ': %{y:.2f}[%]<extra></extra>'
            )
            fig.add_trace(scatter, row=1, col=1)
        fig.add_hrect(y0=80, y1=100, line_width=0, fillcolor='red', opacity=0.2, row=1, col=1)
        fig.add_hline(y=90, line_width=0.5, line_dash="dash", line_color="black", row=1, col=1)
        fig.add_hrect(y0=0, y1=20, line_width=0, fillcolor='lightgreen', opacity=0.4, row=1, col=1)
        fig.add_hline(y=10, line_width=0.5, line_dash="dash", line_color="black", row=1, col=1)

        data = self.rel_bb.copy()
        for n, col in enumerate(data.columns):
            scatter = go.Scatter(
                name=f'{col}',
                x=data.index,
                y=data[col],
                visible=True,
                mode='lines',
                line=dict(color=CD_COLORS[n]),
                showlegend=True,
                legendgroup='BB',
                legendgrouptitle=dict(text='BB 신호 비교') if not n else None,
                hovertemplate=col + ': %{y:.2f}[-]<extra></extra>'
            )
            fig.add_trace(scatter, row=2, col=1)
        fig.add_hrect(y0=1, y1=1.5, line_width=0, fillcolor='red', opacity=0.2, row=2, col=1)
        fig.add_hrect(y0=-0.5, y1=0, line_width=0, fillcolor='lightgreen', opacity=0.4, row=2, col=1)

        fig.update_layout(
            title=f'MFI / Bollinger Band 신호 비교',
            plot_bgcolor='white',
            legend=dict(groupclick="toggleitem"),
            hovermode="x",
            hoverlabel=dict(font=dict(color='white')),
            xaxis=self._skh.x_axis(
                title='', showticklabels=True, rangeselector=True,
                showspikes=True,
                spikecolor="black",
                spikesnap="cursor",
                spikemode="across",
                spikethickness=0.5,
                showline=False
            ),
            xaxis2=self._skh.x_axis(
                title='날짜', showticklabels=True, rangeselector=False,
                showspikes=True,
                spikecolor="black",
                spikesnap="cursor",
                spikemode="across",
                spikethickness=0.5,
                showline=False
            ),
            yaxis=self._skh.y_axis(title='MFI'),
            yaxis2=self._skh.y_axis(title='BB-Sig')
        )
        return fig

    @property
    def fig_sharpe_ratio(self) -> go.Figure:
        fig = go.Figure()

        gaps = ['3M', '6M', '1Y', '2Y', '3Y', '5Y']
        tags = ['3개월', '6개월', '1년', '2년', '3년', '5년']
        data = self.rel_sharpe_ratio.copy()
        for t, gap in enumerate(gaps):
            for n, name in enumerate(self.names):
                d = data[name]
                fig.add_trace(go.Scatter(
                    name=name,
                    x=[d.loc[gap, 'risk']],
                    y=[d.loc[gap, 'cagr']],
                    mode='markers',
                    visible=False if t else True,
                    showlegend=True,
                    marker=dict(color=CD_COLORS[n], size=d.loc[gap, 'cap'], symbol='circle'),
                    hovertemplate=name + '<br>변동성: %{x:.2f}%<br>CAGR: %{y:.2f}%<br><extra></extra>'
                ))

            loc = [data[name].loc[gap, 'risk'] for name in self.names]
            x = [0.8*min(loc), 1.2 * max(loc)]
            fig.add_trace(go.Scatter(
                name='기준선',
                x=x,
                y=[0.8 * x[0], 0.8 * x[1]],
                mode='lines',
                line=dict(color='black', dash='dot', width=0.5),
                hoverinfo='skip',
                visible=False if t else True,
                showlegend=False
            ))

        steps = []
        for i in range(len(gaps)):
            step = dict(
                method="update",
                args=[
                    {"visible": [False] * len(fig.data)},
                    {"title": f"{tags[i]}({gaps[i]}) 샤프비율 비교"}
                ],
                label=tags[i]
            )
            for j in range(len(self.tickers) + 1):
                step["args"][0]["visible"][(len(self.tickers) + 1) * i + j] = True
            steps.append(step)
        sliders = [dict(active=0, currentvalue={"prefix": "비교 기간: "}, pad={"t": 50}, steps=steps)]

        fig.update_layout(
            title=f'{tags[0]}({gaps[0]}) 수익률 비교',
            plot_bgcolor='white',
            sliders=sliders,
            xaxis=dict(
                title='변동성[%]',
                showgrid=True,
                gridcolor='lightgrey',
                autorange=True
            ),
            yaxis=dict(
                title='CAGR[%]',
                showgrid=True,
                gridcolor='lightgrey',
                autorange=True,
                zeroline=True,
                zerolinecolor='grey',
                zerolinewidth=1
            )
        )
        return fig

    @property
    def fig_profit(self) -> go.Figure:
        fig = make_subplots(
            rows=2, cols=2,
            vertical_spacing=0.11,
            horizontal_spacing=0.1,
            subplot_titles=("영업이익률", "배당수익률", "ROA", "ROE"),
            specs=[
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "bar"}]
            ]
        )

        data = self.rel_profit.copy()
        columns = list()
        for y, col in data.columns:
            if not y in columns:
                columns.append(y)
        col_vis = [col for col in columns if not '(' in col][-1]

        for n, col in enumerate(columns):
            sub = data[col]
            for m, key in enumerate(sub.columns):
                fig.add_trace(go.Bar(
                    name=col,
                    x=sub.index,
                    y=sub[key],
                    visible=True if col == col_vis else 'legendonly',
                    showlegend=False if m else True,
                    legendgroup=col,
                    texttemplate='%{y}%',
                    hovertemplate='분기: ' + col + '<br>' + key + ': %{y}%<extra></extra>'
                ), row=1 if m < 2 else 2, col=2 if m % 2 else 1)

        fig.update_layout(
            title='수익성 비교',
            plot_bgcolor='white'
        )
        fig.update_yaxes(
            title_text="[-]",
            showgrid=True,
            gridcolor='lightgrey'
        )
        return fig

    @property
    def fig_growth(self) -> go.Figure:
        fig = make_subplots(
            rows=2, cols=2,
            vertical_spacing=0.11,
            horizontal_spacing=0.1,
            subplot_titles=("매출성장율", "영업이익성장율", "EPS성장율", "PEG"),
            specs=[
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "bar"}]
            ]
        )

        data = self.rel_growth.copy()
        columns = list()
        for y, col in data.columns:
            if not y in columns:
                columns.append(y)

        for n, col in enumerate(columns):
            sub = data[col]
            for m, key in enumerate(sub.columns):
                u = '' if key == 'PEG' else '%'
                fig.add_trace(go.Bar(
                    name=col,
                    x=sub.index,
                    y=sub[key],
                    visible=True if col.endswith('현재') else 'legendonly',
                    showlegend=False if m else True,
                    legendgroup=col,
                    texttemplate='%{y}' + u,
                    hovertemplate='분기: ' + col + '<br>' + key + ': %{y}' + u + '<extra></extra>'
                ), row=1 if m < 2 else 2, col=2 if m % 2 else 1)

        fig.update_layout(
            title='성장성 비교',
            plot_bgcolor='white'
        )
        fig.update_yaxes(
            title_text="[-]",
            showgrid=True,
            gridcolor='lightgrey'
        )
        return fig

    @property
    def fig_multiple(self) -> go.Figure:
        fig = make_subplots(
            rows=2, cols=2,
            vertical_spacing=0.11,
            horizontal_spacing=0.1,
            subplot_titles=("PSR", "EV/EBITDA", "PER", "PBR"),
            specs=[
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "bar"}]
            ]
        )

        data = self.rel_multiple.copy()
        fig.add_trace(go.Bar(
            name='',
            x=data.index,
            y=data.PSR,
            visible=True,
            showlegend=False,
            meta=data.SPS,
            customdata=data.종가,
            texttemplate='%{y}',
            hovertemplate='%{x}<br>종가: %{customdata:,d}원<br>SPS: %{meta:,.2f}원<extra></extra>'
        ), row=1, col=1)

        fig.add_trace(go.Bar(
            name='',
            x=data.index,
            y=data['EV/EBITDA'],
            visible=True,
            showlegend=False,
            meta=data.EBITDAPS,
            customdata=data.종가,
            texttemplate='%{y}',
            hovertemplate='%{x}<br>종가: %{customdata:,d}원<br>EBITDA-PS: %{meta:,.2f}원<extra></extra>'
        ), row=1, col=2)

        fig.add_trace(go.Bar(
            name='',
            x=data.index,
            y=data.PER,
            visible=True,
            showlegend=False,
            meta=data.EPS,
            customdata=data.종가,
            texttemplate='%{y}',
            hovertemplate='%{x}<br>종가: %{customdata:,d}원<br>EPS: %{meta:,.2f}원<extra></extra>'
        ), row=2, col=1)

        fig.add_trace(go.Bar(
            name='',
            x=data.index,
            y=data.PBR,
            visible=True,
            showlegend=False,
            meta=data.BPS,
            customdata=data.종가,
            texttemplate='%{y}',
            hovertemplate='%{x}<br>종가: %{customdata:,d}원<br>BPS: %{meta:,.2f}원<extra></extra>'
        ), row=2, col=2)

        fig.update_layout(
            title='투자배수 비교',
            plot_bgcolor='white'
        )
        fig.update_yaxes(
            title_text="[-]",
            showgrid=True,
            gridcolor='lightgrey'
        )
        return fig


if __name__ == "__main__":

    from tdatlib.dataset import stock
    # t_tickers = ['TSLA', 'MSFT', 'GOOG', 'ZM']
    # t_tickers = ['1028', '005930', '000660', '058470', '000990']
    # t_tickers = ['005930', '000660', '058470', '000990']
    # t_tickers = ['005930', '000660', '000990', '058470', '005290', '357780']
    # t_tickers = ['105560', '055550', '316140', '024110']
    ticker = '253450'
    my_stock = stock.KR(ticker=ticker, period=3)
    _, relatives = my_stock.relatives

    t_compare = view_compare(tickers=relatives, period=3)
    # t_compare.fig_returns.show()
    # t_compare.fig_drawdown.show()
    # t_compare.fig_rsi.show()
    # t_compare.fig_cci_roc.show()
    # t_compare.fig_mfi_bb.show()
    # t_compare.fig_sharpe_ratio.show()
    # t_compare.fig_profit.show()
    # t_compare.fig_growth.show()
    t_compare.fig_multiple.show()

    # save(t_compare.fig_returns, filename='00_수익률 비교')
    # save(t_compare.fig_drawdown, filename='01_낙폭 비교')
    # save(t_compare.fig_rsi, filename='02_RSI 비교')
    # save(t_compare.fig_cci_roc, filename='03_CCI_ROC')
    # save(t_compare.fig_mfi_bb, filename='04_MFI_B-Sig')
    # save(t_compare.fig_sharpe_ratio, filename='05_샤프비율 비교')
    # save(t_compare.fig_profit, filename='06_수익성 비교')
    # save(t_compare.fig_growth, filename='07_성장성 비교')
    # save(t_compare.fig_multiple, filename='08_투자배수 비교')
