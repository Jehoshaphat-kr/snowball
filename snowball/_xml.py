from xml.etree.ElementTree import ElementTree, fromstring
import pandas as pd
import requests


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