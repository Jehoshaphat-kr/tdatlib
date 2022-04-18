# import tdatlib, os
# from tqdm import tqdm
# from datetime import datetime
# from tdatlib.viewer.treemap import (
#     treemap,
#     treemap_deploy,
# )
#
# from tdatlib.viewer.stock import (
#     view_technical,
#     view_fundamental
# )
#
# # class view_stock(view_technical, view_fundamental):
# #     def __init__(self, ticker:str, period:int=5, key:str='종가', namebook:pd.DataFrame=pd.DataFrame()):
# #         super(view_technical, self).__init__(ticker=ticker, period=period, key=key, namebook=namebook)
# #         super(view_fundamental, self).__init__(ticker=ticker)
# #         return
#
# def stock_analysis(ticker:str, path:str=str()):
#     """ 주식 기본/기술 분석 데이터 다운로드 """
#     if not path:
#         path = os.path.join(tdatlib.archive.desktop, f'tdat/{datetime.today().strftime("%Y-%m-%d")}')
#         if not os.path.isdir(path):
#             os.makedirs(path)
#
#     tech = tdatlib.view_technical(ticker=ticker, period=3)
#     fund = tdatlib.view_fundamental(ticker=ticker)
#     iteral = [(True, 'fig_basic', '기술_00_가격'),
#               (True, 'fig_bb', '기술_01_볼린저밴드'),
#               (True, 'fig_macd', '기술_02_MACD'),
#               (True, 'fig_rsi', '기술_03_RSI'),
#               (True, 'fig_cci', '기술_04_CCI'),
#               (True, 'fig_stc', '기술_05_STC'),
#               (True, 'fig_mfi', '기술_06_MFI'),
#               (True, 'fig_trix', '기술_07_TRIX'),
#               (True, 'fig_vortex', '기술_08_VORTEX'),
#               (False, 'fig_overview', '기본_00_기업개요'),
#               (False, 'fig_relative', '기본_01_상대지표'),
#               (False, 'fig_supply', '기본_02_수급'),
#               (False, 'fig_multiple', '기본_03_PER_PBR'),
#               (False, 'fig_cost', '기본_04_비용')]
#
#     proc = tqdm(iteral)
#     for __o, attr, title in proc:
#         proc.set_description(desc=title)
#         obj = tech if __o else fund
#         obj.save(getattr(obj, attr), title=title, path=path)
#     return
#
# def stock_related(ticker:str):
#     func = tdatlib.view_fundamental(ticker=ticker)
#     return func.related