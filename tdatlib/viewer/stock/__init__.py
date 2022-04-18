from tdatlib.interface.stock import interface_stock
from tdatlib.viewer.stock.value import (
    show_overview,
    show_relative,
    show_supply
)
from tdatlib.viewer.common import save
from inspect import currentframe as inner
import plotly.graph_objects as go


class view_stock(interface_stock):

    def __show__(self, p: str, fname: str = str(), **kwargs):
        if not hasattr(self, f'__{p}'):
            self.__setattr__(f'__{p}', globals()[f"show_{fname if fname else p}"](**kwargs))
        return self.__getattribute__(f'__{p}')

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

if __name__ == "__main__":
    ticker = '001680'
    viewer = view_stock(ticker=ticker, period=5)

    # save(fig=viewer.overview, filename=f'{viewer.name}_00_기업개요')
    # save(fig=viewer.relative, filename=f'{viewer.name}_01_벤치마크')
    save(fig=viewer.supply, filename=f'{viewer.name}_02_수급현황')