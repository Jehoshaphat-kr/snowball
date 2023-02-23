from datetime import datetime, timedelta
from pykrx.stock import (
    get_index_ticker_list,
    get_index_ticker_name,
    get_index_portfolio_deposit_file,
    get_index_ohlcv_by_date
)
import pandas as pd
import yfinance as yf


class _index(object):

    period = 10

    @property
    def kospi(self) -> pd.DataFrame:
        if not hasattr(self, f'__kospi_{self.period}'):
            self.__setattr__(f'__kospi_{self.period}', self.ohlcv(ticker='1001'))
        return self.__getattribute__(f'__kospi_{self.period}')

    @property
    def kosdaq(self) -> pd.DataFrame:
        if not hasattr(self, f'__kosdaq_{self.period}'):
            self.__setattr__(f'__kosdaq_{self.period}', self.ohlcv(ticker='2001'))
        return self.__getattribute__(f'__kosdaq_{self.period}')

    @property
    def bank(self) -> pd.DataFrame: # 은행 한정
        if not hasattr(self, f'__bank_{self.period}'):
            self.__setattr__(f'__bank_{self.period}', self.ohlcv(ticker='5046'))
        return self.__getattribute__(f'__bank_{self.period}')

    @property
    def financial(self) -> pd.DataFrame: # 금융업(은행, 보험, 증권)
        if not hasattr(self, f'__financial_{self.period}'):
            self.__setattr__(f'__financial_{self.period}', self.ohlcv(ticker='5352'))
        return self.__getattribute__(f'__financial_{self.period}')

    @property
    def snp500(self) -> pd.DataFrame:
        if not hasattr(self, f'__snp500_{self.period}'):
            self.__setattr__(f'__snp500_{self.period}', self.ohlcv(ticker='^GSPC'))
        return self.__getattribute__(f'__snp500_{self.period}')

    @property
    def nasdaq(self) -> pd.DataFrame:
        if not hasattr(self, f'__nasdaq_{self.period}'):
            self.__setattr__(f'__nasdaq_{self.period}', self.ohlcv(ticker='^IXIC'))
        return self.__getattribute__(f'__nasdaq_{self.period}')

    @property
    def properties(self) -> list:
        exclude = [
            'properties',
            'deposit',
            'period',
            'trading_date',
            'kind',
            'ohlcv',
            'describe'
        ]
        return [elem for elem in self.__dir__() if not elem.startswith('_') and not elem in exclude]

    def describe(self):
        for e in self.properties:
            print(e)
        return


# Alias
index = _index()

if __name__ == "__main__":
    import plotly.graph_objects as go

    pd.set_option('display.expand_frame_repr', False)

    index.period = 20

    # print(index.kind)
    print(index.bank)
    # print(len(index.deposit(ticker='5352')), index.deposit(ticker='5352'))
    # index.describe()
