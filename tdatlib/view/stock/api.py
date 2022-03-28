from tdatlib.view.stock.raw import *
from tdatlib import stock, archive
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.offline as of


class analyze(stock):
    __pv, __bb, __ot = go.Figure(), go.Figure(), go.Figure()

    def saveas(self, fig:go.Figure, title:str):
        """
        차트 저장
        :param fig: 차트 오브젝트 
        :param title: 차트 종류
        """
        of.plot(fig, filename=f'{archive.desktop}/{self.name}_{title}.html', auto_open=False)
        return

    @property
    def price_volume(self) -> go.Figure:
        """
        가격, 거래량 차트
        """
        if not self.__pv['data']:
            fig = make_subplots(rows=2, cols=1, row_width=[0.15, 0.85], shared_xaxes=True, vertical_spacing=0.025)

            fig.add_trace(trace=traceCandle(ohlcv=self.ohlcv, gap='일봉'), row=1, col=1)
            for name in ['시가', '고가', '저가', '종가']:
                fig.add_trace(trace=tracePrice(price=self.ohlcv[name], unit=self.currency), row=1, col=1)
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
    def bollinger_band(self) -> go.Figure:
        if not self.__bb['data']:
            fig = make_subplots(rows=3, cols=1, row_width=[0.15, 0.15, 0.7], shared_xaxes=True, vertical_spacing=0.02)

            fig.add_trace(trace=traceCandle(ohlcv=self.ohlcv, gap='일봉'), row=1, col=1)
            for name in ['시가', '고가', '저가', '종가']:
                fig.add_trace(trace=tracePrice(price=self.ohlcv[name], unit=self.currency), row=1, col=1)

            for n, col in enumerate(['upper', 'mid', 'lower']):
                name = {'upper':'상한선', 'mid':'기준선', 'lower':'하한선'}[col]
                fig.add_trace(go.Scatter(
                    name='볼린저밴드', x=self.bollinger.index, y=self.bollinger[col],
                    mode='lines', line=dict(color='rgb(184, 247, 212)'), fill='tonexty' if n else None,
                    visible=True, showlegend=False if n else True, legendgroup='볼린저밴드',
                    meta=reform(span=self.bollinger.index),
                    hovertemplate=name + '<br>날짜: %{meta}<br>값: %{y:,d}원<extra></extra>',
                ))
            fig.add_trace(trace=traceLine(data=self.bollinger.width, name='밴드폭', unit='%'), row=2, col=1)
            fig.add_trace(trace=traceLine(data=self.bollinger.signal, name='신호', unit=''), row=3, col=1)

            layout = go.Layout(
                title=f'{self.name}({self.ticker}) 볼린저밴드',
                plot_bgcolor='white',
                xaxis=setXaxis(title=str(), label=False, xranger=True), yaxis=setYaxis(title=self.currency),
                xaxis2=setXaxis(title=str(), label=False, xranger=False), yaxis2=setYaxis(title='폭[%]'),
                xaxis3=setXaxis(title='날짜', xranger=False), yaxis3=setYaxis(title='신호[-]'),
                xaxis_rangeslider=dict(visible=False)
            )
            fig.update_layout(layout)
            self.__bb = fig
        return self.__bb

    @property
    def overtrade(self) -> go.Figure:
        if not self.__ot['data']:
            fig = make_subplots(rows=4, cols=1, row_width=[0.2, 0.2, 0.2, 0.4], shared_xaxes=True, vertical_spacing=0.02)

            fig.add_trace(trace=traceCandle(ohlcv=self.ohlcv, gap='일봉'), row=1, col=1)
            for name in ['시가', '고가', '저가', '종가']:
                fig.add_trace(trace=tracePrice(price=self.ohlcv[name], unit=self.currency), row=1, col=1)
            fig.add_trace(trace=traceLine(data=self.rsi.rsi, name='RSI', unit='%'), row=2, col=1)


            layout = go.Layout(
                title=f'{self.name}({self.ticker}) 과매매(Over-Trade)',
                plot_bgcolor='white',
                xaxis=setXaxis(title=str(), label=False, xranger=True), yaxis=setYaxis(title=self.currency),
                xaxis2=setXaxis(title=str(), label=False, xranger=False), yaxis2=setYaxis(title='RSI[%]'),
                xaxis4=setXaxis(title='날짜', xranger=False), yaxis4=setYaxis(title='CCI[%]'),
                xaxis_rangeslider=dict(visible=False)
            )
            fig.update_layout(layout)
            self.__ot = fig
        return self.__ot


if __name__ == "__main__":
    t_analyze = analyze(ticker='000660')
    # t_analyze.price_volume.show()
    # t_analyze.bollinger_band.show()
    t_analyze.overtrade.show()