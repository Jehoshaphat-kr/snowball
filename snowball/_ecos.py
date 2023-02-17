from datetime import datetime, timedelta
from pytz import timezone
from snowball._xml import xml2df
import pandas as pd


__k = "CEW3KQU603E6GA8VX0O9"


def _ecosSymbol():
    """
    ECOS Symbol list

            코드                                 지표명 주기    발행처
    4    102Y004  본원통화 구성내역(평잔, 계절조정계열)    M  한국은행
    5    102Y002        본원통화 구성내역(평잔, 원계열)    M  한국은행
    ..       ...                                    ...   ..       ...
    795  251Y002                          한국/북한 배율   A      None
    796  251Y001       북한의 경제활동별 실질 국내총생산   A  한국은행
    :return:
    """
    url = f"http://ecos.bok.or.kr/api/StatisticTableList/{__k}/xml/kr/1/10000/"
    df = xml2df(url=url)
    df = df[df.SRCH_YN == 'Y'].copy()
    df['STAT_NAME'] = df.STAT_NAME.apply(lambda x: x[x.find(' ') + 1:])
    df = df.drop(columns='SRCH_YN')
    return df.rename(columns={'STAT_CODE': '코드', 'STAT_NAME': '지표명', 'CYCLE': '주기', 'ORG_NAME': '발행처'})


def _ecosContains(symbol: str):
    """
    Single ECOS symbol containing label list
    :param symbol: ECOS symbol

                                 이름 주기      시점      종점  개수
    0           콜금리(1일, 전체거래)    D  19950103  20221005  7081
    1       콜금리(1일, 중개회사거래)    D  19960103  20221005  6785
    ...                           ...  ...
    24                  통안증권(1년)    D  19950103  20221005  7042
    25                   국고채(50년)    D  20161011  20221005  1479
    """
    columns = dict(
        ITEM_NAME='이름',
        ITEM_CODE='코드',
        CYCLE='주기',
        START_TIME='시점',
        END_TIME='종점',
        DATA_CNT='개수'
    )
    url = f"http://ecos.bok.or.kr/api/StatisticItemList/{__k}/xml/kr/1/10000/{symbol}"
    return xml2df(url=url)[columns.keys()].rename(columns=columns)


def _ecosLoad(symbol:str, label:str, period:int):
    """
    ECOS Time-Series Data
    :param symbol: ECOS symbol
    :param label : ECOS label contained in symbol
    :param period: time series period in year
    :return:
    """
    contained = _ecosContains(symbol=symbol)
    key = contained[contained.이름 == label]
    if key.empty:
        raise KeyError(f'{label} not found in {contained.이름}')
    if len(key) > 1:
        cnt = key['개수'].astype(int).max()
        key = key[key.개수 == str(cnt)]

    today = datetime.now(timezone('Asia/Seoul')).date()
    name, code, c, s, e, _ = tuple(key.values[0])
    url = f'http://ecos.bok.or.kr/api/StatisticSearch/{__k}/xml/kr/1/100000/{symbol}/{c}/{s}/{e}/{code}'
    fetch = xml2df(url=url)
    series = pd.Series(
        name=name, dtype=float,
        index=pd.to_datetime(fetch.TIME + ('01' if c == 'M' else '1231' if c == 'Y' else '')),
        data=fetch.DATA_VALUE.tolist()
    )
    if c == 'M':
        series.index = series.index.to_period('M').to_timestamp('M')
    return series[series.index >= (today - timedelta(period * 365)).strftime("%Y-%m-%d")]


class _ecosFrequentlyUsed(object):

    @property
    def SIR(self) -> pd.Series:
        """
        Korea Standard Interest Rate
        """
        return _ecosLoad('722Y001', '한국은행 기준금리', 20)

    @property
    def TY1Y(self) -> pd.Series:
        """
        Korea Treasury Yield 1 Year
        """
        return _ecosLoad('817Y002', '국고채(1년)', 20)

    @property
    def TY2Y(self) -> pd.Series:
        """
        Korea Treasury Yield 2 Year
        """
        return _ecosLoad('817Y002', '국고채(2년)', 20)

    @property
    def TY3Y(self) -> pd.Series:
        """
        Korea Treasury Yield 3 Year
        """
        return _ecosLoad('817Y002', '국고채(3년)', 20)

    @property
    def TY5Y(self) -> pd.Series:
        """
        Korea Treasury Yield 5 Year
        """
        return _ecosLoad('817Y002', '국고채(5년)', 20)

    @property
    def TY10Y(self) -> pd.Series:
        """
        Korea Treasury Yield 10 Year
        """
        return _ecosLoad('817Y002', '국고채(10년)', 20)

    @property
    def CD91D(self) -> pd.Series:
        """
        Korea CD Interest Rate 91 Days
        """
        return _ecosLoad('817Y002', 'CD(91일)', 20)

    @property
    def CP91D(self) -> pd.Series:
        """
        Korea CP Interest Rate 91 Days
        """
        return _ecosLoad('817Y002', 'CP(91일)', 20)

    @property
    def LCapBond3Y(self) -> pd.Series:
        """
        Korea Corporate Bond Yield 3Y AAm
        """
        return _ecosLoad('817Y002', '회사채(3년, AA-)', 20)

    @property
    def JBond3Y(self) -> pd.Series:
        """
        Korea Corporate Junk Bond Yield 3Y
        :return:
        """
        return _ecosLoad('817Y002', '회사채(3년, BBB-)', 20)

    @property
    def USDExchange(self) -> pd.DataFrame:
        return pd.concat(
            objs=dict(
                시가=_ecosLoad('731Y003', '원/달러(시가)', 20),
                고가=_ecosLoad('731Y003', '원/달러(고가)', 20),
                저가=_ecosLoad('731Y003', '원/달러(저가)', 20),
                종가=_ecosLoad('731Y003', '원/달러(종가)', 20)
            ), axis=1
        )