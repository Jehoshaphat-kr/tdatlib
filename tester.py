from tqdm import tqdm
from tdatlib import toolbox, macro
from plotly.subplots import make_subplots
import plotly.graph_objects as go

import pandas as pd
import os, random


DESKTOP = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')


macro = macro()
macro.data.describe()

fig = make_subplots(specs=[[{"secondary_y":True}]])
fig.add_trace(macro.trace('KRW_USD_exchange', key='종가', unit='원'))
# fig.add_trace(macro.trace('KR_10Y_TY', unit='%'), secondary_y=True)
fig.add_trace(macro.trace('US_10Y_TY_Inflation', unit='%'), secondary_y=True)

toolbox.add_layout(
    fig,
    xaxis=toolbox.set_xaxis(title='원'),
    yaxis2=toolbox.set_yaxis(title='%')
)
fig.show()
