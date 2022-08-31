from tdatlib.index.core import data
from tdatlib.index.graph import trace
# from tdatlib.macro.plot import viewer


class index(object):
    def __init__(self):
        self.data = data()
        self.trace = trace(self.data)
        # self.viewer = viewer(self.trace)
        return
