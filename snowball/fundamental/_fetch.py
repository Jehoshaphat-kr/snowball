from datetime import datetime, timedelta
from urllib.request import urlopen
from bs4 import BeautifulSoup as Soup
from pykrx import stock
import requests, json
import pandas as pd
import numpy as np


def get_summary(ticker:str) -> str:
    u = "http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A%s&cID=&MenuYn=Y&ReportGB=D&NewMenuID=Y&stkGb=701"
    html = Soup(requests.get(u % ticker).content, 'lxml').find('ul', id='bizSummaryContent').find_all('li')
    t = '\n\n '.join([e.text for e in html])
    w = [
        '.\n' if t[n] == '.' and not all([t[n - 1].isdigit(), t[n + 1].isdigit(), t[n + 1].isalpha()]) else t[n]
        for n in range(1, len(t) - 2)
    ]
    s = ' ' + t[0] + ''.join(w) + t[-2] + t[-1]
    return s.replace(' ', '').replace('\xa0\xa0', ' ').replace('\xa0', ' ').replace('\n ', '\n')

def get_statement(ticker:str, **kwargs) -> pd.DataFrame:
    url = f"http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A{ticker}&cID=&MenuYn=Y&ReportGB=D&NewMenuID=Y&stkGb=701"
    html = kwargs['html'] if 'html' in kwargs.keys() else pd.read_html(url, header=0)
    by = kwargs['by'] if 'by' in kwargs.keys() else 'annual'
    if by == 'annual':
        s = html[14] if html[11].iloc[0].isnull().sum() > html[14].iloc[0].isnull().sum() else html[11]
    elif by == 'quarter':
        s = html[15] if html[11].iloc[0].isnull().sum() > html[14].iloc[0].isnull().sum() else html[12]
    else:
        raise KeyError

    cols = s.columns.tolist()
    s.set_index(keys=[cols[0]], inplace=True)
    s.index.name = None
    if isinstance(s.columns[0], tuple):
        s.columns = s.columns.droplevel()
    else:
        s.columns = s.iloc[0]
        s.drop(index=s.index[0], inplace=True)
    return s.T.astype(float)

def get_market_cap(ticker:str, todate:str) -> pd.DataFrame:
    fromdate = (datetime.strptime(todate, "%Y%m%d") - timedelta(365 * 5)).strftime("%Y%m%d")
    df = stock.get_market_cap_by_date(fromdate=fromdate, todate=todate, freq='y', ticker=ticker)
    if df.empty:
        return pd.DataFrame(columns=['????????????'])
    df['????????????'] = round(df['????????????'] / 100000000, 1).astype(int)
    df.index = df.index.strftime("%Y/%m")
    df['reindex'] = df.index[:-1].tolist() + [f"{df.index[-1][:4]}/??????"]
    df = df.set_index(keys='reindex')
    return df

def get_products(ticker: str) -> pd.DataFrame:
    url = f"http://cdn.fnguide.com/SVO2//json/chart/02/chart_A{ticker}_01_N.json"
    src = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'), strict=False)
    header = pd.DataFrame(src['chart_H'])[['ID', 'NAME']].set_index(keys='ID').to_dict()['NAME']
    header.update({'PRODUCT_DATE': '??????'})
    products = pd.DataFrame(src['chart']).rename(columns=header).set_index(keys='??????')
    products = products.drop(columns=[c for c in products.columns if products[c].astype(float).sum() == 0])

    i = products.columns[-1]
    products['Sum'] = products.astype(float).sum(axis=1)
    products = products[(90 <= products.Sum) & (products.Sum < 110)].astype(float)
    products[i] = products[i] - (products.Sum - 100)
    return products.drop(columns=['Sum'])

def get_products_recent(ticker: str = str(), products: pd.DataFrame = None) -> pd.DataFrame:
    if not isinstance(products, pd.DataFrame):
        products = get_products(ticker=ticker)
    i = -1 if products.iloc[-1].astype(float).sum() > 10 else -2
    df = products.iloc[i].T.dropna().astype(float)
    df.drop(index=df[df < 0].index, inplace=True)
    df[df.index[i]] += (100 - df.sum())
    return df[df.values != 0]

