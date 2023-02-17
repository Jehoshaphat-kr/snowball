from datetime import datetime, timedelta
from pykrx.stock import (
    get_index_ticker_list,
    get_index_ticker_name,
    get_index_portfolio_deposit_file,
    get_index_ohlcv_by_date
)
import pandas as pd
import yfinance as yf


def _indList() -> pd.DataFrame:
    """
    :return:
                      KOSPI                                KOSDAQ               KRX                      테마
        지수         지수명   지수                         지수명  지수      지수명  지수              지수명
    0   1001         코스피   2001                         코스닥  5042     KRX 100  1163    코스피 고배당 50
    1   1002  코스피 대형주   2002                  코스닥 대형주  5043  KRX 자동차  1164  코스피 배당성장 50
    ...  ...            ...    ...                            ...   ...        ...    ...                 ...
    48   NaN            NaN   2217            코스닥 150 헬스케어   NaN        NaN    NaN                 NaN
    49   NaN            NaN   2218  코스닥 150 커뮤니케이션서비스   NaN        NaN    NaN                 NaN
    """
    objs = dict()
    for market in ('KOSPI', 'KOSDAQ', 'KRX', '테마'):
        indices = get_index_ticker_list(market=market)
        names = [get_index_ticker_name(i) for i in indices]
        objs[market] = pd.DataFrame(data={'지수': indices, '지수명': names})
    return pd.concat(objs=objs, axis=1)


def _indOhlcv(ticker:str, end:str=str(), period:int) -> pd.DataFrame:

    curr = datetime.strptime(end, '%Y%m%d') if end else datetime.now().date()
    prev = curr - timedelta(period * 365)
    if ticker.isdigit():
        _ohlcv = get_index_ohlcv_by_date(fromdate=prev.strftime("%Y%m%d"), todate=curr.strftime("%Y%m%d"), ticker=ticker)
        return _ohlcv.apply(
            lambda x: pd.Series(
                data=[x.종가, x.종가, x.종가, x.종가, 0, 0, 0], index=x.index
            ) if x.시가 == 0 else x,
            axis=1
        )
    else:
        o_names = ['Open', 'High', 'Low', 'Close', 'Volume']
        c_names = ['시가', '고가', '저가', '종가', '거래량']
        _ohlcv = yf.Ticker(ticker).history(period=f'{period}y')[o_names]
        _ohlcv.index.name = '날짜'
        _ohlcv = _ohlcv.rename(columns=dict(zip(o_names, c_names)))
    return _ohlcv


class _fetch(object):

    __today = datetime.now().date()




    def deposit(self, ticker: str) -> list:
        return get_index_portfolio_deposit_file(ticker, date=self.__trading_date)


class _index(_fetch):

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
