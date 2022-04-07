from tdatlib.fetch.market.series import series as dataset
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.offline as of
import numpy as np


class series(dataset):

    def __init__(self, tickers:list or np.array, period:int):
        super().__init__(tickers=tickers, period=period)
        return

