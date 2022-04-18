import pandas as pd


def calc_asset(df_statement:pd.DataFrame) -> pd.DataFrame:
    asset =  df_statement[['자산총계', '부채총계', '자본총계']].fillna(0).astype(int).copy()
    for col in asset.columns:
        asset[f'{col}LB'] = asset[col].apply(lambda x: f'{x}억원' if x < 10000 else f'{str(x)[:-4]}조 {str(x)[-4:]}억원')
    return asset


def calc_profit(df_statement:pd.DataFrame) -> pd.DataFrame:
    key = [_ for _ in ['매출액', '순영업수익', '이자수익', '보험료수익'] if _ in df_statement.columns][0]
    profit = df_statement[[key, '영업이익', '당기순이익']].fillna(0).astype(int) 
    for col in [key, '영업이익', '당기순이익']:
        profit[f'{col}LB'] = profit[col].apply(lambda x: f'{x}억원' if x < 10000 else f'{str(x)[:-4]}조 {str(x)[-4:]}억원')
    return profit