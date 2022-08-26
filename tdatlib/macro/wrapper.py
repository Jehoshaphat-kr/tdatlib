from tdatlib.macro.core import data
from tdatlib.macro.graph import trace
from tdatlib.macro.plot import viewer


class macro(object):
    def __init__(self):
        self.data = data()
        self.trace = trace(self.data)
        self.viewer = viewer(self.trace)
        return
