from datetime import datetime
from pykrx.stock import (
    get_index_ohlcv_by_date,
    get_market_ohlcv_by_date
)
from pandas_datareader import get_data_fred
from snowball.archive import symbols
from snowball._xml import xml2df
import pandas as pd
import yfinance as yf


def krx(ticker:str, prev:datetime, curr:datetime):
    fetch = get_index_ohlcv_by_date(
        fromdate=prev.strftime("%Y%m%d"),
        todate=curr.strftime("%Y%m%d"),
        ticker=ticker
    )
    return fetch.apply(
        lambda x: pd.Series(
            data=[x.종가, x.종가, x.종가, x.종가, 0, 0, 0], index=x.index
        ) if x.시가 == 0 else x, axis=1
    )


def krse(ticker:str, prev:datetime, curr:datetime):
    fetch = get_market_ohlcv_by_date(
        fromdate=prev.strftime("%Y%m%d"),
        todate=curr.strftime("%Y%m%d"),
        ticker=ticker
    )
    trade_stop = fetch[fetch.시가 == 0].copy()
    if not trade_stop.empty:
        fetch.loc[trade_stop.index, ['시가', '고가', '저가']] = trade_stop['종가']
    return fetch


def ecos(symbol:str, label:str, prev:datetime, curr:datetime) -> pd.Series:
    contained = symbols.econtain(symbol=symbol)
    key = contained[contained.이름 == label]
    if key.empty:
        raise KeyError(f'{label} not found in {contained.이름}')

    if len(key) > 1:
        cnt = key['개수'].astype(int).max()
        key = key[key.개수 == str(cnt)]

    api = "CEW3KQU603E6GA8VX0O9"
    name, code, c, s, e, _ = tuple(key.values[0])
    url = f'http://ecos.bok.or.kr/api/StatisticSearch/{api}/xml/kr/1/100000/{symbol}/{c}/{s}/{e}/{code}'
    fetch = xml2df(url=url)
    tseries = pd.Series(
        name=name, dtype=float,
        index=pd.to_datetime(fetch.TIME + ('01' if c == 'M' else '1231' if c == 'Y' else '')),
        data=fetch.DATA_VALUE.tolist()
    )
    if c == 'M':
        tseries.index = tseries.index.to_period('M').to_timestamp('M')
    return tseries[tseries.index >= prev.strftime("%Y-%m-%d")]


def nyse(ticker:str, period:int) -> pd.DataFrame:
    o_names = ['Open', 'High', 'Low', 'Close', 'Volume']
    c_names = ['시가', '고가', '저가', '종가', '거래량']
    ohlcv = yf.Ticker(ticker).history(period=f'{period}y')[o_names]
    ohlcv.index.name = '날짜'
    return ohlcv.rename(columns=dict(zip(o_names, c_names)))


def fred(symbol: str, prev:datetime, curr:datetime) -> pd.Series:
    fetch = get_data_fred(symbols=symbol, start=prev, end=curr)
    return pd.Series(name=symbol, dtype=float, index=fetch.index, data=fetch[symbol])