import pandas as pd
import plotly.graph_objects as go


def setXaxis(title:str, label:bool=True, xranger:bool=True) -> dict:
    """
    X축 Layout 설정
    :param title: x축 이름
    :param label: label 표출 여부
    :param xranger: range selector 표출 여부
    """
    x = dict(
        title=title, showgrid=True, gridcolor='lightgrey', showticklabels=label, zeroline=False, autorange=True,
        showline=True, linewidth=1, linecolor='grey', mirror=False
    )
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
    return dict(
        title=title, showgrid=True, gridcolor='lightgrey', showticklabels=True, zeroline=False, autorange=True,
        showline=True, linewidth=0.5, linecolor='grey', mirror=False
    )

def reform(span) -> list:
    """
    날짜 형식 변경 (from)datetime --> (to)YY/MM/DD
    :param span: 날짜 리스트
    :return:
    """
    return [f'{d.year}/{d.month}/{d.day}' for d in span]

def traceLine(
        data:pd.Series,
        unit:str='[-]',
        name:str=str(),
        visible:bool or str=True,
        showlegend:bool=True,
        color:str=str(),
        dtype:str='float'
) -> go.Scatter:
    """
    1-D 시계열 차트
    :param data: [pd.Series] 데이터
    :param unit: 단위
    :param name: 이름
    :param visible: 시각화 여부
    :param showlegend: 범례 여부
    :param color: 색상
    :param dtype: 데이터 타입
    :return: 
    """
    exp = '%{y:.2f}' if dtype == 'float' else '%{y:,}'
    scatter = go.Scatter(
        name=data.name if not name else name, x=data.index, y=data,
        visible=visible, showlegend=showlegend,
        meta=reform(span=data.index),
        hovertemplate='날짜: %{meta}<br>' + f'{str(data.name)}: {exp}{unit}<extra></extra>'
    )
    if color:
        scatter['line'] = dict(color=color)
    return scatter

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

def traceScatter(
        data:pd.Series,
        name:str=str(),
        unit:str='[-]',
        symbol:str='circle',
        color:str=str(),
        size:int=8,
        opacity:float=0.8,
        visible:str='legendonly',
        showlegend:bool=True,
        dtype:str='int'
) -> go.Scatter:
    """
    1-D 산포도 
    :param data: [pd.Series] 데이터
    :param name: 데이터 이름
    :param unit: 데이터 단위
    :param symbol: 마커 표시
    :param color: 마커 색상
    :param size: 마커 크키
    :param opacity: 마커 투명도
    :param visible: 시각화 여부
    :param showlegend: 범례 여부
    :param dtype: 데이터 타입
    """
    data = data.dropna()
    marker = dict(symbol=symbol, size=size, opacity=opacity)
    if color:
        marker.update(dict(color=color))
    exp = '%{y:.2f}' if dtype == 'float' else '%{y:,}'
    return go.Scatter(
        name=name if name else data.name, x=data.index, y=data,
        mode='markers', marker=marker, visible=visible, showlegend=showlegend,
        meta=reform(span=data.index),
        hovertemplate='날짜: %{meta}<br>' + f'{name}: ' + exp + unit + '<extra></extra>'
    )


