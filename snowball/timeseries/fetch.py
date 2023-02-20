from datetime import datetime, timedelta
from pytz import timezone
from pykrx.stock import (
    get_index_ohlcv_by_date,
    get_market_ohlcv_by_date,
    get_index_ticker_name
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


class _fetch(object):
    __p = 20
    __d = datetime.now(timezone('Asia/Seoul')).date()
    __u = None
    __t = None
    def __init__(self, ticker:str, label:str=None):
        self.ticker = ticker
        self.label = label
        self.mode = symbols.locate(symbol=ticker)
        return

    @property
    def name(self) -> str:
        if not hasattr(self, '__name'):
            if self.mode == 'krx':
                self.__setattr__('__name', get_index_ticker_name(self.ticker))
            elif self.mode == 'krse':
                book = symbols.kr.set_index(keys='symbol').copy()
                self.__setattr__('__name', book.loc[self.ticker, 'longName'])
            elif self.mode == 'ecos':
                self.__setattr__('__name', self.label)
            else:
                self.__setattr__('__name', self.ticker)
        return self.__getattribute__('__name')

    @property
    def unit(self) -> str:
        if not self.__u:
            if self.mode == 'krx': self.__u = '-'
            elif self.mode == 'krse': self.__u = 'KRW'
            elif self.mode == 'ecos': self.__u = '%'
            elif self.mode == 'us': self.__u = 'USD'
            else: self.__u = '%'
        return self.__u

    @unit.setter
    def unit(self, unit:str):
        self.__u = unit

    @property
    def dtype(self) -> str:
        if not self.__t:
            if self.mode == 'krse': self.__t = ',d'
            else: self.__t = ',.2f'
        return self.__t

    @dtype.setter
    def dtype(self, dtype:str):
        self.__t = dtype

    @property
    def enddate(self) -> str:
        return self.__d.strftime("%Y%m%d")

    @enddate.setter
    def enddate(self, enddate:str):
        self.__d = datetime.strptime(enddate, "%Y%m%d")

    @property
    def period(self) -> int or float:
        return self.__p

    @period.setter
    def period(self, period:int or float):
        self.__p = period

    @property
    def src(self) -> pd.DataFrame:
        return self._fetch()

    @property
    def ohlcv(self) -> pd.DataFrame:
        if isinstance(self.src, pd.Series):
            return pd.DataFrame(columns=['시가', '고가', '저가', '종가', '거래량'])
        return self.src

    def _fetch(self) -> pd.DataFrame:
        curr = self.__d
        prev = curr - timedelta(self.period * 365)

        attr = f'__ohlcv{self.enddate}{self.period}'
        if not hasattr(self, attr):
            if self.mode == 'krx':
                self.__setattr__(attr, krx(self.ticker, prev=prev, curr=curr))
            elif self.mode == 'krse':
                self.__setattr__(attr, krse(self.ticker, prev=prev, curr=curr))
            elif self.mode == 'ecos':
                if not self.label:
                    raise KeyError("Label missing")
                self.__setattr__(attr, ecos(self.ticker, self.label, prev=prev, curr=curr))
            elif self.mode == 'nyse':
                self.__setattr__(attr, nyse(self.ticker, self.period))
            else:
                self.__setattr__(attr, fred(self.ticker,prev=prev, curr=curr))
        return self.__getattribute__(attr)