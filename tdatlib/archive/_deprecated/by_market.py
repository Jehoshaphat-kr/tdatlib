import pandas as pd
import urllib.request as req
import json, requests, time, os
# from by_stock import stock
from tdatlib import archive
from tqdm import tqdm
from pykrx import stock as krx
from pytz import timezone
from datetime import datetime, timedelta


kst = datetime.now(timezone('Asia/Seoul'))
class corporate:
    __icm, __ohlcv, __theme = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    __wics, __wi26, __wise_date = pd.DataFrame(), pd.DataFrame(), str()
    __today = kst.strftime("%Y%m%d")

    def __set_wise_date(self):
        """
        WISE 산업분류 기준 날짜
        """
        if not self.__wise_date:
            source = requests.get(url='http://www.wiseindex.com/Index/Index#/G1010.0.Components').text
            tic = source.find("기준일")
            toc = source[tic:].find("</p>")
            # self.__wise_date = datetime.strptime(source[tic + 6: tic + toc], "%Y.%m.%d").strftime("%Y%m%d")
            self.__wise_date = source[tic + 6: tic + toc].replace('.', '')
        return

    def __fetch_wise(self, codes:dict, name:str) -> pd.DataFrame:
        """
        WISE INDEX 산업/업종 구분 데이터 Fetch
        :param codes: 산업/업종명 by 구분코드
        :param name: WICS 또는 WI26
        :return: 
        """
        frame = pd.DataFrame()
        for code, name in tqdm(codes.items(), desc=f'Fetch {name}'):
            is_done = False
            while not is_done:
                try:
                    _read = requests.get(
                        f'http://www.wiseindex.com/Index/GetIndexComponets?ceil_yn=0&dt={self.__wise_date}&sec_cd={code}'
                    ).json()
                    read = pd.DataFrame(
                        data=[[_['CMP_CD'], _['CMP_KOR'], _['SEC_NM_KOR'], _['IDX_NM_KOR'][5:]] for _ in _read['list']],
                        columns=['종목코드', '종목명', '산업', '섹터']
                    )
                except ConnectionError as e:
                    print(f'\t- Parse error while fetching WISE INDEX {code} {name}')
                    time.sleep(1)
                    continue

                frame = pd.concat(objs=[frame, read], axis=0, ignore_index=True)
                is_done = True
        return frame.copy()

    def __init_perform(self):
        """
        기준일자 기간별 수익률 파일 초기화
        :return: 
        """
        file = os.path.join(archive.root, f'market/performance/{self.__today}perf.csv')
        if not os.path.isfile(file):
            t_label = ['R1W', 'R1M', 'R3M', 'R6M', 'R1Y']
            t_stamp = [(kst - timedelta(days)).strftime("%Y%m%d") for days in [7, 30, 91, 183, 365]]
            shares = pd.concat(objs={
                f'PREV': krx.get_market_cap_by_ticker(date=t_stamp[-1], market='ALL', prev=True)['상장주식수'],
                f'CURR': krx.get_market_cap_by_ticker(date=self.__today, market='ALL', prev=True)['상장주식수']
            }, axis=1)

            objs = {'R1D': round(krx.get_market_ohlcv(self.__today, market='ALL', prev=True)['등락률'], 2)}
            for label, t in zip(t_label, t_stamp):
                objs[label] = krx.get_market_price_change(t, self.__today, market='ALL')['등락률']
            perf = pd.concat(objs=objs, axis=1, ignore_index=False)
            perf = perf[perf.index.isin(shares[shares.PREV == shares.CURR].index)]
            perf.index.name = '종목코드'
            perf.to_csv(file, encoding='utf-8', index=True)
        return

    def get_performance(self, tickers:list=None) -> pd.DataFrame:
        """
        기간별 수익률
        :param tickers: 대상 종목 리스트
                 R1D   R1W    R1M    R3M    R6M     R1Y
        종목코드
        095570  0.35  0.18   9.88   6.18  -4.22   42.82
        006840  3.39  1.91   8.10   2.64 -21.22  -25.48
        054620  1.26 -0.82   7.11  -8.02 -33.97   59.39
        ...      ...   ...    ...    ...    ...     ...
        000545 -0.37 -1.72  -2.20  -3.50 -16.67   20.12
        037440  0.44  0.11 -10.20  18.35  43.35  113.52
        238490  0.00 -3.17  -2.07  -0.84  -6.24  -27.43
        """
        self.__init_perform()

        file = os.path.join(archive.root, f'market/performance/{self.__today}perf.csv')
        perf = pd.read_csv(file, encoding='utf-8', index_col='종목코드')
        perf.index = perf.index.astype(str).str.zfill(6)
        if not isinstance(tickers, list):
            return perf

        add = [ticker for ticker in tickers if not ticker in perf.index]
        if not add:
            return perf

        process = tqdm(add)
        for n, ticker in enumerate(process):
            process.set_description(f'Fetch Returns - {ticker}')
            while True:
                # noinspection PyBroadException
                try:
                    perf = pd.concat(
                        objs=[perf, stock(ticker=ticker, period=2, meta=self.icm).returns],
                        axis=0, ignore_index=False
                    )
                    break
                except Exception as e:
                    time.sleep(1)

        perf.index.name = '종목코드'
        perf.to_csv(file, encoding='utf-8', index=True)
        return perf

    @property
    def icm(self) -> pd.DataFrame:
        """
        IPO, Market Cap and Multiples: 상장일, 시가총액 및 투자배수(기초) 정보

                 종목명         IPO   종가       시가총액   거래량    거래대금  상장주식수      BPS    PER   PBR      EPS   DIV     DPS
        종목코드
        000210       DL  1976-02-02  57100  1196580976400    56637  3230631400    20955884  67178.0   4.37  0.85  13077.0  2.28  1300.0
        004840  DRB동일  1976-05-21   4970    99052100000     4725    23512045    19930000  17702.0  41.06  0.28    121.0  1.01    50.0
        155660      DSR  2013-05-15   5560    88960000000   154220   874995590    16000000  10087.0   9.96  0.55    558.0  0.90    50.0
        ...         ...         ...    ...            ...      ...         ...         ...      ...    ...   ...      ...   ...     ...
        000547      NaN         NaN  27800     4270080000      231     6440750      153600      0.0   0.00  0.00      0.0  0.00     0.0
        009275      NaN         NaN  36500     3312010000      215     7855350       90740      0.0   0.00  0.00      0.0  0.00     0.0
        001529      NaN         NaN  34650     3108867300    12358   437491300       89722      0.0   0.00  0.00      0.0  0.43   150.0
        """
        if self.__icm.empty:
            self.__icm = pd.read_csv(archive.icm, index_col='종목코드', encoding='utf-8')
            self.__icm.index = self.__icm.index.astype(str).str.zfill(6)
            cond1 = not str(self.__icm['날짜'][0]) == self.__today
            cond2 = str(self.__icm['날짜'][0]) == self.__today and int(kst.now().strftime("%H%M")) <= 1530
            if cond1 or cond2:
                process, objs = tqdm(['IPO-DATE', 'MARKET-CAP', 'FUNDAMENTAL']), list()
                for text in process:
                    process.set_description(desc=f'Fetch {text} ...')
                    if text == 'IPO-DATE':
                        link = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'
                        ipo = pd.read_html(io=link, header=0)[0][['회사명', '종목코드', '상장일']]
                        ipo = ipo.rename(columns={'회사명': '종목명', '상장일': 'IPO'}).set_index(keys='종목코드')
                        ipo.index = ipo.index.astype(str).str.zfill(6)
                        ipo.IPO = pd.to_datetime(ipo.IPO)
                        objs.append(ipo)
                    if text == 'MARKET-CAP':
                        objs.append(krx.get_market_cap_by_ticker(date=self.__today, market="ALL", prev=True))
                    if text == 'FUNDAMENTAL':
                        objs.append(krx.get_market_fundamental(date=self.__today, market='ALL', prev=True))
                self.__icm = pd.concat(objs=objs, axis=1)
                self.__icm['날짜'] = self.__today
                self.__icm.index.name = '종목코드'
                self.__icm.to_csv(archive.icm, index=True, encoding='utf-8')
        return self.__icm.drop(columns=['날짜'])

    @property
    def wics(self) -> pd.DataFrame:
        """
                          종목명      산업      섹터
        종목코드
        096770      SK이노베이션    에너지    에너지
        010950             S-Oil    에너지    에너지
        267250    현대중공업지주    에너지    에너지
        ...                  ...       ...       ...
        003480  한진중공업홀딩스  유틸리티  유틸리티
        053050          지에스이  유틸리티  유틸리티
        034590      인천도시가스  유틸리티  유틸리티
        """
        if self.__wics.empty:
            self.__set_wise_date()
            self.__wics = pd.read_csv(archive.wics, index_col='종목코드', encoding='utf-8')
            self.__wics.index = self.__wics.index.astype(str).str.zfill(6)
            if not str(self.__wics['날짜'][0]) == self.__wise_date:
                self.__wics = self.__fetch_wise(codes=archive.wics_code, name='WICS')
                self.__wics['날짜'] = self.__wise_date
                self.__wics.to_csv(archive.wics, index=False, encoding='utf-8')
                self.__wics.set_index(keys='종목코드', inplace=True)
        return self.__wics.drop(columns=['날짜'])

    @property
    def wi26(self) -> pd.DataFrame:
        """
                           종목명     섹터
        종목코드
        096770       SK이노베이션   에너지
        010950              S-Oil   에너지
        267250     현대중공업지주   에너지
        ...                  ...       ...
        003480  한진중공업홀딩스  유틸리티
        053050          지에스이  유틸리티
        034590      인천도시가스  유틸리티
        """
        if self.__wi26.empty:
            self.__set_wise_date()
            self.__wi26 = pd.read_csv(archive.wi26, index_col='종목코드', encoding='utf-8')
            self.__wi26.index = self.__wi26.index.astype(str).str.zfill(6)
            if not str(self.__wi26['날짜'][0]) == self.__wise_date:
                self.__wi26 = self.__fetch_wise(codes=archive.wi26_code, name='WI26')
                self.__wi26['날짜'] = self.__wise_date
                self.__wi26.drop(columns=['산업'], inplace=True)
                self.__wi26.to_csv(archive.wi26, index=False, encoding='utf-8')
                self.__wi26.set_index(keys='종목코드', inplace=True)
        return self.__wi26.drop(columns=['날짜'])

    @property
    def theme(self) -> pd.DataFrame:
        """
                     종목명          섹터
        종목코드
        211270       AP위성      우주항공
        138930  BNK금융지주          배당
        079160       CJ CGV  미디어컨텐츠
        ...             ...           ...
        298000     효성화학        수소차
        093370         후성       2차전지
        145020         휴젤        바이오
        """
        if self.__theme.empty:
            self.__theme = pd.read_csv(archive.theme, index_col='종목코드')
            self.__theme.index = self.__theme.index.astype(str).str.zfill(6)
        return self.__theme


