from tdatlib import market
from pykrx import stock as krx
import numpy as np
import pandas as pd
import plotly.graph_objects as go


def setXaxis(title:str, label:bool=True, xranger:bool=True) -> dict:
    """
    X축 Layout 설정
    :param title: x축 이름
    :param label: label 표출 여부
    :param xranger: range selector 표출 여부
    """
    x = dict(title=title, showgrid=True, gridcolor='lightgrey', showticklabels=label, zeroline=False, autorange=True)
    if xranger:
        x.update(dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        ))
    return x

def setYaxis(title) -> dict:
    """
    Y축 Layout 설정
    :param title: y축 이름
    """
    return dict(title=title, showgrid=True, gridcolor='lightgrey', showticklabels=True, zeroline=False, autorange=True)

def reform(span) -> list:
    """
    날짜 형식 변경 (from)datetime --> (to)YY/MM/DD
    :param span: 날짜 리스트
    :return:
    """
    return [f'{d.year}/{d.month}/{d.day}' for d in span]

def traceCandle(ohlcv:pd.DataFrame, gap:str='일봉') -> go.Candlestick:
    """
    캔들 차트 오브젝트
    :param ohlcv: 가격 데이터프레임
    :param gap: 캔들명 - 일봉/주봉/월봉...
    """
    return go.Candlestick(
        name=gap, x=ohlcv.index, open=ohlcv.시가, high=ohlcv.고가, low=ohlcv.저가, close=ohlcv.종가,
        increasing_line=dict(color='red'), decreasing_line=dict(color='royalblue'),
        visible=True, showlegend=True,
    )

def traceLine(
        data:pd.Series,
        unit:str,
        name:str=str(),
        visible:bool or str=True,
        showlegend:bool=True,
        dtype:str='float'
) -> go.Scatter:
    """
    1-D 시계열 차트
    :param data: [pd.Series] 데이터
    :param unit: 단위
    :param name: 이름
    :param visible: 시각화 여부
    :param showlegend: 범례 여부
    :param dtype: 데이터 타입
    :return: 
    """
    exp = '%{y:.2f}' if dtype == 'float' else '%{y:,}'
    return go.Scatter(
        name=data.name if not name else name, x=data.index, y=data,
        visible=visible, showlegend=showlegend,
        meta=reform(span=data.index),
        hovertemplate='날짜: %{meta}<br>' + f'{str(data.name)}: {exp}{unit}<extra></extra>'
    )

def traceBar(data:pd.Series, name:str, color:str or list or pd.Series) -> go.Bar:
    """
    1-D 시계열 막대 차트
    :param data: [pd.Series] 데이터
    :param name: 이름
    :param color: 색상
    :return: 
    """
    if isinstance(color, str) and color == 'zc':
        color = ['royalblue' if y < 0 else 'red' for y in data.pct_change().fillna(1)]
    return go.Bar(
        name=name, x=data.index, y=data,
        marker=dict(color=color),
        visible=True, showlegend=True,
        meta=reform(span=data.index),
        hovertemplate='날짜: %{meta}<br>' + name + ': %{y:.2f}<extra></extra>'
    )

def traceVolume(volume:pd.Series) -> go.Bar:
    """
    거래량 바 차트
    :param volume: [pd.Series] 거래량
    """
    return go.Bar(
        name='거래량', x=volume.index, y=volume,
        marker=dict(color=['blue' if d < 0 else 'red' for d in volume.pct_change().fillna(1)]),
        visible=True, showlegend=True,
        meta=reform(span=volume.index),
        hovertemplate='날짜:%{meta}<br>거래량:%{y:,d}<extra></extra>'
    )


