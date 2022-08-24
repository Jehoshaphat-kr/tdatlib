from tdatlib.dataset import market, index
from tdatlib.viewer import stock
from tdatlib.tdef import labels, crypto
from tqdm import tqdm
from tdatlib.macro import macro_data, macro_view
import pandas as pd
import os, random

DESKTOP = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')



macro_view.미국금리.show()