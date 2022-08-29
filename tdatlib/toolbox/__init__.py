from xml.etree.ElementTree import ElementTree, fromstring
from tdatlib.toolbox.plotter import (
    set_xaxis,
    set_yaxis,
    add_layout
)
import pandas as pd
import requests


def xml_to_df(url: str) -> pd.DataFrame:
    exclude = ['row', 'P_STAT_CODE']

    resp = requests.get(url)
    root = ElementTree(fromstring(resp.text)).getroot()
    data = list()
    for tag in root.findall('row'):
        getter = dict()
        for n, t in enumerate([inner for inner in tag.iter()]):
            if t.tag in exclude:
                continue
            getter.update({t.tag: t.text})
        data.append(getter)

    return pd.DataFrame(data=data) if data else pd.DataFrame()