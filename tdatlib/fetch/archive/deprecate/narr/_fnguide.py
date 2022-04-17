import requests, json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from urllib.request import urlopen
from bs4 import BeautifulSoup as Soup
from pykrx import stock
from tdatlib import archive


class fnguide:

    u1 = "http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A%s&cID=&MenuYn=Y&ReportGB=D&NewMenuID=Y&stkGb=701"
    u2 = "http://comp.fnguide.com/SVO2/ASP/SVD_Corp.asp?pGB=1&gicode=A%s&cID=&MenuYn=Y&ReportGB=&NewMenuID=102&stkGb=701"
    def __init__(self, ticker:str):
        self.ticker = ticker
        return

    def _get_name(self) -> str:
        """ 종목명 """
        # noinspection PyBroadException
        try:
            return stock.get_market_ticker_name(ticker=self.ticker)
        except:
            book = pd.read_csv(archive.icm, encoding='utf-8', index_col='종목코드')
            book.index = book.index.astype(str).str.zfill(6)
            return book.loc[self.ticker, '종목명']

    def _get_summary(self) -> str:
        """ 기업개요 요약 다운로드 """
        html = requests.get(self.u1 % self.ticker).content
        texts = Soup(html, 'lxml').find('ul', id='bizSummaryContent').find_all('li')
        text = '\n\n '.join([text.text for text in texts])

        words = []
        for n in range(1, len(text) - 2):
            if text[n] == '.':
                words.append('.' if text[n - 1].isdigit() or text[n + 1].isdigit() or text[n + 1].isalpha() else '.\n')
            else:
                words.append(text[n])
        return ' ' + text[0] + ''.join(words) + text[-2] + text[-1]

    def _get_products(self) -> pd.DataFrame:
        """ 매출 제품 구성 다운로드 """
        url = f"http://cdn.fnguide.com/SVO2//json/chart/02/chart_A{self.ticker}_01_N.json"
        src = json.loads(urlopen(url).read().decode('utf-8-sig', 'replace'))
        header = pd.DataFrame(src['chart_H'])[['ID', 'NAME']].set_index(keys='ID').to_dict()['NAME']
        header.update({'PRODUCT_DATE': '기말'})
        products = pd.DataFrame(src['chart']).rename(columns=header).set_index(keys='기말')

        i = -1 if products.iloc[-1].astype(float).sum() > 10 else -2
        df = products.iloc[i].T.dropna().astype(float)
        df.drop(index=df[df < 0].index, inplace=True)
        df[df.index[i]] += (100 - df.sum())
        return df[df.values != 0]

    def _get_stat_annual(self) -> pd.DataFrame:
        """ 연간 재무 요약 다운로드 """
        if not hasattr(self, 'table1'):
            self.__setattr__('table1', pd.read_html(self.u1 % self.ticker, encoding='utf-8'))
        htmls = self.__getattribute__('table1')

        statement = htmls[14] if htmls[11].iloc[0].isnull().sum() > htmls[14].iloc[0].isnull().sum() else htmls[11]
        cols = statement.columns.tolist()
        statement.set_index(keys=[cols[0]], inplace=True)
        statement.index.name = None
        statement.columns = statement.columns.droplevel()
        return statement.T

    def _get_stat_quarter(self) -> pd.DataFrame:
        """ 분기 재무 요약 다운로드 """
        if not hasattr(self, 'table1'):
            self.__setattr__('table1', pd.read_html(self.u1 % self.ticker, encoding='utf-8'))

        htmls = self.__getattribute__('table1')
        statement = htmls[15] if htmls[11].iloc[0].isnull().sum() > htmls[14].iloc[0].isnull().sum() else htmls[12]
        cols = statement.columns.tolist()
        statement.set_index(keys=[cols[0]], inplace=True)
        statement.index.name = None
        statement.columns = statement.columns.droplevel()
        return statement.T

    def _get_multifactor(self) -> pd.DataFrame:
        """ 멀티팩터 데이터 다운로드 """
        url = f"http://cdn.fnguide.com/SVO2/json/chart/05_05/A{self.ticker}.json"
        data = json.loads(urlopen(url).read().decode('utf-8-sig', 'replace'))
        header = pd.DataFrame(data['CHART_H'])['NAME'].tolist()
        return pd.DataFrame(data['CHART_D']).rename(
            columns=dict(zip(['NM', 'VAL1', 'VAL2'], ['팩터'] + header))
        ).set_index(keys='팩터')

    def _get_benchmark_return(self) -> pd.DataFrame:
        """ 벤치마크 대비 수익률 다운로드 """
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
        return pd.concat(objs=objs, axis=1)

    def _get_benchmark_multiple(self) -> pd.DataFrame:
        """ 벤치마크 대비 투자배수 다운로드 """
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
        return pd.concat(objs=objs, axis=1)

    def _get_consensus(self) -> pd.DataFrame:
        """ 투자의견 다운로드 """
        url = f"http://cdn.fnguide.com/SVO2/json/chart/01_02/chart_A{self.ticker}.json"
        data = json.loads(urlopen(url).read().decode('utf-8-sig', 'replace'))
        consensus = pd.DataFrame(data['CHART']).rename(columns={
            'TRD_DT': '날짜', 'VAL1': '투자의견', 'VAL2': '목표주가', 'VAL3': '종가'
        }).set_index(keys='날짜')
        consensus.index = pd.to_datetime(consensus.index)
        consensus['목표주가'] = consensus['목표주가'].apply(lambda x: int(x) if x else np.nan)
        consensus['종가'] = consensus['종가'].astype(int)
        return consensus

    def _get_foreign_rate(self) -> pd.DataFrame:
        """ 외국인소진율 다운로드 """
        objs = dict()
        for dt in ['3M', '1Y', '3Y']:
            url = f"http://cdn.fnguide.com/SVO2/json/chart/01_01/chart_A{self.ticker}_{dt}.json"
            data = json.loads(urlopen(url).read().decode('utf-8-sig', 'replace'))
            frame = pd.DataFrame(data["CHART"])[['TRD_DT', 'J_PRC', 'FRG_RT']].rename(columns={
                'TRD_DT': '날짜', 'J_PRC': '종가', 'FRG_RT': '외국인보유비중'
            }).set_index(keys='날짜')
            frame.index = pd.to_datetime(frame.index)
            objs[dt] = frame
        return pd.concat(objs=objs, axis=1)

    def _get_short_sell(self) -> pd.DataFrame:
        """ 공매도 비율 다운로드 """
        url = f"http://cdn.fnguide.com/SVO2/json/chart/11_01/chart_A{self.ticker}_SELL1Y.json"
        data = json.loads(urlopen(url).read().decode('utf-8-sig', 'replace'))
        shorts = pd.DataFrame(data['CHART']).rename(columns={
            'TRD_DT': '날짜', 'VAL': '차입공매도비중', 'ADJ_PRC': '수정 종가'
        }).set_index(keys='날짜')
        shorts.index = pd.to_datetime(shorts.index)
        return shorts

    def _get_short_balance(self) -> pd.DataFrame:
        """ 대차 잔고 비율 다운로드 """
        url = f"http://cdn.fnguide.com/SVO2/json/chart/11_01/chart_A{self.ticker}_BALANCE1Y.json"
        data = json.loads(urlopen(url).read().decode('utf-8-sig', 'replace'))
        balance = pd.DataFrame(data['CHART'])[['TRD_DT', 'BALANCE_RT', 'ADJ_PRC']].rename(columns={
            'TRD_DT': '날짜', 'BALANCE_RT': '대차잔고비중', 'ADJ_PRC': '수정 종가'
        }).set_index(keys='날짜')
        balance.index = pd.to_datetime(balance.index)
        return balance

    def _get_expenses(self) -> pd.DataFrame:
        """ 비용처리 데이터 다운로드 """
        if not hasattr(self, 'table2'):
            self.__setattr__('table2', pd.read_html(self.u2 % self.ticker, encoding='utf-8'))
        htmls = self.__getattribute__('table2')

        sales_cost = htmls[4].set_index(keys=['항목'])
        sales_cost.index.name = None

        sg_n_a = htmls[5].set_index(keys=['항목'])
        sg_n_a.index.name = None

        r_n_d = htmls[8].set_index(keys=['회계연도'])
        r_n_d.index.name = None
        r_n_d = r_n_d[['R&D 투자 총액 / 매출액 비중.1', '무형자산 처리 / 매출액 비중.1', '당기비용 처리 / 매출액 비중.1']]
        r_n_d = r_n_d.rename(columns={
            'R&D 투자 총액 / 매출액 비중.1': 'R&D투자비중',
            '무형자산 처리 / 매출액 비중.1': '무형자산처리비중',
            '당기비용 처리 / 매출액 비중.1': '당기비용처리비중'
        })
        if '관련 데이터가 없습니다.' in r_n_d.index:
            r_n_d.drop(index=['관련 데이터가 없습니다.'], inplace=True)
        return pd.concat(objs=[sales_cost.T, sg_n_a.T, r_n_d], axis=1).sort_index(ascending=True)

    def _get_multiple_series(self) -> pd.DataFrame:
        """ 시계열 투자배수 다운로드 """
        todate = datetime.today().strftime("%Y%m%d")
        fromdate = (datetime.today() - timedelta(3 * 365)).strftime("%Y%m%d")
        df = stock.get_market_fundamental(fromdate, todate, self.ticker)
        return df

    def _get_multiple_band(self) -> (pd.DataFrame, pd.DataFrame):
        """ PER / PBR 밴드 데이터 다운로드 """
        url = f"http://cdn.fnguide.com/SVO2/json/chart/01_06/chart_A{self.ticker}_D.json"
        src = json.loads(urlopen(url).read().decode('utf-8-sig', 'replace'))
        per_header = pd.DataFrame(src['CHART_E'])[['ID', 'NAME']].set_index(keys='ID')
        pbr_header = pd.DataFrame(src['CHART_B'])[['ID', 'NAME']].set_index(keys='ID')
        per_header, pbr_header = per_header.to_dict()['NAME'], pbr_header.to_dict()['NAME']
        per_header.update({'GS_YM': '날짜'})
        pbr_header.update({'GS_YM': '날짜'})

        df = pd.DataFrame(src['CHART'])
        per = df[per_header.keys()].replace('-', np.NaN).replace('', np.NaN)
        pbr = df[pbr_header.keys()].replace('-', np.NaN).replace('', np.NaN)
        per['GS_YM'], pbr['GS_YM'] = pd.to_datetime(per['GS_YM']), pd.to_datetime(pbr['GS_YM'])
        return per.rename(columns=per_header).set_index(keys='날짜'), pbr.rename(columns=pbr_header).set_index(keys='날짜')

    def _get_nps(self):
        """ EPS, BPS, EBITA(PS), DPS """
        url = f"http://cdn.fnguide.com/SVO2/json/chart/05/chart_A{self.ticker}_D.json"
        src = json.loads(urlopen(url).read().decode('utf-8-sig', 'replace'))
        header = pd.DataFrame(src['01_Y_H'])[['ID', 'NAME']].set_index(keys='ID').to_dict()['NAME']
        header.update({'GS_YM': '날짜'})
        data = pd.DataFrame(src['01_Y']).rename(columns=header)[header.values()].set_index(keys='날짜')
        data = data[data != '-']
        for col in data.columns:
            data[col] = data[col].astype(str).str.replace(',', '').astype(float)
        return data