def get_expenses(ticker:str) -> pd.DataFrame:
    url = f"http://comp.fnguide.com/SVO2/ASP/SVD_Corp.asp?pGB=1&gicode=A{ticker}&cID=&MenuYn=Y&ReportGB=&NewMenuID=102&stkGb=701"
    html = pd.read_html(url, header=0)

    sales_cost = html[4].set_index(keys=['??????'])
    sales_cost.index.name = None

    sg_n_a = html[5].set_index(keys=['??????'])
    sg_n_a.index.name = None

    r_n_d = html[8].set_index(keys=['????????????'])
    r_n_d.index.name = None
    r_n_d = r_n_d[['R&D ?????? ?????? / ????????? ??????.1', '???????????? ?????? / ????????? ??????.1', '???????????? ?????? / ????????? ??????.1']]
    r_n_d = r_n_d.rename(columns={
        'R&D ?????? ?????? / ????????? ??????.1': 'R&D????????????',
        '???????????? ?????? / ????????? ??????.1': '????????????????????????',
        '???????????? ?????? / ????????? ??????.1': '????????????????????????'
    })
    if '?????? ???????????? ????????????.' in r_n_d.index:
        r_n_d.drop(index=['?????? ???????????? ????????????.'], inplace=True)
    return pd.concat(objs=[sales_cost.T, sg_n_a.T, r_n_d], axis=1).sort_index(ascending=True).astype(float)

def get_consensus(ticker:str) -> pd.DataFrame:
    url = f"http://cdn.fnguide.com/SVO2/json/chart/01_02/chart_A{ticker}.json"
    raw = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
    frm = pd.DataFrame(raw['CHART'])
    frm = frm.rename(columns={'TRD_DT': '??????', 'VAL1': '????????????', 'VAL2': '????????????', 'VAL3': '??????'})
    frm = frm.set_index(keys='??????')
    frm.index = pd.to_datetime(frm.index)
    frm['????????????'] = frm['????????????'].apply(lambda x: int(x) if x else np.nan)
    frm['??????'] = frm['??????'].astype(int)
    frm['?????????'] = round(100 * (frm.??????/frm.???????????? - 1), 2)
    return frm

def get_foreign_rate(ticker:str) -> pd.DataFrame:
    objs = dict()
    for dt in ['3M', '1Y', '3Y']:
        url = f"http://cdn.fnguide.com/SVO2/json/chart/01_01/chart_A{ticker}_{dt}.json"
        data = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
        frm = pd.DataFrame(data["CHART"])[['TRD_DT', 'J_PRC', 'FRG_RT']]
        frm = frm.rename(columns={'TRD_DT':'??????', 'J_PRC':'??????', 'FRG_RT':'?????????????????????'}).set_index(keys='??????')
        frm.index = pd.to_datetime(frm.index)
        frm = frm.replace('', '0.0')
        frm['??????'] = frm['??????'].astype(int)
        frm['?????????????????????'] = frm['?????????????????????'].astype(float)
        objs[dt] = frm
    return pd.concat(objs=objs, axis=1)

def get_nps(ticker:str) -> pd.DataFrame:
    url = f"http://cdn.fnguide.com/SVO2/json/chart/05/chart_A{ticker}_D.json"
    src = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
    header = pd.DataFrame(src['01_Y_H'])[['ID', 'NAME']].set_index(keys='ID').to_dict()['NAME']
    header.update({'GS_YM': '??????'})
    data = pd.DataFrame(src['01_Y']).rename(columns=header)[header.values()].set_index(keys='??????')
    data = data[data != '-']
    for col in data.columns:
        data[col] = data[col].astype(str).str.replace(',', '').astype(float)

    missing = [col for col in ['EPS', 'BPS', 'EBITDAPS', '?????????DPS'] if not col in data.columns]
    if missing:
        data[missing] = np.nan
    return data

def get_multi_factor(ticker:str) -> pd.DataFrame:
    url = f"http://cdn.fnguide.com/SVO2/json/chart/05_05/A{ticker}.json"
    data = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
    header = pd.DataFrame(data['CHART_H'])['NAME'].tolist()
    return pd.DataFrame(data['CHART_D']).rename(
        columns=dict(zip(['NM', 'VAL1', 'VAL2'], ['??????'] + header))
    ).set_index(keys='??????').astype(float)

def get_benchmark_return(ticker:str):
    objs = dict()
    for period in ['3M', '1Y', '3Y']:
        url = f"http://cdn.fnguide.com/SVO2/json/chart/01_01/chart_A{ticker}_{period}.json"
        data = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
        header = pd.DataFrame(data["CHART_H"])[['ID', 'PREF_NAME']]
        header = header[header['PREF_NAME'] != ""]
        inner = pd.DataFrame(data["CHART"])[
            ['TRD_DT'] + header['ID'].tolist()
            ].set_index(keys='TRD_DT').rename(columns=header.set_index(keys='ID').to_dict()['PREF_NAME'])
        inner.index = pd.to_datetime(inner.index)
        objs[period] = inner
    df = pd.concat(objs=objs, axis=1).copy()
    for c in df.columns:
        df[c] = df[c].str.replace(',', '').astype(float)
    return df

