from snowball.timeseries import TimeSeries
from snowball.fundamental.deprecated import (
    _summary,
    _state,
    _asset,
    _product,
    _profit,
    _marketcap,
    _expenses,
    _consensus,
    _foreigner,
    _multiple
)


class KrseStock(TimeSeries):

    def __init__(self, ticker:str):
        super().__init__(ticker=ticker)

        self.summary = _summary(self.ticker)

        self.statement = _state(self.ticker)

        self.asset = _asset(self.ticker, self.name, self.statement)

        self.profit = _profit(self.ticker, self.name, self.statement)

        self.products = _product(self.ticker, self.name)

        self.marketcap = _marketcap(self.ticker, self.name, self.enddate)

        self.expenses = _expenses(self.ticker, self.name, self.statement)

        self.consensus = _consensus(self.ticker, self.name)

        self.foreigner = _foreigner(self.ticker, self.name)

        self.multiples = _multiple(self.ticker, self.name)



# class _trace(fnguide):
#     @property
#     def MULTIFACTOR(self) -> go.Figure:
#         traces = [
#             go.Scatterpolar(
#                 name=col,
#                 r=self.multi_factor[col].astype(float),
#                 theta=self.multi_factor.index,
#                 fill='toself',
#                 showlegend=True,
#                 visible=True,
#                 hovertemplate=col + '<br>팩터: %{theta}<br>값: %{r}<extra></extra>'
#             ) for n, col in enumerate(self.multi_factor.columns)
#         ]
#         layout = dict(
#             title=f"<b>{self.name}({self.ticker})</b> Multi-Factors",
#             plot_bgcolor='white',
#         )
#         return go.Figure(data=traces, layout=layout)

if __name__ == "__main__":

    # tester.SUPPLY.show()
    # tester.MULTIFACTOR.show()

    # t = '012330'
    t = '017670'
    stock = KrseStock(ticker=t)
    # stock.summary('show')
    # stock.asset('show')
    # stock.profit('show')
    # stock.products('show', 'bars')
    # stock.products('show', 'pie')
    # stock.marketcap('show')
    # stock.expenses('show')
    # stock.consensus('show')
    # stock.foreigner('show')

    print(stock.multiples.df)