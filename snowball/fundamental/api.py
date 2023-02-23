from snowball.timeseries import TimeSeries
from snowball.fundamental.wrap import (
    _summary,
    _state,
    _asset,
    _product,
    _profit,
    _marketcap,
    _expenses
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



# class _trace(fnguide):
#     @property
#     def SUPPLY(self) -> go.Figure:
#         fig = make_subplots(
#             rows=2, cols=2,
#             subplot_titles=["Consensus", "Foreigner: 3Y", "Foreigner: 1Y", "Foreigner: 3M"],
#             horizontal_spacing=0.08, vertical_spacing=0.08,
#             specs=[
#                 [{}, {'secondary_y':True}],
#                 [{'secondary_y':True}, {'secondary_y':True}]
#             ],
#             x_title="날짜", y_title='종가[원]'
#         )
#         for n, c in enumerate(self.consensus):
#             if c == '투자의견': continue
#             fig.add_trace(
#                 go.Scatter(
#                     name=c,
#                     x=self.consensus.index,
#                     y=self.consensus[c],
#                     showlegend=False if c.endswith('종가') else True,
#                     legendgroup=c,
#                     mode='lines',
#                     line=dict(dash='dot' if c == '종가' else None, color='black' if c == '종가' else self._c[0]),
#                     xhoverformat="%Y/%m/%d",
#                     yhoverformat=",d",
#                     hovertemplate="%{x}<br>" + c + ": %{y}원<extra></extra>"
#                 ), row=1, col=1
#             )
#         for n, c in enumerate(('3Y', '1Y', '3M')):
#             df = self.foreigner[c].dropna()
#             for col in df.columns[::-1]:
#                 trace = go.Scatter(
#                     name=col,
#                     x=df.index,
#                     y=df[col],
#                     showlegend=True if not n else False,
#                     legendgroup=col,
#                     mode='lines',
#                     line=dict(dash='dot' if col == '종가' else None, color='black' if col == '종가' else self._c[1]),
#                     xhoverformat='%Y/%m/%d',
#                     yhoverformat=",d" if col == '종가' else ".2f",
#                     hovertemplate="%{x}<br>" + col + ": %{y}" + ("원" if col == '종가' else '%') + "<extra></extra>"
#                 )
#                 fig.add_trace(
#                     trace, row={0:1, 1:2, 2:2}[n], col={0:2, 1:1, 2:2}[n],
#                     secondary_y=False if col == '종가' else True
#                 )
#         fig.update_layout(dict(
#             title=f"<b>{self.name}({self.ticker})</b> Consensus and Foreign Rate",
#             plot_bgcolor='white',
#             margin=dict(r=0),
#             legend=dict(
#                 orientation="h",
#                 xanchor="right",
#                 yanchor="bottom",
#                 x=1,
#                 y=1.04
#             ),
#         ))
#         fig.update_xaxes(dict(showticklabels=True, tickformat="%Y/%m/%d", showgrid=True, gridcolor="lightgrey"))
#         fig.update_yaxes(dict(showgrid=True, gridcolor='lightgrey'), secondary_y=False)
#         fig.update_yaxes(dict(title='[%]'), secondary_y=True)
#         return fig
#
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
    stock.expenses('show')
