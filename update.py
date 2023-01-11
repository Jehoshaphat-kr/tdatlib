from tdatlib.dataset import market as treemap_api_old_version
from tdatlib import market as treemap_api_new_version

RUN_TREEMAP = True
CHK_ETF     = False
CHK_THEME   = False

if __name__ == "__main__":
    # old_treemap = treemap_api_old_version.KR()
    new_treemap = treemap_api_new_version.marketmap

    if RUN_TREEMAP:
        new_treemap.collect()
        new_treemap.pd2js()
        # old_treemap.treemap_deploy()


    """
    ETF 현황 체크
    """
    if CHK_ETF:
        old_treemap.isetfokay()

    """
    테마 항목 상폐 여부 확인
    """
    if CHK_THEME:
        wics  = old_treemap.wics
        theme = old_treemap.theme
        print(theme[~theme.index.isin(wics.index)])

    # from tdatlib import macro
    # macro = macro()
    # df = macro.data.ecos(symbol='817Y002')
    # print(df)