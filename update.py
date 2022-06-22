from tdatlib.dataset import market


RUN_TREEMAP = True
CHK_ETF     = False
CHK_THEME   = False

if __name__ == "__main__":
    myMarket = market.KR()

    if RUN_TREEMAP:
        myMarket.treemap_deploy()

    """
    ETF 현황 체크
    """
    if CHK_ETF:
        myMarket.isetfokay()

    """
    테마 항목 상폐 여부 확인
    """
    if CHK_THEME:
        wics  = myMarket.wics
        theme = myMarket.theme
        print(theme[~theme.index.isin(wics.index)])