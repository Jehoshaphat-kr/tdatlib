from tqdm import tqdm
from tdatlib import macro
from plotly.subplots import make_subplots
import plotly.graph_objects as go

import pandas as pd
import os, random


DESKTOP = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')


macro = macro()
macro.data.describe()


fig = make_subplots(specs=[[{"secondary_y":True}]])
fig.add_trace(macro.trace('US_10Y3M_dTY'))
fig.show()
