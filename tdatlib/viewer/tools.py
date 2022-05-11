from datetime import datetime
import plotly.graph_objects as go
import plotly.offline as of
import os


CD_COLORS = [
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf'   # blue-teal
]

CD_RANGER = dict(
    buttons=list([
        dict(count=1, label="1m", step="month", stepmode="backward"),
        dict(count=3, label="3m", step="month", stepmode="backward"),
        dict(count=6, label="6m", step="month", stepmode="backward"),
        dict(count=1, label="YTD", step="year", stepmode="todate"),
        dict(count=1, label="1y", step="year", stepmode="backward"),
        dict(step="all")
    ])
)



def save(fig: go.Figure, filename: str, path: str = str()):
    """
    :param fig      : 차트
    :param filename : 파일명
    :param path     : 파일 경로
    """
    if path:
        of.plot(fig, filename=f'{path}/{filename}.html', auto_open=False)
        return

    # noinspection PyBroadException
    try:
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    except:
        desktop = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')

    path = f'{desktop}/tdat/{datetime.now().strftime("%Y-%m-%d")}'
    if not os.path.isdir(path):
        os.makedirs(path)
    of.plot(fig, filename=f'{path}/{filename}.html', auto_open=False)
    return


def dform(span) -> list:
    """
    :param span : [list or np.array or pd.Series; iterable] date
    :return     : YY/MM/DD
    """
    return [f'{d.year}/{d.month}/{d.day}' for d in span]


def set_x(title:str, label:bool=True) -> dict:
    """
    :param title : x축 이름
    :param label : label 표출 여부
    """
    return dict(
        title=title, showgrid=True, gridcolor='lightgrey', showticklabels=label, zeroline=False, autorange=True,
        showline=True, linewidth=1, linecolor='grey', mirror=False
    )

def set_y(title:str) -> dict:
    """
    :param title: y축 이름
    """
    return dict(
        title=title, showgrid=True, gridcolor='lightgrey', showticklabels=True, zeroline=False, autorange=True,
        showline=True, linewidth=0.5, linecolor='grey', mirror=False
    )