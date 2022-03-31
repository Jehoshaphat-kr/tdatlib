from tdatlib.view.stock.raw import *
from tdatlib import stock, archive
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.offline as of


class analyze(stock):
    __pv, __bb, __ot = go.Figure(), go.Figure(), go.Figure()
    __rsi, __macd = go.Figure(), go.Figure()

    def save(self, fig:go.Figure, title:str, path:str=str()):
        """
        차트 저장
        :param fig: 차트 오브젝트 
        :param title: 차트 종류
        :param path:
        """
        if path:
            of.plot(fig, filename=f'{path}/{self.name}_{title}.html', auto_open=False)
        else:
            of.plot(fig, filename=f'{archive.desktop}/{self.name}_{title}.html', auto_open=False)
        return

    def __getbase(self, row_width:list=None, vertical_spacing:float=0.02) -> go.Figure:
        if not row_width:
            row_width = [0.15, 0.85]
        fig = make_subplots(
            rows=len(row_width), cols=1, row_width=row_width, shared_xaxes=True, vertical_spacing=vertical_spacing
        )

    @property
    def fig_pv(self) -> go.Figure:
        """
        가격, 거래량 차트
        """
        if not self.__pv['data']:
            fig = make_subplots(rows=2, cols=1, row_width=[0.15, 0.85], shared_xaxes=True, vertical_spacing=0.025)

            fig.add_trace(trace=traceCandle(ohlcv=self.ohlcv, gap='일봉'), row=1, col=1)
            for n in ['시가', '고가', '저가', '종가']:
                trace = traceLine(data=self.ohlcv[n], unit=self.currency, name=n, visible='legendonly', dtype='int')
                fig.add_trace(trace=trace, row=1, col=1)
            fig.add_trace(trace=traceVolume(volume=self.ohlcv.거래량), row=2, col=1)

            layout = go.Layout(
                title=f'{self.name}({self.ticker}) 가격/거래량',
                plot_bgcolor='white',
                xaxis=setXaxis(title=str(), label=False, xranger=True), xaxis2=setXaxis(title='날짜', xranger=False),
                yaxis=setYaxis(title=self.currency), yaxis2=setYaxis(title='거래량'),
                xaxis_rangeslider=dict(visible=False)
            )
            fig.update_layout(layout)
            self.__pv = fig
        return self.__pv

    @property
    def fig_bb(self) -> go.Figure:
        if not self.__bb['data']:
            fig = make_subplots(rows=4, cols=1, row_width=[0.15, 0.15, 0.1, 0.6], shared_xaxes=True, vertical_spacing=0.02)

            fig.add_trace(trace=traceCandle(ohlcv=self.ohlcv, gap='일봉'), row=1, col=1)
            for n in ['시가', '고가', '저가', '종가']:
                trace = traceLine(data=self.ohlcv[n], unit=self.currency, name=n, visible='legendonly', dtype='int')
                fig.add_trace(trace=trace, row=1, col=1)
            fig.add_trace(trace=traceVolume(volume=self.ohlcv.거래량), row=2, col=1)

            for n, col in enumerate(['upper', 'mid', 'lower']):
                name = {'upper':'상한선', 'mid':'기준선', 'lower':'하한선'}[col]
                fig.add_trace(go.Scatter(
                    name='볼린저밴드', x=self.bollinger.index, y=self.bollinger[col],
                    mode='lines', line=dict(color='rgb(184, 247, 212)'), fill='tonexty' if n else None,
                    visible=True, showlegend=False if n else True, legendgroup='볼린저밴드',
                    meta=reform(span=self.bollinger.index),
                    hovertemplate=name + '<br>날짜: %{meta}<br>값: %{y:,d}원<extra></extra>',
                ), row=1, col=1)
            fig.add_trace(trace=traceLine(data=self.bollinger.width, name='밴드폭', unit='%'), row=3, col=1)
            fig.add_trace(trace=traceLine(data=self.bollinger.signal, name='신호', unit=''), row=4, col=1)

            layout = go.Layout(
                title=f'{self.name}({self.ticker}) 볼린저밴드',
                plot_bgcolor='white',
                xaxis=setXaxis(title=str(), label=False, xranger=True), yaxis=setYaxis(title=self.currency),
                xaxis2=setXaxis(title=str(), label=False, xranger=False), yaxis2=setYaxis(title='거래량'),
                xaxis3=setXaxis(title=str(), label=False, xranger=False), yaxis3=setYaxis(title='폭[%]'),
                xaxis4=setXaxis(title='날짜', xranger=False), yaxis4=setYaxis(title='신호[-]'),
                xaxis_rangeslider=dict(visible=False)
            )
            fig.update_layout(layout)
            self.__bb = fig
        return self.__bb

    @property
    def fig_rsi(self) -> go.Figure:
        if not self.__rsi['data']:
            fig = make_subplots(rows=4, cols=1, row_width=[0.2, 0.2, 0.1, 0.5], shared_xaxes=True, vertical_spacing=0.02)

            fig.add_trace(trace=traceCandle(ohlcv=self.ohlcv, gap='일봉'), row=1, col=1)
            for n in ['시가', '고가', '저가', '종가']:
                trace=traceLine(data=self.ohlcv[n], unit=self.currency, name=n, visible='legendonly', dtype='int')
                fig.add_trace(trace=trace, row=1, col=1)
            fig.add_trace(trace=traceVolume(volume=self.ohlcv.거래량), row=2, col=1)

            fig.add_trace(trace=traceLine(data=self.rsi.rsi, name='RSI', unit='%'), row=3, col=1)
            fig.add_hrect(y0=70, y1=80, line_width=0, fillcolor='red', opacity=0.2, row=3, col=1)
            fig.add_hrect(y0=20, y1=30, line_width=0, fillcolor='green', opacity=0.2, row=3, col=1)

            fig.add_trace(trace=traceLine(data=self.rsi.stochastic, name='S-RSI', unit='%'), row=4, col=1)
            fig.add_trace(trace=traceLine(data=self.rsi['stochastic-signal'], name='S-RSI-Sig', unit='%'), row=4, col=1)
            fig.add_hrect(y0=80, y1=100, line_width=0, fillcolor='red', opacity=0.2, row=4, col=1)
            fig.add_hrect(y0=0, y1=20, line_width=0, fillcolor='green', opacity=0.2, row=4, col=1)

            layout = go.Layout(
                title=f'{self.name}({self.ticker}) RSI:Relative Strength Index',
                plot_bgcolor='white',
                xaxis=setXaxis(title=str(), label=False, xranger=True), yaxis=setYaxis(title=self.currency),
                xaxis2=setXaxis(title=str(), label=False, xranger=False), yaxis2=setYaxis(title='거래량'),
                xaxis3=setXaxis(title=str(), label=False, xranger=False), yaxis3=setYaxis(title='RSI[%]'),
                xaxis4=setXaxis(title='날짜', label=True, xranger=False), yaxis4=setYaxis(title='S-RSI[%]'),
                xaxis_rangeslider=dict(visible=False)
            )
            fig.update_layout(layout)
            self.__rsi = fig
        return self.__rsi

    @property
    def fig_macd(self) -> go.Figure:
        if not self.__macd['data']:
            fig = make_subplots(rows=3, cols=1, row_width=[0.3, 0.1, 0.6], shared_xaxes=True, vertical_spacing=0.02)

            fig.add_trace(trace=traceCandle(ohlcv=self.ohlcv, gap='일봉'), row=1, col=1)
            for n in ['시가', '고가', '저가', '종가']:
                trace=traceLine(data=self.ohlcv[n], unit=self.currency, name=n, visible='legendonly', dtype='int')
                fig.add_trace(trace=trace, row=1, col=1)
            fig.add_trace(trace=traceVolume(volume=self.ohlcv.거래량), row=2, col=1)

            fig.add_trace(trace=traceLine(data=self.macd.macd, name='MACD', unit=''), row=3, col=1)
            fig.add_trace(trace=traceLine(data=self.macd.signal, name='Sigal', unit=''), row=3, col=1)
            fig.add_trace(trace=traceBar(data=self.macd.histogram, name='Histogram', color='zc'), row=3, col=1)
            fig.add_hline(y=0, line_width=0.5, line_dash="dash", line_color="black", row=3, col=1)

            layout = go.Layout(
                title=f'{self.name}({self.ticker}) MACD',
                plot_bgcolor='white',
                xaxis=setXaxis(title=str(), label=False, xranger=True), yaxis=setYaxis(title=self.currency),
                xaxis2=setXaxis(title=str(), label=False, xranger=False), yaxis2=setYaxis(title='거래량'),
                xaxis3=setXaxis(title='날짜', label=True, xranger=False), yaxis3=setYaxis(title='MACD'),
                xaxis_rangeslider=dict(visible=False)
            )
            fig.update_layout(layout)
            self.__macd = fig
        return self.__macd

    @property
    def fig_ot(self) -> go.Figure:
        if not self.__ot['data']:
            fig = make_subplots(rows=4, cols=1, row_width=[0.2, 0.2, 0.2, 0.4], shared_xaxes=True, vertical_spacing=0.02)

            fig.add_trace(trace=traceCandle(ohlcv=self.ohlcv, gap='일봉'), row=1, col=1)
            for n in ['시가', '고가', '저가', '종가']:
                fig.add_trace(
                    trace=traceLine(data=self.ohlcv[n], unit=self.currency, name=n, visible='legendonly', dtype='int'),
                    row=1, col=1
                )

            fig.add_trace(trace=traceLine(data=self.rsi.rsi, name='RSI', unit='%'), row=2, col=1)
            fig.add_hrect(y0=70, y1=80, line_width=0, fillcolor='red', opacity=0.2, row=2, col=1)
            fig.add_hrect(y0=20, y1=30, line_width=0, fillcolor='green', opacity=0.2, row=2, col=1)

            fig.add_trace(trace=traceLine(data=self.rsi.stochastic, name='S-RSI', unit='%'), row=3, col=1)
            fig.add_trace(trace=traceLine(data=self.rsi['stochastic-signal'], name='S-RSI-Sig', unit='%'), row=3, col=1)
            fig.add_hrect(y0=80, y1=100, line_width=0, fillcolor='red', opacity=0.2, row=3, col=1)
            fig.add_hrect(y0=0, y1=20, line_width=0, fillcolor='green', opacity=0.2, row=3, col=1)

            fig.add_trace(trace=traceLine(data=self.cci, name='CCI', unit='%'), row=4, col=1)
            fig.add_hrect(y0=200, y1=400, line_width=0, fillcolor='red', opacity=0.2, row=4, col=1)
            fig.add_hrect(y0=100, y1=200, line_width=0, fillcolor='brown', opacity=0.2, row=4, col=1)
            fig.add_hrect(y0=-200, y1=-100, line_width=0, fillcolor='lightgreen', opacity=0.2, row=4, col=1)
            fig.add_hrect(y0=-400, y1=-200, line_width=0, fillcolor='green', opacity=0.2, row=4, col=1)

            layout = go.Layout(
                title=f'{self.name}({self.ticker}) 과매매(Over-Trade)',
                plot_bgcolor='white',
                xaxis=setXaxis(title=str(), label=False, xranger=True), yaxis=setYaxis(title=self.currency),
                xaxis2=setXaxis(title=str(), label=False, xranger=False), yaxis2=setYaxis(title='RSI[%]'),
                xaxis3=setXaxis(title=str(), label=False, xranger=False), yaxis3=setYaxis(title='S-RSI[%]'),
                xaxis4=setXaxis(title='날짜', xranger=False), yaxis4=setYaxis(title='CCI[%]'),
                xaxis_rangeslider=dict(visible=False)
            )
            fig.update_layout(layout)
            self.__ot = fig
        return self.__ot


if __name__ == "__main__":
    import random, os, datetime

    tickers = krx.get_index_portfolio_deposit_file(ticker='1028')
    ticker = random.sample(tickers, 1)[0]

    t_analyze = analyze(ticker=ticker, period=3)

    # t_analyze.fig_pv.show()
    # t_analyze.fig_bb.show()
    # t_analyze.fig_rsi.show()
    # t_analyze.fig_macd.show()
    # t_analyze.fig_ot.show()


    path = rf'C:\Users\Administrator\Desktop\tdat\{datetime.datetime.today().strftime("%Y-%m-%d")}'
    if not os.path.isdir(path):
        os.makedirs(path)
    t_analyze.save(t_analyze.fig_bb, title='볼린저밴드', path=path)
    t_analyze.save(t_analyze.fig_macd, title='MACD', path=path)
    t_analyze.save(t_analyze.fig_rsi, title='RSI', path=path)
    # t_analyze.save(t_analyze.overtrade, title='과매매')