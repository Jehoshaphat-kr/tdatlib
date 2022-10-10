import plotly.graph_objects as go


def set_xaxis(**kwargs) -> dict:
    return dict(
        title=kwargs['title'] if 'title' in kwargs.keys() else '날짜',
        showticklabels=False if 'showticklabels' in kwargs.keys() else True,
        tickformat='%Y/%m/%d',
        zeroline=True if 'zeroline' in kwargs.keys() else False,
        showgrid=True,
        gridcolor='lightgrey',
        autorange=True,
        showline=True,
        linewidth=0.5,
        linecolor='grey',
        mirror=True if 'mirror' in kwargs.keys() else False,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        ) if 'rangeselector' in kwargs.keys() else None
    )


def set_yaxis(**kwargs) -> dict:
    return dict(
        title=kwargs['title'] if 'title' in kwargs.keys() else '[-]',
        showticklabels=True,
        zeroline=True if 'zeroline' in kwargs.keys() else False,
        showgrid=True,
        gridcolor='lightgrey',
        autorange=True,
        showline=True,
        linewidth=0.5,
        linecolor='grey',
        mirror=False
    )


def add_layout(
    fig: go.Figure,
    **kwargs
) -> go.Figure:
    fig.update_layout(
        title=kwargs['title'] if 'title' in kwargs.keys() else '',
        plot_bgcolor='white',
        legend=dict(
            groupclick=kwargs['groupclick'] if 'groupclick' in kwargs.keys() else "toggleitem",
            tracegroupgap=kwargs['tracegroupgap'] if 'tracegroupgap' in kwargs.keys() else 5
        ),
        xaxis=kwargs['xaxis'] if 'xaxis' in kwargs.keys() else set_xaxis(),
        yaxis=kwargs['yaxis'] if 'yaxis' in kwargs.keys() else set_yaxis(),
        xaxis_rangeslider=dict(visible=False)
    )

    attr = dict()
    for key in kwargs.keys():
        if key.startswith('xaxis') or key.startswith('yaxis') and key[-1].isdigit():
            attr[key] = kwargs[key]
    if attr:
        fig.update_layout(attr)
    return fig
