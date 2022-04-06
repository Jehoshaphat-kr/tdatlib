from tdatlib.fetch.fundamental.fnguide import *
from pykrx import stock


class kr_fundamental:

    __summary, __html1, __html2 = str(), list(), list()
    __annual_statement, __quarter_statement = pd.DataFrame(), pd.DataFrame()
    __multi_factor, __benchmark_relative, __multiple_relative = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    __consensus, __foreigner, __short, __short_balance = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    def __init__(self, ticker:str, name:str=str()):
        self.ticker, self.__name = ticker, name
        return

    @property
    def name(self) -> str:
        if not self.__name:
            self.__name = stock.get_market_ticker_name(ticker=self.ticker)
        return self.__name

    @property
    def summary(self) -> str:
        """
        기업 개요 Summary (Text)
        """
        if not self.__summary:
            self.__summary = getCorpSummary(ticker=self.ticker)
        return self.__summary

    @property
    def product(self) -> pd.Series:
        """
        제품 구성
        """
        return getProductsPie(ticker=self.ticker)

    @property
    def annual_statement(self) -> pd.DataFrame:
        """
        연간 재무 요약
        """
        if not self.__html1:
            self.__html1 = getMainTables(ticker=self.ticker)
        if self.__annual_statement.empty:
            self.__annual_statement = getAnnualStatement(ticker=self.ticker, htmls=self.__html1)
        return self.__annual_statement

    @property
    def quarter_statement(self) -> pd.DataFrame:
        """
        분기 재무 요약
        """
        if not self.__html1:
            self.__html1 = getMainTables(ticker=self.ticker)
        if self.__quarter_statement.empty:
            self.__quarter_statement = getQuarterStatement(ticker=self.ticker, htmls=self.__html1)
        return self.__quarter_statement

    @property
    def multi_factor(self) -> pd.DataFrame:
        """
        멀티 팩터
        """
        if self.__multi_factor.empty:
            self.__multi_factor = getMultiFactor(ticker=self.ticker)
        return self.__multi_factor

    @property
    def benchmark_relative(self) -> pd.DataFrame:
        """
        벤치마크 지표와 수익률 비교
        """
        if self.__benchmark_relative.empty:
            self.__benchmark_relative = getRelReturnsBMark(ticker=self.ticker)
        return self.__benchmark_relative

    @property
    def multiple_relative(self) -> pd.DataFrame:
        """
        기초 배수 상대 지표
        """
        if self.__multiple_relative.empty:
            self.__multiple_relative = getRelMultiples(ticker=self.ticker)
        return self.__multiple_relative

    @property
    def consensus(self) -> pd.DataFrame:
        """
        컨센서스
        """
        if self.__consensus.empty:
            self.__consensus = getConsensus(ticker=self.ticker)
        return self.__consensus

    @property
    def foreigner(self) -> pd.DataFrame:
        """
        외국인 보유율
        """
        if self.__foreigner.empty:
            self.__foreigner = getForeignRate(ticker=self.ticker)
        return self.__foreigner

    @property
    def short(self) -> pd.DataFrame:
        """
        공매도 비중
        """
        if self.__short.empty:
            self.__short = getShorts(ticker=self.ticker)
        return self.__short

    @property
    def short_balance(self) -> pd.DataFrame:
        """
        대차 잔고
        """
        if self.__short_balance.empty:
            self.__short_balance = getShortBalance(ticker=self.ticker)
        return self.__short_balance

    @property
    def cost(self) -> pd.DataFrame:
        """
        각 종 비용
        """
        if not self.__html2:
            self.__html2 = getCorpTables(ticker=self.ticker)
        return getCosts(ticker=self.ticker, htmls=self.__html2)


if __name__ == "__main__":
    ticker = '005930'

    app = fundamental_krx(ticker=ticker)
    print(app.summary)
    print(app.product)
    print(app.annual_statement)
    print(app.quarter_statement)
    print(app.multi_factor)
    print(app.benchmark_relative)
    print(app.multiple_relative)
    print(app.consensus)
    print(app.foreigner)
    print(app.short)
    print(app.short_balance)
    print(app.cost)