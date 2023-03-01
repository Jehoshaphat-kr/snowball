from snowball.archive.book import symbols
from pykrx.stock import get_index_ticker_name


class label(object):
    """
    Set basic property or attribute of single asset ticker.
    Asset is classified by market:
      1) krse: Korean Stock Exchange
      2) krx : Korean Exchange (Only for KRX index)
      3) ecos: Korean Econimic Statistics System
      4) nyse: New York Stock Exchange
      5) fred: Federal Reserve Economic Data

    Argument "ticker" is automatically recognized by rule and name, unit, data type will be set accordingly.
    """

    def __init__(self, ticker:str, label:str=str()):
        self.ticker = ticker
        self.label = label
        self.market = symbols.locate(symbol=ticker)

    def __call__(self, *args, **kwargs):
        return

    @property
    def name(self) -> str:
       if not hasattr(self, '__name'):
           if self.market == 'krx':
               self.__setattr__('__name', get_index_ticker_name(self.ticker))
           elif self.market == 'krse':
               self.__setattr__('__name', self.kr.loc[self.ticker, 'longName'])
           elif self.market == 'ecos':
               self.__setattr__('__name', self.label)
           else:
               self.__setattr__('__name', self.ticker)
       return self.__getattribute__('__name')

    @name.setter
    def name(self, name:str):
        self.__setattr__('__name', name)

    @property
    def unit(self) -> str:
       if not hasattr(self, '__unit'):
           if self.market == 'krx':
               self.__setattr__('__unit', '-')
           elif self.market == 'krse':
               self.__setattr__('__unit', 'KRW')
           elif self.market == 'us':
               self.__setattr__('__unit', 'USD')
           else:
               self.__setattr__('__unit', '%')
       return self.__getattribute__('__unit')

    @unit.setter
    def unit(self, unit: str):
       self.__setattr__('__unit', unit)