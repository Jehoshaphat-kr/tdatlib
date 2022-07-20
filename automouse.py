from datetime import datetime
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
    auto_mouse(t_gap=90, due=755)