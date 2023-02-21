from snowball.fundamental._fnguide import (
    getSummary,
    getAllProducts,
    getRecentProducts,
    getStatement,
    getExpenses,
    getConsensus,
    getForeigner,
    getNps,
    getMultifactor,
    getBenchmarkReturn,
    getBenchmarkMultiple,
    getShortSell,
    getShortBalance,
    getMultipleBand,
    getMultipleSeries
)
from snowball.timeseries import TimeSeries
import pandas as pd


class fnguide(TimeSeries):

    __by = 'annual'

    def _set_(self, name:str, func, **kwargs):
        if not hasattr(self, name):
            self.__setattr__(name, func(self.ticker, **kwargs))
        return self.__getattribute__(name)

    @property
    def by(self) -> str:
        return self.__by

    @by.setter
    def by(self, period:str):
        if not period in ['annual', 'quarter']:
            raise KeyError
        self.__by = period

    @property
    def _html(self) -> pd.DataFrame:
        if not hasattr(self, '__html'):
            url = "http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A%s&cID=&MenuYn=Y&ReportGB=D&NewMenuID=Y&stkGb=701"
            self.__setattr__('__html', pd.read_html(url % self.ticker, header=0))
        return self.__getattribute__('__html')

    @property
    def summary(self) -> str:
        return self._set_('__summary', getSummary)

    @property
    def products_all(self) -> pd.DataFrame:
        return self._set_('__products1', getAllProducts)

    @property
    def products_recent(self) -> pd.DataFrame:
        return self._set_('__products2', getRecentProducts, products=self.products_all)

    @property
    def statement(self) -> pd.DataFrame:
        return self._set_('__statement', getStatement, html=self._html, kind=self.by)

    @property
    def asset(self) -> pd.DataFrame:
        asset = self.statement[['자산총계', '부채총계', '자본총계']].dropna().astype(int).copy()
        for col in asset.columns:
            asset[f'{col}LB'] = asset[col].apply(lambda x: f'{x}억원' if x < 10000 else f'{str(x)[:-4]}조 {str(x)[-4:]}억원')
        return asset

    @property
    def profit(self) -> pd.DataFrame:
        key = [_ for _ in ['매출액', '순영업수익', '이자수익', '보험료수익'] if _ in self.statement.columns][0]
        profit = self.statement[[key, '영업이익', '당기순이익']].dropna().astype(int)
        for col in [key, '영업이익', '당기순이익']:
            profit[f'{col}LB'] = profit[col].apply(lambda x: f'{x}억원' if x < 10000 else f'{str(x)[:-4]}조 {str(x)[-4:]}억원')
        return profit

    @property
    def expenses(self) -> pd.DataFrame:
        return self._set_('__expenses', getExpenses)

    @property
    def foreigner(self) -> pd.DataFrame:
        return self._set_('__foreigner', getForeigner)

    @property
    def consensus(self) -> pd.DataFrame:
        return self._set_('__consensus', getConsensus)

    @property
    def multiples(self) -> pd.DataFrame:
        return self._set_('__multiples', getNps)

    @property
    def benchmark_return(self) -> pd.DataFrame:
        return self._set_('__benchmark1', getBenchmarkReturn)

    @property
    def benchmark_multiple(self) -> pd.DataFrame:
        return self._set_('__benchmark2', getBenchmarkMultiple)

    @property
    def multi_factor(self) -> pd.DataFrame:
        return self._set_('__multifactor', getMultifactor)

    @property
    def multiple_series(self) -> pd.DataFrame:
        return self._set_('__multiple1', getMultipleSeries)

    @property
    def multiple_band(self) -> pd.DataFrame:
        return self._set_('__multiple2', getMultipleBand)

    @property
    def short_sell(self) -> pd.DataFrame:
        return self._set_('__short1', getShortSell)

    @property
    def short_balance(self) -> pd.DataFrame:
        return self._set_('__short2', getShortBalance)


if __name__ == '__main__':
    ticker = '316140'
    tester = fnguide(ticker=ticker)
    # print(tester.summary)
    # print(tester.products_all)
    # print(tester.products_recent)
    print(tester.statement)
    print(tester.asset)
    print(tester.profit)
    # print(tester.Expenses)
    # print(tester.Foreigner)
    # print(tester.Consensus)
    # print(tester.Nps)
    # print(tester.BenchmarkReturn)
    # print(tester.BenchmarkMultiple)
    # print(tester.Multifactor)
    # print(tester.MultipleSeries)
    # print(tester.MultipleBand)
    # print(tester.ShortSell)
    # print(tester.ShortBalance)
