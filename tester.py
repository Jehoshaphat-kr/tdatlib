import tdatlib
from pykrx import stock as krx
from datetime import datetime, timedelta
from pytz import timezone
from tqdm import tqdm
import pandas as pd
import time as t
import pyautogui as pya


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
    #
    # pd.set_option('display.expand_frame_repr', False)
    # kst = datetime.now(timezone('Asia/Seoul'))
    # t_today = kst.strftime("%Y%m%d")
    # t_stamp = [(kst - timedelta(days)).strftime("%Y%m%d") for days in [7, 30, 91, 183, 365]]
    #
    # if tl.is_etf_latest():
    #     tl.convert_etf_excel2csv()

    print(tdatlib.kmarket.wics)