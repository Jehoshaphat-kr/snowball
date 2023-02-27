from datetime import datetime, timedelta
from urllib.request import urlopen
from bs4 import BeautifulSoup as Soup
from pykrx import stock
from snowball.define import int2won
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
    return s.T

def get_asset(stat:pd.DataFrame) -> pd.DataFrame:
    asset = stat[['자산총계', '부채총계', '자본총계']].dropna().astype(int).copy()
    for col in asset.columns:
        asset[f'{col}LB'] = asset[col].apply(int2won)
    return asset

def get_profit(stat:pd.DataFrame) -> pd.DataFrame:
    key = [_ for _ in ['매출액', '순영업수익', '이자수익', '보험료수익'] if _ in stat.columns][0]
    profit = stat[[key, '영업이익', '당기순이익']].dropna().astype(int)
    for col in [key, '영업이익', '당기순이익']:
        profit[f'{col}LB'] = profit[col].apply(int2won)
    return profit

def get_market_cap(ticker:str, todate:str) -> pd.Series:
    fromdate = (datetime.strptime(todate, "%Y%m%d") - timedelta(365 * 5)).strftime("%Y%m%d")
    df = stock.get_market_cap_by_date(fromdate=fromdate, todate=todate, freq='y', ticker=ticker)
    df['시가총액'] = round(df['시가총액'] / 100000000, 1).astype(int)
    df['시가총액LB'] = df.시가총액.apply(int2won)
    # df = df.drop(index=[df.index[-1]])
    df.index = df.index.strftime("%Y/%m")
    df['reindex'] = df.index[:-1].tolist() + [f"{df.index[-1][:4]}/현재"]
    df = df.set_index(keys='reindex')
    return df[['시가총액', '시가총액LB']]

def get_products(ticker: str) -> pd.DataFrame:
    url = f"http://cdn.fnguide.com/SVO2//json/chart/02/chart_A{ticker}_01_N.json"
    src = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'), strict=False)
    header = pd.DataFrame(src['chart_H'])[['ID', 'NAME']].set_index(keys='ID').to_dict()['NAME']
    header.update({'PRODUCT_DATE': '기말'})
    products = pd.DataFrame(src['chart']).rename(columns=header).set_index(keys='기말')
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

    sales_cost = html[4].set_index(keys=['항목'])
    sales_cost.index.name = None

    sg_n_a = html[5].set_index(keys=['항목'])
    sg_n_a.index.name = None

    r_n_d = html[8].set_index(keys=['회계연도'])
    r_n_d.index.name = None
    r_n_d = r_n_d[['R&D 투자 총액 / 매출액 비중.1', '무형자산 처리 / 매출액 비중.1', '당기비용 처리 / 매출액 비중.1']]
    r_n_d = r_n_d.rename(columns={
        'R&D 투자 총액 / 매출액 비중.1': 'R&D투자비중',
        '무형자산 처리 / 매출액 비중.1': '무형자산처리비중',
        '당기비용 처리 / 매출액 비중.1': '당기비용처리비중'
    })
    if '관련 데이터가 없습니다.' in r_n_d.index:
        r_n_d.drop(index=['관련 데이터가 없습니다.'], inplace=True)
    return pd.concat(objs=[sales_cost.T, sg_n_a.T, r_n_d], axis=1).sort_index(ascending=True).astype(float)

def get_consensus(ticker:str) -> pd.DataFrame:
    url = f"http://cdn.fnguide.com/SVO2/json/chart/01_02/chart_A{ticker}.json"
    raw = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
    frm = pd.DataFrame(raw['CHART'])
    frm = frm.rename(columns={'TRD_DT': '날짜', 'VAL1': '투자의견', 'VAL2': '목표주가', 'VAL3': '종가'})
    frm = frm.set_index(keys='날짜')
    frm.index = pd.to_datetime(frm.index)
    frm['목표주가'] = frm['목표주가'].apply(lambda x: int(x) if x else np.nan)
    frm['종가'] = frm['종가'].astype(int)
    return frm

def get_foreign_rate(ticker:str) -> pd.DataFrame:
    objs = dict()
    for dt in ['3M', '1Y', '3Y']:
        url = f"http://cdn.fnguide.com/SVO2/json/chart/01_01/chart_A{ticker}_{dt}.json"
        data = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
        frm = pd.DataFrame(data["CHART"])[['TRD_DT', 'J_PRC', 'FRG_RT']]
        frm = frm.rename(columns={'TRD_DT':'날짜', 'J_PRC':'종가', 'FRG_RT':'외국인보유비중'}).set_index(keys='날짜')
        frm.index = pd.to_datetime(frm.index)
        frm = frm.replace('', '0.0')
        frm['종가'] = frm['종가'].astype(int)
        frm['외국인보유비중'] = frm['외국인보유비중'].astype(float)
        objs[dt] = frm
    return pd.concat(objs=objs, axis=1)

