from tdatlib.market.core import krse, etf
from tdatlib.market.index import index
from tdatlib.tools.treemap import treemap


class marketmap(object):
    def __init__(self):
        kq = index.deposit('2001')
        ks200 = index.deposit('1028')
        ksmid = index.deposit('1003')
        kq150 = index.deposit('2203')
        kqmid = index.deposit('2003')

        wics = krse.wics.join(krse.overview.drop(columns=['종목명']), how='left').sort_values(by='시가총액', ascending=False)
        wi26 = krse.wi26.join(krse.overview.drop(columns=['종목명']), how='left').sort_values(by='시가총액', ascending=False)
        them = krse.theme.join(krse.overview.drop(columns=['종목명']), how='left')
        etfs = etf.group.join(etf.overview.drop(columns=['종목명']), how='left').join(etf.returns, how='left')

        wics_main = wics.head(500)
        wics_ks200 = wics[wics.index.isin(ks200)]

        kind = [
            ()
        ]