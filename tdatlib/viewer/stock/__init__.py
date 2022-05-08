# from tdatlib.interface.stock import interface_stock
from tdatlib.viewer.stock.ohlcv import (
    object_candle,
    object_prices,
    object_volume,
    object_bollinger_band,
    object_base,

    show_basic,
    show_bollinger_band,
    show_rsi,
    show_macd,
    show_mfi,
    show_cci,
    show_stc,
    show_vortex,
    show_trix,
    show_ta
)
from tdatlib.viewer.stock.value import (
    show_overview,
    show_relative,
    show_supply,
    show_cost,
    show_multiples
)
from tdatlib.viewer.common import save
from inspect import currentframe as inner
from tqdm import tqdm
import plotly.graph_objects as go


class view_stock(interface_stock):

    def __show__(self, p: str, fname: str = str(), **kwargs):
        if not hasattr(self, f'__{p}'):
            self.__setattr__(f'__{p}', globals()[f"{fname if fname else f'show_{p}'}"](**kwargs))
        return self.__getattribute__(f'__{p}')

    def __base__(self, row_width:list, vertical_spacing:float=0.02):
        return object_base(
            row_width=row_width,
            vertical_spacing=vertical_spacing,
            candle=self.__show__(p='__candle', fname='object_candle', ohlcv=self.ohlcv),
            prices=self.__show__(p='__prices', fname='object_prices', ohlcv=self.ohlcv, currency=self.currency),
            volume=self.__show__(p='__volume', fname='object_volume', ohlcv=self.ohlcv),
            bollinger=self.__show__(p='__bollinger', fname='object_bollinger_band', ta=self.ta),
            currency=self.currency
        )

    def collect_techical_analysis(self, path:str=str()):
        process = tqdm([
            (self.basic, f'{self.name}_기술01_가격'),
            (self.bollinger_band, f'{self.name}_기술02_볼린저밴드'),
            (self.rsi, f'{self.name}_기술03_RSI'),
            (self.macd, f'{viewer.name}_기술04_MACD'),
            (self.mfi, f'{viewer.name}_기술05_MFI'),
            (self.cci, f'{viewer.name}_기술06_CCI'),
            (self.vortex, f'{viewer.name}_기술07_VORTEX'),
            (self.stc, f'{viewer.name}_기술08_STC'),
            (self.trix, f'{viewer.name}_기술09_TRIX'),
        ])
        for fig, filename in process:
            process.set_description(desc=filename)
            save(fig=fig, filename=filename, path=path)
        return

    def collect_fundamental_analysis(self, path:str=str()):
        if not self.currency == 'KRW':
            print('KRX한국거래소 상장 종목 확인 불가')
            return
        process = tqdm([
            (self.overview, f'{self.name}_기본01_기업개요'),
            (self.relative, f'{self.name}_기본02_벤치마크'),
            (self.supply, f'{self.name}_기본03_수급현황'),
            (self.cost, f'{self.name}_기본04_비용처리'),
            (self.multiples, f'{self.name}_기본05_투자배수'),
        ])
        for fig, filename in process:
            process.set_description(desc=filename)
            save(fig=fig, filename=filename, path=path)
        return

    def ta_display(self, col:str):
        return show_ta(
            ticker=self.ticker, name=self.name,
            base=self.__base__(row_width=[0.3, 0.1, 0.6], vertical_spacing=0.02),
            ta=self.ta,
            indicator=col
        )

    @property
    def basic(self) -> go.Figure:
        return self.__show__(
            inner().f_code.co_name,
            ticker=self.ticker, name=self.name, currency=self.currency,
            base=self.__base__(row_width=[0.15, 0.85], vertical_spacing=0.02),
            sma=self.sma,
            trend=self.avg_trend,
            bound=self.bound
        )

    @property
    def bollinger_band(self) -> go.Figure:
        return self.__show__(
            inner().f_code.co_name,
            ticker=self.ticker, name=self.name,
            base=self.__base__(row_width=[0.15, 0.15, 0.1, 0.6], vertical_spacing=0.02),
            ta=self.ta
        )

    @property
    def rsi(self) -> go.Figure:
        return self.__show__(
            inner().f_code.co_name,
            ticker=self.ticker, name=self.name,
            base=self.__base__(row_width=[0.25, 0.25, 0.1, 0.4], vertical_spacing=0.02),
            ta=self.ta
        )

    @property
    def macd(self) -> go.Figure:
        return self.__show__(
            inner().f_code.co_name,
            ticker=self.ticker, name=self.name,
            base=self.__base__(row_width=[0.3, 0.1, 0.6], vertical_spacing=0.02),
            ta=self.ta
        )

    @property
    def mfi(self) -> go.Figure:
        return self.__show__(
            inner().f_code.co_name,
            ticker=self.ticker, name=self.name,
            base=self.__base__(row_width=[0.3, 0.1, 0.6], vertical_spacing=0.02),
            ta=self.ta
        )

    @property
    def cci(self) -> go.Figure:
        return self.__show__(
            inner().f_code.co_name,
            ticker=self.ticker, name=self.name,
            base=self.__base__(row_width=[0.3, 0.1, 0.6], vertical_spacing=0.02),
            ta=self.ta
        )

    @property
    def vortex(self) -> go.Figure:
        return self.__show__(
            inner().f_code.co_name,
            ticker=self.ticker, name=self.name,
            base=self.__base__(row_width=[0.15, 0.35, 0.1, 0.4], vertical_spacing=0.02),
            ta=self.ta
        )

    @property
    def stc(self) -> go.Figure:
        return self.__show__(
            inner().f_code.co_name,
            ticker=self.ticker, name=self.name,
            base=self.__base__(row_width=[0.3, 0.1, 0.6], vertical_spacing=0.02),
            ta=self.ta
        )

    @property
    def trix(self) -> go.Figure:
        return self.__show__(
            inner().f_code.co_name,
            ticker=self.ticker, name=self.name,
            base=self.__base__(row_width=[0.3, 0.1, 0.6], vertical_spacing=0.02),
            trix=self.trix_sign
        )

    @property
    def overview(self) -> go.Figure:
        return self.__show__(
            inner().f_code.co_name,
            ticker=self.ticker, name=self.name,
            df_products=self.products,
            df_multifactor=self.multifactor,
            df_asset=self.asset,
            df_profit=self.profit
        )

    @property
    def relative(self) -> go.Figure:
        return self.__show__(
            inner().f_code.co_name,
            ticker=self.ticker, name=self.name,
            df_benchmark_return=self.benchmark_return,
            df_benchmark_multiple=self.benchmark_multiple
        )

    @property
    def supply(self) -> go.Figure:
        return self.__show__(
            inner().f_code.co_name,
            ticker=self.ticker, name=self.name,
            df_consensus=self.consensus,
            df_foreign_rate=self.foreign_rate,
            df_short_sell=self.short_sell,
            df_short_balance=self.short_balance
        )

    @property
    def cost(self) -> go.Figure:
        return self.__show__(
            inner().f_code.co_name,
            ticker=self.ticker, name=self.name,
            df_expenses=self.expenses,
            df_statement=self.annual_stat
        )

    @property
    def multiples(self) -> go.Figure:
        return self.__show__(
            inner().f_code.co_name,
            ticker=self.ticker, name=self.name,
            df_multiple_series=self.multiple_series,
            df_multiple_band=self.multiple_band
        )



