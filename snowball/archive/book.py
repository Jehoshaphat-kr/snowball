from pykrx.stock import (
    get_index_ticker_list,
    get_index_ticker_name
)
from stocksymbol import StockSymbol
from snowball.define import xml2df
import pandas as pd
import os


class _symbols(object):
    _engine_s = StockSymbol("95012214-44b0-4664-813f-a7ef5ad3b0b4")
    _dir = os.path.dirname(__file__)

    def __init__(self):
        pass

    @property
    def kr(self) -> pd.DataFrame:
        """
              symbol             shortName                    longName exchange     market quoteType      name       sector
        0     000020          DongwhaPharm       Dongwha Pharm.Co.,Ltd       KS  kr_market    EQUITY  동화약품     건강관리
        1     000040             KR MOTORS          KR Motors Co., Ltd       KS  kr_market    EQUITY  KR모터스       자동차
        2     000050             Kyungbang           Kyungbang Co.,Ltd       KS  kr_market    EQUITY      경방  화장품,의류
        ...      ...                   ...                         ...      ...        ...       ...       ...          ...
        2639  950200              Psomagen              Psomagen, Inc.       KQ  kr_market    EQUITY       NaN          NaN
        2640  950210    PRESTIGE BIOPHARMA  Prestige BioPharma Limited       KS  kr_market    EQUITY       NaN          NaN
        2641  950220  NeoImmuneTech(Reg.S)         NeoImmuneTech, Inc.       KQ  kr_market    EQUITY       NaN          NaN
        """
        if not hasattr(self, '__kr'):
            kr = pd.DataFrame(self._engine_s.get_symbol_list(market='kr'))
            split = kr.symbol.str.split('.').str
            kr['symbol'] = split[0]
            kr['exchange'] = split[1]
            kr.set_index(keys='symbol', inplace=True)

            local = pd.concat(
                objs=[
                    pd.read_csv(os.path.join(self._dir, r'krse/wi26.csv'), dtype=str),
                    pd.read_csv(os.path.join(self._dir, r'krse/etf.csv'), dtype=str)
                ], axis=0
            )
            local.set_index(keys='종목코드', inplace=True)
            kr = kr.join(local[['종목명', '섹터']].rename(columns={'종목명':'name', '섹터':'sector'}), how='left')
            kr.index.name = 'symbol'
            self.__setattr__('__kr', kr.reset_index(level=0))
        return self.__getattribute__('__kr')

    @property
    def us(self) -> pd.DataFrame:
        """
             symbol  shortName                   longName exchange     market quoteType
        0      AAPL      apple                 Apple Inc.   NASDAQ  us_market    EQUITY
        1      MSFT  microsoft      Microsoft Corporation   NASDAQ  us_market    EQUITY
        2      GOOG   alphabet              Alphabet Inc.   NASDAQ  us_market    EQUITY
        ...     ...        ...                        ...      ...        ...       ...
        8777   FLCX                        flooidCX Corp.      OTC  us_market    EQUITY
        8778   BLEG                   BRANDED LEGACY INC.      OTC  us_market    EQUITY
        8779   RRIF             Rainforest Resources Inc.      OTC  us_market    EQUITY
        """
        if not hasattr(self, '__us'):
            self.__setattr__('__us', pd.DataFrame(self._engine_s.get_symbol_list(market='us')))
        return self.__getattribute__('__us')

    @property
    def ecos(self) -> pd.DataFrame:
        """
              symbol                                    name cycle     quote
        4    102Y004   본원통화 구성내역(평잔, 계절조정계열)     M  한국은행
        5    102Y002         본원통화 구성내역(평잔, 원계열)     M  한국은행
        6    102Y003   본원통화 구성내역(말잔, 계절조정계열)     M  한국은행
        ..       ...                                     ...   ...       ...
        815  251Y003                                    총량     A      None
        816  251Y002                          한국/북한 배율     A      None
        817  251Y001       북한의 경제활동별 실질 국내총생산     A  한국은행
        """
        if not hasattr(self, '__ecos'):
            api = "CEW3KQU603E6GA8VX0O9"
            url = f"http://ecos.bok.or.kr/api/StatisticTableList/{api}/xml/kr/1/10000/"
            df = xml2df(url=url)
            df = df[df.SRCH_YN == 'Y'].copy()
            df['STAT_NAME'] = df.STAT_NAME.apply(lambda x: x[x.find(' ') + 1:])
            df = df.drop(columns='SRCH_YN')
            self.__setattr__(
                '__ecos',
                df.rename(columns={'STAT_CODE': 'symbol', 'STAT_NAME': 'name', 'CYCLE': 'cycle', 'ORG_NAME': 'quote'})
            )
        return self.__getattribute__('__ecos')

    @property
    def krx(self) -> pd.DataFrame:
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

    def econtain(self, symbol:str):
        if not hasattr(self, f'__ecos{symbol}'):
            columns = dict(
                ITEM_NAME='이름',
                ITEM_CODE='코드',
                CYCLE='주기',
                START_TIME='시점',
                END_TIME='종점',
                DATA_CNT='개수'
            )
            api = "CEW3KQU603E6GA8VX0O9"
            url = f"http://ecos.bok.or.kr/api/StatisticItemList/{api}/xml/kr/1/10000/{symbol}"
            self.__setattr__(f'__ecos{symbol}', xml2df(url=url)[columns.keys()].rename(columns=columns))
        return self.__getattribute__(f'__ecos{symbol}')

    def locate(self, symbol:str):
        if symbol.isdigit() and len(symbol) == 4:
            return 'krx'
        elif symbol.isdigit() and len(symbol) == 6:
            return 'krse'
        elif symbol in self.ecos.symbol.values:
            return 'ecos'
        elif symbol in self.us.symbol.values:
            return 'nyse'
        else:
            pass
        return 'fred'

# Alias
symbols = _symbols()

if __name__ == "__main__":
    pd.set_option('display.expand_frame_repr', False)

    # print(symbols.kr)
    # print(symbols.us)
    # print(symbols.ecos)