class index:
    __ks, __kq, __krx = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    __depo, __theme, __display = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    @staticmethod
    def __update(market) -> pd.DataFrame:
        tickers = krx.get_index_ticker_list(market='테마' if market == 'THEME' else market)
        return pd.DataFrame(data={
            '종목코드': tickers,
            '종목명': [krx.get_index_ticker_name(ticker) for ticker in tickers],
            '지수분류': [market] * len(tickers)
        }).set_index(keys='종목코드')

    @property
    def deposit(self) -> pd.DataFrame:
        """
        주요 지수: 코스피200, 코스닥150, 코스피 중형주, 코스피 소형주, 코스닥 중형주 종목
        """
        def update(date:str):
            indices, objs = ['1028', '1003', '1004', '2203', '2003'], list()
            for index in indices:
                tickers = krx.get_index_portfolio_deposit_file(ticker=index)
                df = pd.DataFrame(index=tickers)
                df['지수코드'] = index
                df['지수명'] = krx.get_index_ticker_name(index)
                df['날짜'] = date
                objs.append(df)
            return pd.concat(objs=objs, axis=0)

        if self.__depo.empty:
            self.__depo = pd.read_csv(archive.deposit, index_col='종목코드')
            self.__depo.index = self.__depo.index.astype(str).str.zfill(6)

            today = kst.today().weekday()
            d_date = kst.today() + (timedelta((3 - today) - 7) if today < 3 else -timedelta(today - 3))

            latest_date = str(self.__depo['날짜'].values[0])
            if not latest_date == d_date.strftime("%Y%m%d"):
                self.__depo = update(d_date.strftime("%Y%m%d"))
                self.__depo.index.name = '종목코드'
                self.__depo.to_csv(archive.deposit)
        return self.__depo

    @property
    def kospi(self) -> pd.DataFrame:
        """
                                  종목명   지수분류
        종목코드
        1001                      코스피      KOSPI
        1002               코스피 대형주      KOSPI
        1003               코스피 중형주      KOSPI
        1004               코스피 소형주      KOSPI
         ...                        ...
        1232     코스피 200 비중상한 20%      KOSPI
        1244    코스피200제외 코스피지수      KOSPI
        1894          코스피 200 TOP 10       KOSPI
        """
        if self.__ks.empty:
            self.__ks = self.__update(market='KOSPI')
        return self.__ks

    @property
    def kosdaq(self) -> pd.DataFrame:
        """
                                     종목명    지수분류
        종목코드
        2001                         코스닥      KOSDAQ
        2002                  코스닥 대형주      KOSDAQ
        2003                  코스닥 중형주      KOSDAQ
        2004                  코스닥 소형주      KOSDAQ
         ...                           ...          ...
        2216            코스닥 150 정보기술      KOSDAQ
        2217            코스닥 150 헬스케어      KOSDAQ
        2218  코스닥 150 커뮤니케이션서비스      KOSDAQ
        """
        if self.__kq.empty:
            self.__kq = self.__update(market='KOSDAQ')
        return self.__kq

    @property
    def krx(self) -> pd.DataFrame:
        """
                              종목명 지수분류
        종목코드
        5042                 KRX 100      KRX
        5043              KRX 자동차      KRX
        5044              KRX 반도체      KRX
         ...                    ...       ...
        5357            KRX 300 소재      KRX
        5358      KRX 300 필수소비재      KRX
        5600                 KTOP 30      KRX
        """
        if self.__krx.empty:
            self.__krx = self.__update(market='KRX')
        return self.__krx

    @property
    def theme(self) -> pd.DataFrame:
        """
                                          종목명   지수분류
        종목코드
        1163                   코스피 고배당 50       THEME
        1164                 코스피 배당성장 50       THEME
        1165                  코스피 우선주 지수      THEME
         ...                                ...         ...
        5421                  KRX 전기차 Top 15       THEME
        5422                  KRX 반도체 Top 15       THEME
        G004      KRX/S&P 탄소효율 그린뉴딜지수       THEME
        """
        if self.__theme.empty:
            self.__theme = self.__update(market='THEME')
        return self.__theme

    @property
    def display(self) -> pd.DataFrame:
        """
           KOSPI코드        KOSPI지수  KOSDAQ코드                      KOSDAQ지수  KRX코드     KRX지수 THEME코드           THEME지수
        0       1001           코스피        2001                          코스닥     5042     KRX 100      1163    코스피 고배당 50
        1       1002    코스피 대형주        2002                   코스닥 대형주     5043  KRX 자동차      1164  코스피 배당성장 50
        2       1003    코스피 중형주        2003                   코스닥 중형주     5044  KRX 반도체      1165   코스피 우선주 지수
        ..       ...              ...         ...                            ...       ...         ...       ...                  ...
        47         -                -        2216            코스닥 150 정보기술         -           -         -                    -
        48         -                -        2217            코스닥 150 헬스케어         -           -         -                    -
        49         -                -        2218  코스닥 150 커뮤니케이션서비스         -           -         -                    -
        """
        if self.__display.empty:
            objs = []
            for market, data in [('KOSPI', self.kospi), ('KOSDAQ', self.kosdaq), ('KRX', self.krx), ('THEME', self.theme)]:
                obj = data.rename(columns={'종목명': f'{market}지수'}).drop(columns=['지수분류'])
                obj.index.name = f'{market}코드'
                objs.append(obj.reset_index(level=0))
            self.__display = pd.concat(objs=objs, axis=1).fillna('-')
        return self.__display