if __name__ == "__main__":
    ticker = '253450'
    # ticker = 'TSLA'
    viewer = view_stock(ticker=ticker, period=5)

    viewer.collect_techical_analysis()
    viewer.collect_fundamental_analysis()

    # save(fig=viewer.basic, filename=f'{viewer.name}_기술_01_기본형')
    # save(fig=viewer.bollinger_band, filename=f'{viewer.name}_기술_02_볼린저밴드')
    # save(fig=viewer.rsi, filename=f'{viewer.name}_기술_03_RSI')
    # save(fig=viewer.macd, filename=f'{viewer.name}_기술_04_MACD')
    # save(fig=viewer.mfi, filename=f'{viewer.name}_기술_05_MFI')
    # save(fig=viewer.cci, filename=f'{viewer.name}_기술_06_CCI')
    # save(fig=viewer.vortex, filename=f'{viewer.name}_기술_07_VORTEX')
    # save(fig=viewer.stc, filename=f'{viewer.name}_기술_08_STC')
    # save(fig=viewer.trix, filename=f'{viewer.name}_기술_09_TRIX')
    
    # save(fig=viewer.overview, filename=f'{viewer.name}_기본_01_기업개요')
    # save(fig=viewer.relative, filename=f'{viewer.name}_기본_02_벤치마크')
    # save(fig=viewer.supply, filename=f'{viewer.name}_기본_03_수급현황')
    # save(fig=viewer.cost, filename=f'{viewer.name}_기본_04_비용처리')
    # save(fig=viewer.multiples, filename=f'{viewer.name}_기본_05_투자배수')

    # viewer.ta_display(col='volatility_ui').show()