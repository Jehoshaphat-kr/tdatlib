from datetime import datetime
import time as t
import pyautogui as pya
import tdatlib, os

def auto_mouse(t_gap:int=50, due:int=0):
    """
    :param t_gap: in format, int (seconds)
    :param due: in format, %H%M
    :return:
    """
    pya.FAILSAFE = False
    width, height  = pya.size().width, pya.size().height

    while int(datetime.now().strftime("%H%M")) <= due if due else True:
        pya.click(int(width/2), 10)
        t.sleep(t_gap)
        pya.click(int(width / 2), int(height/2))
        t.sleep(t_gap)
    return


if __name__ == "__main__":
    # auto_mouse(t_gap=90)

    # if tdatlib.is_etf_latest(run=False):
    #     tdatlib.etf_excel_to_csv()

    path = os.path.join(tdatlib.archive.desktop, f'tdat/{datetime.today().strftime("%Y-%m-%d")}')
    if not os.path.isdir(path):
        os.makedirs(path)

    ticker = '035720'

    tech = tdatlib.view_technical(ticker=ticker, period=3)
    tech.save(tech.fig_basic, title='기술_00_가격', path=path)
    tech.save(tech.fig_bb, title='기술_01_볼린저밴드', path=path)
    tech.save(tech.fig_macd, title='기술_02_MACD', path=path)
    tech.save(tech.fig_rsi, title='기술_03_RSI', path=path)
    tech.save(tech.fig_cci, title='기술_04_CCI', path=path)
    tech.save(tech.fig_stc, title='기술_05_STC', path=path)
    tech.save(tech.fig_trix, title='기술_06_TRIX', path=path)
    tech.save(tech.fig_vortex, title='기술_07_VORTEX', path=path)

    fund = tdatlib.view_fundamental(ticker=ticker, name=tech.name)
    fund.save(fund.fig_overview, title='기본_00_기업개요', path=path)
    fund.save(fund.fig_relative, title='기본_01_상대지표', path=path)
    fund.save(fund.fig_supply, title='기본_02_수급', path=path)
    fund.save(fund.fig_multiple, title='기본_03_PER_PBR', path=path)
    fund.save(fund.fig_cost, title='기본_04_비용', path=path)