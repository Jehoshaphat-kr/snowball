from snowball.timeseries import TimeSeries
from snowball.fundamental._view import (
    _summary,
    _statement,
    _marketcap,
    _product,
    _expenses,
    _consensus,
    _foreigner,
    _multiple,
    _benchmark,
    _factors,
    _short
)
import os


class KrseStock(TimeSeries):

    def __init__(self, ticker:str):
        super().__init__(ticker=ticker)
        self.__p = os.path.join(os.path.join(os.environ['USERPROFILE']), rf'Desktop/snob/{self.ticker} {self.name}')
        if not os.path.isdir(self.__p):
            os.makedirs(self.__p)

        '''
        Abstract
        1) Attributes
          - text: source text
        2) Method
          - N/A
        3) Call
          - print(text)
        '''
        self.summary = _summary(self)

        '''
        Statement
        1) Attributes
          - by: 'annual' or 'quarter'
        '''
        self.statement = _statement(self)

        '''
        Market-Cap
        1) Attributes
          - df: source dataframe
        2) Method
          - 
        '''
        self.marketcap = _marketcap(self)

        '''
        Products
        1) Attributes
          - df: source dataframe
        2) Method
          - yearly(mode:str)
          - recent(mode:str)
        '''
        self.products = _product(self)


        '''
        Expenses
        1) Attributes
          - df: source datatframe
        '''
        self.expenses = _expenses(self)

        '''
        Consensus
        1) Attributes
          - df: source dataframe
        2) Method
          - __call__: default consensus status
        '''
        self.consensus = _consensus(self)

        '''
        Foreigner
        1) Attributes
          - df: source dataframe
        2) Method
          - __call__: default foreigner status with 3M / 1Y / 3Y optional
        '''
        self.foreigner = _foreigner(self)

        '''
        Multiples (Time-series)
        1) Attributes
          - df: source dataframe
        2) Method
          - __call__: default multiples status
        '''
        self.multiples = _multiple(self)

        '''
        Benchmark
        1) Attributes
          - df: source dataframe
        2) Method
          - __call__: default benchmark series
        '''
        self.benchmark = _benchmark(self)

        '''
        Factors
        1) Attributes
          - df: source dataframe (tuple)
        2) Method
          - __call__: default factor subplots
        '''
        self.factors = _factors(self)

        '''
        Short
        1) Attributes
          - df: source dataframe
        2) Method
          - __call__: default short plot
        '''
        self.short = _short(self)
        return

    @property
    def path(self) -> str:
        return self.__p

    @path.setter
    def path(self, path:str):
        if not os.path.isdir(path):
            os.makedirs(path)
        self.__p = path


if __name__ == "__main__":

    # tester.SUPPLY.show()
    # tester.MULTIFACTOR.show()

    # t = '316140' # Woori
    # t = '017670' # SK Telecom
    t = '000720'
    stock = KrseStock(ticker=t)
    # stock.path = rf'\\kefico\keti\ENT\Softroom\Temp\J.H.Lee\snob\{stock.ticker} {stock.name}'

    # stock.summary('show')
    # stock.statement('save')
    # stock.statement.asset('save')
    # stock.statement.profit('save')
    # stock.statement.rates('save')
    # stock.marketcap('save')
    # stock.products('save')
    # stock.products.yearly('show')
    # stock.products.recent('show')
    # stock.expenses('save')
    # stock.consensus('save')
    # stock.foreigner('save')
    # stock.multiples('save')
    # stock.benchmark('save')
    # stock.factors('show')
    stock.short('show')

    # print(stock.short.df)

