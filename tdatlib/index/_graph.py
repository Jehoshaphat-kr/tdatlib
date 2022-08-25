from tdatlib.index.core import data
import plotly.graph_objects as go


class _trace(object):

    def __init__(self, src:data):
        self._s = src

