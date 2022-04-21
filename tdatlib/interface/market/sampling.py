from tqdm import tqdm
import pandas as pd


def get_baseline(tickers:list, wics:pd.DataFrame, icm:pd.DataFrame, perf:pd.DataFrame) -> pd.DataFrame:
    wics = wics[wics.index.isin(tickers)][['종목명', '섹터']].copy()
    return wics.join(icm.drop(columns=['종목명']), how='left').join(perf, how='left')