from snowball.archive import label
from snowball.fundamental.fnguide._fetch import get_statement
from snowball.fundamental.fnguide.summary import summary
from snowball.fundamental.fnguide.asset import asset
import pandas as pd


class FnGuide(label):

    def __init__(self, ticker:str):
        super().__init__(ticker=ticker)
        self._t = ticker
        return

    @property
    def summary(self) -> summary:
        return summary(self)

    @property
    def statement(self) -> pd.DataFrame:
        if not hasattr(self, '__stat'):
            self.__setattr__('__stat', get_statement(self._t))
        return self.__getattribute__('__stat')

    @property
    def asset(self) -> asset:
        return asset(self.statement)



if __name__ == "__main__":
    stock = FnGuide(ticker='005930')
    stock.summary()