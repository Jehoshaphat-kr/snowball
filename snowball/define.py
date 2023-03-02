from xml.etree.ElementTree import ElementTree, fromstring
import pandas as pd
import numpy as np
import requests

colors = [
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf'   # blue-teal
]

# int2won = lambda x: f'{x}억원' if (type(x) == float or type(x) == int) and x < 10000 else f'{str(x)[:-4]}조 {str(x)[-4:]}억원'
def int2won(x):
    if np.isnan(x):
        return np.nan
    x = int(x)
    return f'{x}억원' if x < 10000 else f'{str(x)[:-4]}조 {str(x)[-4:]}억원'

def xml2df(url: str) -> pd.DataFrame:
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


if __name__ == "__main__":
    print(not np.nan)