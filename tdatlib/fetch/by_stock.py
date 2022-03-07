import requests, json
import pandas as pd
import numpy as np
import yfinance as yf
from urllib.request import urlopen
from datetime import datetime, timedelta
from pykrx import stock as krx
from bs4 import BeautifulSoup as Soup


class _stock:
    __summary, __p1obj, __p2obj = str(), list(), list()
    __ohlcv, __relative_returns, __multiples, __returns = pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    __foreigner, __consensus =  pd.DataFrame(), pd.DataFrame()
    __short_sell, __short_balance = pd.DataFrame(), pd.DataFrame()
    __multi_factors, __comparable_returns, __comparable_multiples = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    __product, __costs = pd.DataFrame(), pd.DataFrame()

    def __init__(self, ticker:str, period:int=5, meta=None):
        self.__exchange = self.exchange = 'krx' if ticker.isdigit() else 'nyse' if ticker.isalpha() else 'na'
        self.__is_index = True if self.__exchange == 'krx' and len(ticker) == 4 else False
        self.__is_init, self.__is_link = False, False
        self.__tic = datetime.today() - timedelta(period * 365)
        self.__toc = datetime.today()

        self.ticker = ticker
        self.period = period

        if self.__exchange == 'nyse':
            self.name = ticker
        elif self.__exchange == 'krx' and self.__is_index:
            self.name = krx.get_index_ticker_name(ticker=ticker)
        elif self.__exchange == 'krx':
            if not isinstance(meta, pd.DataFrame):
                self.name = krx.get_market_ticker_name(ticker=ticker)
            else:
                self.name = meta.loc[ticker, '종목명'] if ticker in meta.index else krx.get_market_ticker_name(ticker=ticker)
        else:
            raise KeyError(f'Unidentified Argument for ticker = {ticker} given')

    def __init_obj(self):
        if not self.__is_init:
            self.__p1obj = pd.read_html(
                f"http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A{self.ticker}&cID=&MenuYn=Y&ReportGB=D&NewMenuID=Y&stkGb=701",
                encoding='utf-8'
            )
            self.__p2obj = pd.read_html(
                f"http://comp.fnguide.com/SVO2/ASP/SVD_Corp.asp?pGB=1&gicode=A{self.ticker}&cID=&MenuYn=Y&ReportGB=&NewMenuID=102&stkGb=701",
                encoding='utf-8'
            )
            self.__is_link = self.__p1obj[11].iloc[0].isnull().sum() > self.__p1obj[14].iloc[0].isnull().sum()
            self.__is_init = True
        return

    def set_ohlcv(self, ohlcv:pd.DataFrame):
        self.__ohlcv = ohlcv.copy()
        return

    @property
    def summary(self) -> str:
        """
        한국거래소 상장 기업 한정, 기업 개요
        """
        if not self.__summary and self.__exchange == 'krx' and not self.__is_index:
            html = requests.get(
                f"http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A{self.ticker}&cID=&MenuYn=Y&ReportGB=D&NewMenuID=Y&stkGb=701"
            ).content
            texts = Soup(html, 'lxml').find('ul', id='bizSummaryContent').find_all('li')
            text = '\n\n '.join([text.text for text in texts])

            syllables = []
            for n in range(1, len(text) - 2):
                if text[n] == '.':
                    if text[n - 1].isdigit() or text[n + 1].isdigit() or text[n + 1].isalpha():
                        syllables.append('.')
                    else:
                        syllables.append('.\n')
                else:
                    syllables.append(text[n])
            self.__summary = ' ' + text[0] + ''.join(syllables) + text[-2] + text[-1]
        return self.__summary

    @property
    def ohlcv(self) -> pd.DataFrame:
        """
                     시가   고가   저가   종가    거래량
        날짜
        2017-01-11  37520  38560  37420  38280    240363
        2017-01-12  38000  38800  37980  38800    233383
        2017-01-13  38100  38319  37460  37460    319089
        ...           ...    ...    ...    ...       ...
        2022-01-05  78800  79000  76400  77400  25470640
        2022-01-06  76700  77600  76600  76900  12931954
        2022-01-07  78100  78400  77400  78300  15102496
        """
        if self.__ohlcv.empty:
            if self.__exchange == 'nyse':
                self.__ohlcv = yf.Ticker(self.ticker).history(period=f'{self.period}y')
            elif self.__exchange == 'krx' and self.__is_index:
                self.__ohlcv = krx.get_index_ohlcv_by_date(
                    fromdate=self.__tic.strftime("%Y%m%d"),
                    todate=self.__toc.strftime("%Y%m%d"),
                    ticker=self.ticker, name_display=False
                )
            else:
                self.__ohlcv = krx.get_market_ohlcv_by_date(
                    fromdate=self.__tic.strftime("%Y%m%d"),
                    todate=self.__toc.strftime("%Y%m%d"),
                    ticker=self.ticker
                )
        return self.__ohlcv

    @property
    def relative_returns(self) -> pd.DataFrame:
        """
                           3M        6M        1Y
        날짜
        2021-01-11        NaN       NaN  0.000000
        2021-01-12        NaN       NaN -3.007519
        2021-01-13        NaN       NaN  0.000000
        ...               ...       ...       ...
        2022-01-06  36.612022  4.166667 -6.015038
        2022-01-07  38.797814  5.833333 -4.511278
        2022-01-10  34.426230  2.500000 -7.518797
        """
        if self.__relative_returns.empty:
            objs = dict()
            close = self.ohlcv['종가' if self.__exchange == 'krx' else 'close'].copy()
            for label, dt in [('3M', 92), ('6M', 183), ('1Y', 365)]:
                objs[label] = 100 * (
                    close[close.index >= close.index[-1] - timedelta(dt)].pct_change().fillna(0) + 1
                ).cumprod() - 100
            self.__relative_returns = pd.concat(objs=objs, axis=1)
        return self.__relative_returns

    @property
    def annual_statement(self) -> pd.DataFrame:
        """
        연간 기본 실적
                        매출액 영업이익  영업이익(발표기준)  당기순이익  ...    PER   PBR  발행주식수  배당수익률
        2016/12     2018667.0  292407.0            292407.0    227261.0  ...  13.18  1.48  7033967.0         1.58
        2017/12     2395754.0  536450.0            536450.0    421867.0  ...   9.40  1.76  6454925.0         1.67
        2018/12     2437714.0  588867.0            588867.0    443449.0  ...   6.42  1.10  5969783.0         3.66
        2019/12     2304009.0  277685.0            277685.0    217389.0  ...  17.63  1.49  5969783.0         2.54
        2020/12     2368070.0  359939.0            359939.0    264078.0  ...  21.09  2.06  5969783.0         3.70
        2021/12(P)  2790400.0  515700.0            515700.0         NaN  ...    NaN   NaN        NaN          NaN
        2022/12(E)  3017532.0  558278.0                 NaN    428421.0  ...  12.61  1.65        NaN          NaN
        2023/12(E)  3278481.0  662686.0                 NaN    511360.0  ...  10.56  1.49        NaN          NaN
        """
        self.__init_obj()
        df_copy = (self.__p1obj[14] if self.__is_link else self.__p1obj[11]).copy()
        cols = df_copy.columns.tolist()
        df_copy.set_index(keys=[cols[0]], inplace=True)
        df_copy.index.name = None
        df_copy.columns = df_copy.columns.droplevel()
        df_copy = df_copy.T
        return df_copy

    @property
    def quarter_statement(self) -> pd.DataFrame:
        """
        분기 기본 실적
                       매출액  영업이익  영업이익(발표기준)  당기순이익  ...  PER   PBR  발행주식수  배당수익률
        2020/09      81288.0    13019.0             13019.0     10845.0  ...  NaN  1.15   728002.0          NaN
        2020/12      79662.0     9589.0              9589.0     17704.0  ...  NaN  1.59   728002.0         0.99
        2021/03      84942.0    13244.0             13244.0      9926.0  ...  NaN  1.76   728002.0          NaN
        2021/06     103217.0    26946.0             26946.0     19884.0  ...  NaN  1.62   728002.0          NaN
        2021/09     118053.0    41718.0             41718.0     33153.0  ...  NaN  1.23   728002.0          NaN
        2021/12(E)  123607.0    41844.0                 NaN     33903.0  ...  NaN   NaN        NaN          NaN
        2022/03(E)  112451.0    30024.0                 NaN     21875.0  ...  NaN   NaN        NaN          NaN
        2022/06(E)  115935.0    28307.0                 NaN     17382.0  ...  NaN   NaN        NaN          NaN
        """
        self.__init_obj()
        df_copy = (self.__p1obj[15] if self.__is_link else self.__p1obj[12]).copy()
        cols = df_copy.columns.tolist()
        df_copy.set_index(keys=[cols[0]], inplace=True)
        df_copy.index.name = None
        df_copy.columns = df_copy.columns.droplevel()
        df_copy = df_copy.T
        return df_copy

    @property
    def returns(self) -> pd.DataFrame:
        """
                 R1D   R1M    R3M   R6M    R1Y
        000660 -3.15  -0.4  34.43  -0.4  -5.75
        """
        if self.__returns.empty:
            key = '종가' if self.__exchange == 'krx' else 'close'
            data = [round(100 * self.ohlcv[key].pct_change(periods=dt)[-1], 2) for dt in [1, 5, 21, 63, 126, 252]]
            self.__returns = pd.DataFrame(data=data, columns=[self.ticker], index=['R1D', 'R1W', 'R1M', 'R3M', 'R6M', 'R1Y']).T
        return self.__returns

    @property
    def multiples(self) -> pd.DataFrame:
        """
                      BPS    PER   PBR   EPS   DIV   DPS   PSR
        날짜
        2021-01-11  37528  28.74  2.42  3166  1.56  1416  2.11
        2021-01-12  37528  28.62  2.41  3166  1.56  1416  2.10
        2021-01-13  37528  28.33  2.39  3166  1.58  1416  2.08
        ...           ...    ...   ...   ...   ...   ...   ...
        2022-01-06  39406  20.02  1.95  3841  3.89  2994  1.74
        2022-01-07  39406  20.39  1.99  3841  3.82  2994  1.77
        2022-01-10  39406  20.31  1.98  3841  3.84  2994  1.76
        """
        if self.__multiples.empty and self.__exchange == 'krx' and not self.__is_index:
            key = self.quarter_statement.columns[0]
            s = self.quarter_statement[key]
            s = s[~s.index.str.endswith(')')]
            s.index = s.index + '/30'
            s.index = pd.to_datetime(s.index)
            sales = pd.Series(
                data=[s[:n + 1].sum() * (4 / (n + 1)) if n < 3 else s[n - 3:n + 1].sum() for n in range(len(s))],
                index=s.index
            )

            fromdate, todate = (self.__toc - timedelta(365)).strftime("%Y%m%d"), self.__toc.strftime("%Y%m%d")
            cap = krx.get_market_cap_by_date(fromdate=fromdate, todate=todate, ticker=self.ticker)
            cap['시가총액'] = cap['시가총액'] / 100000000

            objs = []
            for n, (date, sale) in enumerate(zip(sales.index, sales.values)):
                cond = (cap.index >= date) & (cap.index < sales.index[n + 1]) if n < len(sales) - 1 else cap.index >= date
                cut = cap[cond].copy()
                cut[key] = int(sale)
                objs.append(cut)
            recap = pd.concat(objs=objs, axis=0)

            psr = round(recap['시가총액'] / recap[key], 2)
            psr.name = 'PSR'
            self.__multiples = krx.get_market_fundamental_by_date(
                fromdate=fromdate, todate=todate, ticker=self.ticker
            ).join(psr, how='left')
        return self.__multiples

    @property
    def foreigner(self) -> pd.DataFrame:
        """
        한국거래소 상장 기업 한정, 외국인 소진율
                               (Daily) 3M             (Weekly) 1Y            (Monthly) 3Y
                      종가 외국인보유비중     종가 외국인보유비중     종가 외국인보유비중
        날짜
        2019-01-01    NaN            NaN      NaN             NaN    42369          56.04
        2019-02-01    NaN            NaN      NaN             NaN    46309          56.72
        2019-03-01    NaN            NaN      NaN             NaN    44560          56.75
        ...           ...            ...      ...             ...      ...            ...
        2022-01-05  77400          51.99      NaN             NaN      NaN            NaN
        2022-01-06  76900          52.03      NaN             NaN      NaN            NaN
        2022-01-07  78300          52.11    77980           52.02      NaN            NaN
        """
        if self.__foreigner.empty and self.__exchange == 'krx' and not self.__is_index:
            objs = dict()
            for dt in ['3M', '1Y', '3Y']:
                url = f"http://cdn.fnguide.com/SVO2/json/chart/01_01/chart_A{self.ticker}_{dt}.json"
                data = json.loads(urlopen(url).read().decode('utf-8-sig', 'replace'))
                frame = pd.DataFrame(data["CHART"])[['TRD_DT', 'J_PRC', 'FRG_RT']].rename(columns={
                    'TRD_DT': '날짜', 'J_PRC': '종가', 'FRG_RT': '외국인보유비중'
                }).set_index(keys='날짜')
                frame.index = pd.to_datetime(frame.index)
                objs[dt] = frame
            self.__foreigner = pd.concat(objs=objs, axis=1)
        return self.__foreigner

    @property
    def consensus(self) -> pd.DataFrame:
        """
                    투자의견  목표주가    종가
        날짜
        2021-01-11      4.00    145520  133000
        2021-01-12      4.00    149720  129000
        2021-01-13      4.00    149720  133000
        ...              ...       ...     ...
        2022-01-05      3.91    145739  125500
        2022-01-06      3.91    145739  125000
        2022-01-07      3.91    147478  127000
        """
        if self.__consensus.empty and self.__exchange == 'krx' and not self.__is_index:
            url = f"http://cdn.fnguide.com/SVO2/json/chart/01_02/chart_A{self.ticker}.json"
            data = json.loads(urlopen(url).read().decode('utf-8-sig', 'replace'))
            self.__consensus = pd.DataFrame(data['CHART']).rename(columns={
                'TRD_DT': '날짜', 'VAL1': '투자의견', 'VAL2': '목표주가', 'VAL3': '종가'
            }).set_index(keys='날짜')
            self.__consensus.index = pd.to_datetime(self.__consensus.index)
            self.__consensus['목표주가'] = self.__consensus['목표주가'].apply(lambda x: x if x else np.nan)
        return self.__consensus

    @property
    def short_sell(self) -> pd.DataFrame:
        """
                   차입공매도비중  수정 종가
        날짜
        2021-01-11              0    133000
        2021-01-18              0    130000
        2021-01-25           0.03    135000
               ...            ...       ...
        2021-12-20           2.58    120500
        2021-12-27           1.18    126000
        2022-01-03           0.98    128500
        """
        if self.__short_sell.empty and self.__exchange == 'krx' and not self.__is_index:
            url = f"http://cdn.fnguide.com/SVO2/json/chart/11_01/chart_A{self.ticker}_SELL1Y.json"
            data = json.loads(urlopen(url).read().decode('utf-8-sig', 'replace'))
            self.__short_sell = pd.DataFrame(data['CHART']).rename(columns={
                'TRD_DT': '날짜', 'VAL': '차입공매도비중', 'ADJ_PRC': '수정 종가'
            }).set_index(keys='날짜')
            self.__short_sell.index = pd.to_datetime(self.__short_sell.index)
        return self.__short_sell

    @property
    def short_balance(self) -> pd.DataFrame:
        """
                    대차잔고비중   수정 종가
        날짜
        2021-01-11          1.95      133000
        2021-01-18          2.07      130000
        2021-01-25          2.11      135000
               ...           ...         ...
        2021-12-20          2.71      120500
        2021-12-27          2.68      126000
        2022-01-03          2.36      128500
        """
        if self.__short_balance.empty and self.__exchange == 'krx' and not self.__is_index:
            url = f"http://cdn.fnguide.com/SVO2/json/chart/11_01/chart_A{self.ticker}_BALANCE1Y.json"
            data = json.loads(urlopen(url).read().decode('utf-8-sig', 'replace'))
            self.__short_balance = pd.DataFrame(data['CHART'])[['TRD_DT', 'BALANCE_RT', 'ADJ_PRC']].rename(columns={
                'TRD_DT': '날짜', 'BALANCE_RT': '대차잔고비중', 'ADJ_PRC': '수정 종가'
            }).set_index(keys='날짜')
            self.__short_balance.index = pd.to_datetime(self.__short_balance.index)
        return self.__short_balance

    @property
    def multi_factor(self) -> pd.DataFrame:
        """
                     SK하이닉스 반도체(업종)
        팩터
        베타               0.80         0.31
        배당성            -0.08        -1.03
        수익건전성         1.09        -0.12
        성장성             0.28        -0.05
        기업투자          -0.67        -0.14
        거시경제 민감도   -0.18        -0.32
        모멘텀            -0.34         0.20
        단기 Return        0.35         0.50
        기업규모           0.84        -2.36
        거래도            -0.14         0.68
        밸류               0.16        -0.36
        변동성            -0.24         0.64
        """
        if self.__multi_factors.empty and self.__exchange == 'krx' and not self.__is_index:
            url = f"http://cdn.fnguide.com/SVO2/json/chart/05_05/A{self.ticker}.json"
            data = json.loads(urlopen(url).read().decode('utf-8-sig', 'replace'))
            header = pd.DataFrame(data['CHART_H'])['NAME'].tolist()
            self.__multi_factors = pd.DataFrame(data['CHART_D']).rename(
                columns=dict(zip(['NM', 'VAL1', 'VAL2'], ['팩터'] + header))
            ).set_index(keys='팩터')
        return self.__multi_factors

    @property
    def comparable_returns(self) -> pd.DataFrame:
        """
                                              (Daily) 3M                          (Weekly) 1Y
                    SK하이닉스  코스피 전기,전자   KOSPI  SK하이닉스  코스피 전기,전자  KOSPI
        TRD_DT
        2021-01-15         NaN              NaN      NaN      100.00           100.00  100.00
        2021-01-22         NaN              NaN      NaN       99.69            98.44   99.13
        2021-01-29         NaN              NaN      NaN       97.70            97.66   99.10
        ...                ...              ...      ...         ...              ...     ...
        2022-01-05      137.16           113.68   101.29         NaN              NaN     NaN
        2022-01-06      136.61           112.58   100.14         NaN              NaN     NaN
        2022-01-07      138.80           114.45   101.32       97.17            90.77   94.56
        """
        if self.__comparable_returns.empty and self.__exchange == 'krx' and not self.__is_index:
            objs = {}
            for period in ['3M', '1Y']:
                url = f"http://cdn.fnguide.com/SVO2/json/chart/01_01/chart_A{self.ticker}_{period}.json"
                data = json.loads(urlopen(url).read().decode('utf-8-sig', 'replace'))
                header = pd.DataFrame(data["CHART_H"])[['ID', 'PREF_NAME']]
                header = header[header['PREF_NAME'] != ""]
                inner = pd.DataFrame(data["CHART"])[
                    ['TRD_DT'] + header['ID'].tolist()
                ].set_index(keys='TRD_DT').rename(columns=header.set_index(keys='ID').to_dict()['PREF_NAME'])
                inner.index = pd.to_datetime(inner.index)
                objs[period] = inner
            self.__comparable_returns = pd.concat(objs=objs, axis=1)
        return self.__comparable_returns

    @property
    def comparable_multiples(self) -> pd.DataFrame:
        """
                                               PER                               EV/EBITA                                    ROE
              SK하이닉스  코스피 전기,전자  코스피   SK하이닉스  코스피 전기,전자  코스피   SK하이닉스  코스피 전기,전자  코스피
        2019       34.15            21.90    20.01         6.76              6.85    7.21         4.23              6.11    4.69
        2020       18.14            19.87    22.35         6.37              8.06    8.57         9.53              9.26    5.26
        2021E       9.72            13.28    11.10         4.27              4.65    6.44        16.86             14.15   11.62
        """
        if self.__comparable_multiples.empty and self.__exchange == 'krx' and not self.__is_index:
            url = f"http://cdn.fnguide.com/SVO2/json/chart/01_04/chart_A{self.ticker}_D.json"
            data = json.loads(urlopen(url).read().decode('utf-8-sig', 'replace'))
            objs = {}
            for label, index in (('PER', '02'), ('EV/EBITA', '03'), ('ROE', '04')):
                header1 = pd.DataFrame(data[f'{index}_H'])[['ID', 'NAME']].set_index(keys='ID')
                header1['NAME'] = header1['NAME'].astype(str).str.replace("'", "20")
                header1 = header1.to_dict()['NAME']
                header1.update({'CD_NM': '이름'})

                inner1 = pd.DataFrame(data[index])[list(header1.keys())].rename(columns=header1).set_index(keys='이름')
                inner1.index.name = None
                for col in inner1.columns:
                    inner1[col] = inner1[col].apply(lambda x: np.nan if x == '-' else x)
                objs[label] = inner1.T
            self.__comparable_multiples = pd.concat(objs=objs, axis=1)
        return self.__comparable_multiples

    @property
    def product(self) -> pd.DataFrame:
        """
                    IM  반도체     CE     DP  기타(계)
        기말
        2017/12  44.42   30.92  18.79  14.35     -8.48
        2018/12  41.30   35.40  17.30  13.30     -7.30
        2019/12  46.56   28.19  19.43  13.48     -7.65
        2020/12  42.05   30.77  20.34  12.92     -6.08
        """
        if self.__product.empty and self.__exchange == 'krx' and not self.__is_index:
            url = f"http://cdn.fnguide.com/SVO2//json/chart/02/chart_A{self.ticker}_01_N.json"
            src = json.loads(urlopen(url).read().decode('utf-8-sig', 'replace'))
            header = pd.DataFrame(src['chart_H'])[['ID', 'NAME']].set_index(keys='ID')
            header = header.to_dict()['NAME']
            header.update({'PRODUCT_DATE':'기말'})
            self.__product = pd.DataFrame(src['chart']).rename(columns=header).set_index(keys='기말')
        return self.__product

    @property
    def product_pie(self) -> pd.DataFrame:
        """
        IM        42.05
        반도체    30.77
        CE        20.34
        DP         6.84
        """
        df = self.product.iloc[-1].T.dropna().astype(float)
        df.drop(index=df[df < 0].index, inplace=True)
        df[df.index[-1]] += (100 - df.sum())
        df.name = '비중'
        return df

    @property
    def costs(self) -> pd.DataFrame:
        """
                판관비율  매출원가율  R&D투자비중  무형자산처리비중  당기비용처리비중
        2016/12      NaN         NaN         7.33             0.34               6.99
        2017/12    23.64       53.97         7.01             0.19               6.83
        2018/12    21.53       54.31         7.65             0.12               7.53
        2019/12    24.04       63.91         8.77             0.12               8.65
        2020/12    23.79       61.02         8.96             0.05               8.92
        """
        self.__init_obj()
        if self.__costs.empty and self.__exchange == 'krx' and not self.__is_index:
            sales_cost = self.__p2obj[4].set_index(keys=['항목'])
            sales_cost.index.name = None

            sg_n_a = self.__p2obj[5].set_index(keys=['항목'])
            sg_n_a.index.name = None

            r_n_d = self.__p2obj[8].set_index(keys=['회계연도'])
            r_n_d.index.name = None
            r_n_d = r_n_d[
                ['R&D 투자 총액 / 매출액 비중.1', '무형자산 처리 / 매출액 비중.1', '당기비용 처리 / 매출액 비중.1']
            ].rename(columns={
                'R&D 투자 총액 / 매출액 비중.1': 'R&D투자비중',
                '무형자산 처리 / 매출액 비중.1': '무형자산처리비중',
                '당기비용 처리 / 매출액 비중.1': '당기비용처리비중'
            })
            if '관련 데이터가 없습니다.' in r_n_d.index:
                r_n_d.drop(index=['관련 데이터가 없습니다.'], inplace=True)
            self.__costs = pd.concat(objs=[sales_cost.T, sg_n_a.T, r_n_d], axis=1)
        return self.__costs.sort_index(ascending=True)

if __name__ == "__main__":
    stock = _stock(ticker='005930')
    print(stock.product_pie)