def get_nps(ticker:str) -> pd.DataFrame:
    url = f"http://cdn.fnguide.com/SVO2/json/chart/05/chart_A{ticker}_D.json"
    src = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
    header = pd.DataFrame(src['01_Y_H'])[['ID', 'NAME']].set_index(keys='ID').to_dict()['NAME']
    header.update({'GS_YM': '날짜'})
    data = pd.DataFrame(src['01_Y']).rename(columns=header)[header.values()].set_index(keys='날짜')
    data = data[data != '-']
    for col in data.columns:
        data[col] = data[col].astype(str).str.replace(',', '').astype(float)

    missing = [col for col in ['EPS', 'BPS', 'EBITDAPS', '보통주DPS'] if not col in data.columns]
    if missing:
        data[missing] = np.nan
    return data

def get_multi_factor(ticker:str) -> pd.DataFrame:
    url = f"http://cdn.fnguide.com/SVO2/json/chart/05_05/A{ticker}.json"
    data = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
    header = pd.DataFrame(data['CHART_H'])['NAME'].tolist()
    return pd.DataFrame(data['CHART_D']).rename(
        columns=dict(zip(['NM', 'VAL1', 'VAL2'], ['팩터'] + header))
    ).set_index(keys='팩터').astype(float)

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
    return pd.concat(objs=objs, axis=1)

def get_benchmark_multiple(ticker:str) -> pd.DataFrame:
    url = f"http://cdn.fnguide.com/SVO2/json/chart/01_04/chart_A{ticker}_D.json"
    data = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
    objs = dict()
    for label, index in (('PER', '02'), ('EV/EBITDA', '03'), ('ROE', '04')):
        header1 = pd.DataFrame(data[f'{index}_H'])[['ID', 'NAME']].set_index(keys='ID')
        header1['NAME'] = header1['NAME'].astype(str).str.replace("'", "20")
        header1 = header1.to_dict()['NAME']
        header1.update({'CD_NM': '이름'})

        inner1 = pd.DataFrame(data[index])[list(header1.keys())].rename(columns=header1).set_index(keys='이름')
        inner1.index.name = None
        for col in inner1.columns:
            inner1[col] = inner1[col].apply(lambda x: np.nan if x == '-' else x)
        objs[label] = inner1.T
    return pd.concat(objs=objs, axis=1)

def get_short_sell(ticker:str) -> pd.DataFrame:
    url = f"http://cdn.fnguide.com/SVO2/json/chart/11_01/chart_A{ticker}_SELL1Y.json"
    data = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
    frm = pd.DataFrame(data['CHART'])
    frm = frm.rename(columns={'TRD_DT': '날짜', 'VAL': '차입공매도비중', 'ADJ_PRC': '수정종가'}).set_index(keys='날짜')
    frm.index = pd.to_datetime(frm.index)
    frm['수정종가'] = frm['수정종가'].astype(int)
    frm['차입공매도비중'] = frm['차입공매도비중'].astype(float)
    return frm

def get_short_balance(ticker:str) -> pd.DataFrame:
    url = f"http://cdn.fnguide.com/SVO2/json/chart/11_01/chart_A{ticker}_BALANCE1Y.json"
    data = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
    frm = pd.DataFrame(data['CHART'])[['TRD_DT', 'BALANCE_RT', 'ADJ_PRC']]
    frm = frm.rename(columns={'TRD_DT': '날짜', 'BALANCE_RT': '대차잔고비중', 'ADJ_PRC': '수정종가'}).set_index(keys='날짜')
    frm.index = pd.to_datetime(frm.index)
    frm['수정종가'] = frm['수정종가'].astype(int)
    frm['대차잔고비중'] = frm['대차잔고비중'].astype(float)
    return frm

def get_multiple_band(ticker:str) -> (pd.DataFrame, pd.DataFrame):
    url = f"http://cdn.fnguide.com/SVO2/json/chart/01_06/chart_A{ticker}_D.json"
    src = json.loads(urlopen(url=url).read().decode('utf-8-sig', 'replace'))
    per_header = pd.DataFrame(src['CHART_E'])[['ID', 'NAME']].set_index(keys='ID')
    pbr_header = pd.DataFrame(src['CHART_B'])[['ID', 'NAME']].set_index(keys='ID')
    per_header, pbr_header = per_header.to_dict()['NAME'], pbr_header.to_dict()['NAME']
    per_header.update({'GS_YM': '날짜'})
    pbr_header.update({'GS_YM': '날짜'})

    df = pd.DataFrame(src['CHART'])
    per = df[per_header.keys()].replace('-', np.NaN).replace('', np.NaN)
    pbr = df[pbr_header.keys()].replace('-', np.NaN).replace('', np.NaN)
    per['GS_YM'], pbr['GS_YM'] = pd.to_datetime(per['GS_YM']), pd.to_datetime(pbr['GS_YM'])
    return per.rename(columns=per_header).set_index(keys='날짜'), pbr.rename(columns=pbr_header).set_index(keys='날짜')

def get_multiple_series(ticker:str) -> pd.DataFrame:
    todate = datetime.today().strftime("%Y%m%d")
    fromdate = (datetime.today() - timedelta(3 * 365)).strftime("%Y%m%d")
    return stock.get_market_fundamental(fromdate, todate, ticker)


if __name__ == "__main__":
    # t = "383310"
    t = "005930"
    # df = get_products(ticker=t)
    # df = get_consensus(ticker=t)
    # df = get_foreign_rate(ticker=t)
    # df = get_nps(ticker=t)
    df = get_benchmark_return(ticker=t)
    print(df)