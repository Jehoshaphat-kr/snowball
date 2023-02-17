from datetime import datetime, timedelta
from pytz import timezone
from snowball.archive import symbols
from snowball.timeseries.fetch import (
    krx,
    krse,
    ecos,
    nyse,
    fred
)
import pandas as pd


class TimeSeries:
    __p = 20
    __d = datetime.now(timezone('Asia/Seoul')).date()
    def __init__(self, ticker:str, label:str=None):
        self.ticker = ticker
        self.label = label
        self.mode = symbols.locate(symbol=ticker)
        return

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
    def ohlcv(self) -> pd.DataFrame:
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
