from pykrx.stock import get_market_cap_by_date
import pandas as pd


def getMarketCap(ticker:str, fromdate:str, todate:str, freq:str='y') -> pd.Series:
    df = get_market_cap_by_date(fromdate=fromdate, todate=todate, freq=freq, ticker=ticker)
    df['시가총액'] = round(df['시가총액'] / 100000000, 1).astype(int)
    df['시가총액LB'] = df.시가총액.apply(lambda x: f'{x}억원' if x < 10000 else f'{str(x)[:-4]}조 {str(x)[-4:]}억원')
    df = df.drop(index=[df.index[-1]])
    df.index = df.index.strftime("%Y/%m")
    return df[['시가총액', '시가총액LB']]
