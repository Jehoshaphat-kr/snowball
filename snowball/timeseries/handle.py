from datetime import timedelta, datetime
from snowball.timeseries.fetch import _fetch
import pandas as pd


class _handle(_fetch):

    @property
    def typrice(self) -> pd.Series:
        return (self.ohlcv.고가 + self.ohlcv.저가 + self.ohlcv.종가)/3

    @property
    def max52w(self) -> int or float:
        if self.ohlcv.empty:
            return None
        return self.ohlcv[self.ohlcv.index >= (self.ohlcv.index[-1] - timedelta(365))].max()['종가']

    @property
    def min52w(self) -> int or float:
        if self.ohlcv.empty:
            return None
        return self.ohlcv[self.ohlcv.index >= (self.ohlcv.index[-1] - timedelta(365))].min()['종가']


if __name__ == "__main__":
    test = _handle(ticker='DGS10')
    print(test.src)
    print(test.ohlcv)
    print(test.typrice)
    print(test.max52w)