def get_benchmark_multiple(ticker:str) -> pd.DataFrame:
    url = f"http://cdn.fnguide.com/SVO2/json/chart/01_04/chart_A{ticker}_D.json"
    data = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
    objs = dict()
    for label, index in (('PER', '02'), ('EV/EBITDA', '03'), ('ROE', '04')):
        header1 = pd.DataFrame(data[f'{index}_H'])[['ID', 'NAME']].set_index(keys='ID')
        header1['NAME'] = header1['NAME'].astype(str).str.replace("'", "20")
        header1 = header1.to_dict()['NAME']
        header1.update({'CD_NM': '??????'})

        inner1 = pd.DataFrame(data[index])[list(header1.keys())].rename(columns=header1).set_index(keys='??????')
        inner1.index.name = None
        for col in inner1.columns:
            inner1[col] = inner1[col].apply(lambda x: np.nan if x == '-' else x)
        objs[label] = inner1.T
    return pd.concat(objs=objs, axis=1).astype(float)

def get_short_sell(ticker:str) -> pd.DataFrame:
    url = f"http://cdn.fnguide.com/SVO2/json/chart/11_01/chart_A{ticker}_SELL1Y.json"
    data = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
    frm = pd.DataFrame(data['CHART'])
    frm = frm.rename(columns={'TRD_DT': '??????', 'VAL': '?????????????????????', 'ADJ_PRC': '????????????'}).set_index(keys='??????')
    frm.index = pd.to_datetime(frm.index)
    frm['????????????'] = frm['????????????'].astype(int)
    frm['?????????????????????'] = frm['?????????????????????'].astype(float)
    return frm

def get_short_balance(ticker:str) -> pd.DataFrame:
    url = f"http://cdn.fnguide.com/SVO2/json/chart/11_01/chart_A{ticker}_BALANCE1Y.json"
    data = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
    frm = pd.DataFrame(data['CHART'])[['TRD_DT', 'BALANCE_RT', 'ADJ_PRC']]
    frm = frm.rename(columns={'TRD_DT': '??????', 'BALANCE_RT': '??????????????????', 'ADJ_PRC': '????????????'}).set_index(keys='??????')
    frm.index = pd.to_datetime(frm.index)
    frm['????????????'] = frm['????????????'].astype(int)
    frm['??????????????????'] = frm['??????????????????'].astype(float)
    return frm

def get_multiple_band(ticker:str) -> (pd.DataFrame, pd.DataFrame):
    url = f"http://cdn.fnguide.com/SVO2/json/chart/01_06/chart_A{ticker}_D.json"
    src = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
    per_header = pd.DataFrame(src['CHART_E'])[['ID', 'NAME']].set_index(keys='ID')
    pbr_header = pd.DataFrame(src['CHART_B'])[['ID', 'NAME']].set_index(keys='ID')
    per_header, pbr_header = per_header.to_dict()['NAME'], pbr_header.to_dict()['NAME']
    per_header.update({'GS_YM': '??????'})
    pbr_header.update({'GS_YM': '??????'})

    df = pd.DataFrame(src['CHART'])
    per = df[per_header.keys()].replace('-', np.NaN).replace('', np.NaN)
    pbr = df[pbr_header.keys()].replace('-', np.NaN).replace('', np.NaN)
    per['GS_YM'], pbr['GS_YM'] = pd.to_datetime(per['GS_YM']), pd.to_datetime(pbr['GS_YM'])
    return per.rename(columns=per_header).set_index(keys='??????').astype(float),\
           pbr.rename(columns=pbr_header).set_index(keys='??????').astype(float)

def get_multiple_series(ticker:str) -> pd.DataFrame:
    todate = datetime.today().strftime("%Y%m%d")
    fromdate = (datetime.today() - timedelta(5 * 365)).strftime("%Y%m%d")
    return stock.get_market_fundamental(fromdate, todate, ticker)


if __name__ == "__main__":
    # df1, df2 = get_multiple_band(ticker='005930')
    print(get_benchmark_return('247540'))
    # print(get_benchmark_multiple('012330'))