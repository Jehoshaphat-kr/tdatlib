from tqdm import tqdm
from tdatlib import toolbox, macro, index
from plotly.subplots import make_subplots
import plotly.graph_objects as go

import pandas as pd
import os, random


DESKTOP = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')

PERIOD = 20

macro = macro()
index = index()

macro.data.period = index.data.period = PERIOD
# macro.data.describe()

fig = make_subplots(specs=[[{"secondary_y":True}]])
fig.add_trace(index.trace('bank', key='종가', unit='-'), secondary_y=False)
fig.add_trace(macro.trace('KRW_USD_exchange', key='종가', unit='원'), secondary_y=True)
# fig.add_trace(macro.trace('KR_10Y_TY', unit='%'), secondary_y=True)
# fig.add_trace(macro.trace('US_10Y_TY', unit='%'), secondary_y=True)

toolbox.add_layout(
    fig,
    yaxis=toolbox.set_xaxis(title='-'),
    yaxis2=toolbox.set_yaxis(title='원')
)
fig.show()