class etf:
    __list, __meta, __group = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    @property
    def group(self) -> pd.DataFrame:
        """
                                          종목명          산업   섹터
        종목코드
        069500                         KODEX 200  국내 시장지수  대형
        278540               KODEX MSCI Korea TR  국내 시장지수  대형
        278530                       KODEX 200TR  국내 시장지수  대형
        ...                                  ...            ...   ...
        396520         TIGER 차이나반도체FACTSET           해외  중국
        391600    KINDEX 미국친환경그린테마INDXX           해외  미국
        391590         KINDEX 미국스팩&IPO INDXX           해외  미국
        """
        if self.__group.empty:
            self.__group = pd.read_csv(archive.etf, index_col='종목코드')
            self.__group.index = self.__group.index.astype(str).str.zfill(6)
        return self.__group

    @property
    def list(self) -> pd.DataFrame:
        """
                                     종목명   종가        시가총액
        종목코드
        069500                    KODEX 200  39725  5718400000000
        371460  TIGER 차이나전기차SOLACTIVE  16435  3229800000000
        278540          KODEX MSCI Korea TR  12820  2239700000000
        ...                             ...    ...            ...
        334700   KBSTAR 팔라듐선물인버스(H)   5520     1700000000
        287310         KBSTAR 200경기소비재  10895     1500000000
        287320             KBSTAR 200산업재  11135     1300000000
        """
        if self.__list.empty:
            url = 'https://finance.naver.com/api/sise/etfItemList.nhn'
            _ = pd.DataFrame(json.loads(req.urlopen(url).read().decode('cp949'))['result']['etfItemList'])
            self.__list = _[['itemcode', 'itemname', 'nowVal', 'marketSum']].rename(
                columns=dict(zip(
                    ['itemcode', 'itemname', 'nowVal', 'marketSum'], ['종목코드', '종목명', '종가', '시가총액']
                ))
            )
            self.__list['시가총액'] = self.__list['시가총액'] * 100000000
            self.__list.set_index(keys='종목코드', inplace=True)
        return self.__list

    def deposit(self, ticker:str, date_or_period=None) -> pd.DataFrame:
        """
        :param ticker: ETF 종목코드
        :param date_or_period: 기준 날짜 또는 기간(일자)
                 계약수      금액       비중        종목명
        티커
        051910   616.0  442904000  20.309999        LG화학
        096770  1661.0  410267000  18.980000  SK이노베이션
        006400   486.0  309096000  14.080000       삼성SDI
           ...     ...        ...        ...           ...
        101360    88.0    2613600   0.120000      이엔드디
        290670    47.0    2444000   0.110000  대보마그네틱
        277880   146.0    1963700   0.090000    티에스아이

        또는

                       051910     096770  006400  ...  101360  290670  277880
        2021-12-13  20.049999  15.860000   15.07  ...    0.11    0.08    0.07
        2021-12-14  19.490000  15.860000   14.92  ...    0.11    0.08    0.07
        2021-12-15  19.440001  15.810000   14.85  ...    0.11    0.08    0.07
        ...               ...        ...     ...  ...     ...     ...     ...
        2022-01-06  19.500000  18.860001   14.31  ...    0.12    0.11    0.09
        2022-01-07  20.120001  18.639999   14.04  ...    0.12    0.11    0.09
        2022-01-10  20.309999  18.980000   14.08  ...    0.12    0.11    0.09
        """
        if isinstance(date_or_period, str) or not date_or_period:
            if self.__meta.empty:
                self.__meta = corporate().icm['종목명']
            depo = krx.get_etf_portfolio_deposit_file(ticker=ticker, date=date_or_period)
            if '' in depo.index:
                depo.drop(index=[''], inplace=True)
            return depo.join(self.__meta, how='left')

        elif isinstance(date_or_period, int):
            toc = kst.today()
            objs = []
            for dt in range(date_or_period, -1, -1):
                _date = (toc - timedelta(dt)).date()
                _depo = krx.get_etf_portfolio_deposit_file(ticker=ticker, date=_date.strftime("%Y%m%d"))
                if '' in _depo.index:
                    _depo.drop(index=[''], inplace=True)
                if _depo['비중'].sum() < 10:
                    continue
                if not abs(dt) % 10:
                    time.sleep(1)
                objs.append(pd.DataFrame(data=dict(zip(_depo.index, _depo['비중'])), index=[_date]))
            return pd.concat(objs=objs, axis=0)
        else:
            raise KeyError(f'Argument not appropriate for date_or_period = {date_or_period}')

    def is_etf_latest(self) -> bool:
        prev = pd.read_excel(archive.etf_xl, index_col='종목코드')
        prev.index = prev.index.astype(str).str.zfill(6)
        curr = self.list
        to_be_delete = prev[~prev.index.isin(curr.index)]
        to_be_update = curr[~curr.index.isin(prev.index)]
        if to_be_delete.empty and to_be_update.empty:
            return True
        else:
            for kind, frm in [('삭제', to_be_delete), ('추가', to_be_update)]:
                if not frm.empty:
                    print("-" * 70, f"\n▷ ETF 분류 {kind} 필요 항목: {'없음' if frm.empty else '있음'}")
                    print(frm)

            import os
            os.startfile(archive.etf_xl)
            return False

    @staticmethod
    def excel2csv():
        df = pd.read_excel(archive.etf_xl, index_col='종목코드')
        df.index = df.index.astype(str).str.zfill(6)
        df.to_csv(archive.etf, index=True, encoding='utf-8')
        return


if __name__ == "__main__":
    pd.set_option('display.expand_frame_repr', False)

    corp = corporate()
    # print(corp.icm)
    # print(corp.wics)
    # print(corp.wi26)
    # print(corp.theme)
    print(corp.get_performance())

    # index = index()
    # print(index.deposit)
    #
    # etf = etf()
    # print(etf.group)
    # if etf.is_etf_latest():
    #     etf.excel2csv()