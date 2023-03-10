# from pandas_datareader import get_data_fred
# from datetime import datetime, timedelta
# from pytz import timezone
# import pandas as pd
#
#
# def _fredLoad(symbol: str, period: int) -> pd.Series:
#     """
#     Fetch src from Federal Reserve Economic Data | FRED | St. Louis Fed
#     :param symbol : symbol
#     :return:
#     """
#     today = datetime.now(timezone('Asia/Seoul')).date()
#     start, end = today - timedelta(period * 365), today
#     fetch = get_data_fred(symbols=symbol, start=start, end=end)
#     return pd.Series(
#         name=symbol, dtype=float,
#         index=fetch.index, data=fetch[symbol]
#     )
#
#
# class _fredFrequentlyUsed(object):
#
#     @property
#     def SIR(self) -> pd.Series:
#         return _fredLoad('DFF', 20)
#
#     @property
#     def TY2Y(self) -> pd.Series:
#         return _fredLoad('DGS2', 20)
#
#     @property
#     def TY3Y(self) -> pd.Series:
#         return _fredLoad('DGS3MO', 20)
#
#     @property
#     def TY10Y(self) -> pd.Series:
#         return _fredLoad('DGS10', 20)
#
#     @property
#     def TY10YINFL(self) -> pd.Series:
#         return _fredLoad('DFII10', 20)
#
#     @property
#     def TYD10Y3M(self) -> pd.Series:
#         return _fredLoad('T10Y3M', 20)
#
#     @property
#     def TYD10Y2Y(self) -> pd.Series:
#         return _fredLoad('T10Y2Y', 20)
#
#     @property
#     def JBond(self) -> pd.Series:
#         return _fredLoad('BAMLH0A0HYM2', 20)
#
#     @property
#     def BEI5Y(self) -> pd.Series:
#         return _fredLoad('T5YIE', 20)
#
#     @property
#     def BEI10Y(self) -> pd.Series:
#         return _fredLoad('T10YIE', 20)
#
#     @property
#     def CPI(self) -> pd.Series:
#         return _fredLoad('CPIAUCSL', 20)
#
#     @property
#     def BRENTOIL(self) -> pd.Series:
#         return _fredLoad('DCOILBRENTEU', 20)
#
#     @property
#     def WTIOIL(self) -> pd.Series:
#         return _fredLoad('DCOILWTICO', 20)