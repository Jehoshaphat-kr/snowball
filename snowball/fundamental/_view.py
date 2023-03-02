from datetime import datetime
from plotly.subplots import make_subplots
from plotly.offline.offline import plot
from snowball.archive import label
from snowball.define import colors, int2won
from snowball.fundamental._fetch import (
    get_summary,
    get_statement,
    get_market_cap,
    get_products,
    get_products_recent,
    get_expenses,
    get_consensus,
    get_foreign_rate,
    get_multiple_series,
    get_multiple_band
)
import plotly.graph_objects as go
import pandas as pd
import os


class _summary(object):
    """
    Company Guide :: Summary

    Abstracted company information in Korean
    """
    def __init__(self, parent:label or None):
        self._p = parent

    def __call__(self, call:str = 'show'):
        if call == 'show':
            print(f"{self._p.name}({self._p.ticker})\n{self.text}")
        elif call == 'save':
            with open(os.path.join(getattr(self._p, 'path'), r'summary.txt'), 'w') as f: f.write(self.text)
        else:
            raise KeyError
        return

    @property
    def text(self) -> str:
        return get_summary(self._p.ticker)


class _statement(object):
    """
    Company Guide :: Statement

    Adjusted by 'annual', 'quarter'
    Consisting Indicator:
      - Asset
      - Profit
      - Rates
    """
    def __init__(self, parent:label or None):
        self._p = parent

    def __call__(self, mode:str = 'show'):
        if mode.startswith('fig'):
            return self.asset(mode), self.profit(mode), self.rates(mode)
        self.asset(mode)
        self.profit(mode)
        self.rates(mode)
        return

    @property
    def by(self) -> str:
        if not hasattr(self, '__by'):
            self.__setattr__('__by', 'annual')
        return self.__getattribute__('__by')

    @by.setter
    def by(self, by:str):
        self.__setattr__('__by', by)

    @property
    def df(self) -> pd.DataFrame:
        if not hasattr(self, f'__{self.by}'):
            self.__setattr__(f'__{self.by}', get_statement(self._p.ticker, by=self.by))
        return self.__getattribute__(f'__{self.by}')

    def _text_asset(self, col:str='자산총계'):
        return go.Scatter(
            name=col[:2],
            x=self.df.index,
            y=self.df[col],
            showlegend=False,
            visible=True,
            mode='text',
            opacity=1.0,
            text=self.df[col].apply(int2won),
            texttemplate="%{text}",
            textposition="top center",
            hoverinfo="skip"
        )
    def _bar_asset(self, col:str):
        return go.Bar(
            name=col[:2],
            x=self.df.index,
            y=self.df[col],
            showlegend=True,
            visible=True,
            marker=dict(color='green' if '자본' in col else 'red'),
            opacity=0.9,
            meta=round(100 * self.df[col] / self.df.자산총계, 2),
            text=self.df[col].apply(int2won),
            texttemplate="%{text}<br>(%{meta}%)",
            textposition="inside",
            hovertemplate=col + ": %{text}<br>" + col[:2] + "비율: %{meta}%<extra></extra>"
        )

    def _bar_profit(self, col:str) -> go.Bar:
        return go.Bar(
            name=col,
            x=self.df.index,
            y=self.df[col],
            showlegend=True,
            visible=True,
            opacity=0.9,
            text=self.df[col].apply(int2won),
            textposition="inside",
            texttemplate="%{text}",
            hovertemplate=col + ": %{text}<extra></extra>"
        )

    def _line_rates(self, col:str) -> go.Scatter:
        return go.Scatter(
            name=col,
            x=self.df.index,
            y=self.df[col],
            showlegend=True,
            visible=True,
            mode='lines+markers+text',
            marker=dict(
                symbol='circle',
                size=9
            ),
            line=dict(
                dash='dot'
            ),
            textposition='top center',
            texttemplate="%{y:.2f}%",
            hoverinfo='skip'
        )

    def _call(self, fig:go.Figure or make_subplots, mode:str, filename:str):
        if mode.startswith('fig'):
            return fig
        elif mode.startswith('show'):
            fig.show()
        elif mode.startswith('save'):
            plot(fig, filename=os.path.join(getattr(self._p, 'path'), f"{filename}.html"), auto_open=False)
        else:
            raise KeyError
        return

    def asset(self, mode:str='show'):
        fig = go.Figure(
            data=[
                self._bar_asset('자본총계'),
                self._bar_asset('부채총계'),
                self._text_asset()
            ],
            layout=go.Layout(
                title=f"<b>{self._p.title}</b> Asset",
                plot_bgcolor='white',
                barmode='stack',
                legend=dict(
                    x=0,
                    y=1.0,
                    bgcolor='rgba(255, 255, 255, 0)',
                    bordercolor='rgba(255, 255, 255, 0)'
                ),
                xaxis=dict(
                    title='기말'
                ),
                yaxis=dict(
                    title='[억원]',
                    showgrid=True,
                    gridcolor='lightgrey',
                    zeroline=True,
                    zerolinecolor='lightgrey'
                ),
            )
        )
        self._call(fig=fig, mode=mode, filename='asset')
        return

    def profit(self, mode:str='show'):
        k_sales = [_ for _ in ['매출액', '순영업수익', '이자수익', '보험료수익'] if _ in self.df.columns][0]
        fig = go.Figure(
            data=[
                self._bar_profit(k_sales),
                self._bar_profit("영업이익"),
                self._bar_profit("당기순이익")
            ],
            layout=go.Layout(
                title=f"<b>{self._p.title}</b> Profit",
                plot_bgcolor='white',
                barmode='group',
                legend=dict(
                    x=0,
                    y=1.0,
                    bgcolor='rgba(255, 255, 255, 0)',
                    bordercolor='rgba(255, 255, 255, 0)'
                ),
                xaxis=dict(
                    title='기말'
                ),
                yaxis=dict(
                    title='[억원]',
                    showgrid=True,
                    gridcolor='lightgrey',
                    zeroline=True,
                    zerolinecolor='lightgrey'
                ),
            )
        )
        self._call(fig=fig, mode=mode, filename='profit')
        return

    def rates(self, mode:str='show'):
        fig = make_subplots(
            rows=2, cols=2,
            vertical_spacing=0.1, horizontal_spacing=0.08,
            x_title='기말', y_title='[%]',
            subplot_titles=['Profit Rate', 'Dividend Rate', 'ROE', 'ROA'],
        )
        fig.update_layout(
            title=f"<b>{self._p.title}</b> Rates",
            plot_bgcolor='white',
            legend=dict(
                orientation="h",
                xanchor="right",
                yanchor="bottom",
                x=0.98,
                y=1.02
            ),
        )
        fig.update_yaxes(
            showgrid=True,
            gridcolor='lightgrey',
            zeroline=True,
            zerolinecolor='lightgrey'
        )
        fig.add_traces(
            data=[
                self._line_rates('영업이익률'),
                self._line_rates('배당수익률'),
                self._line_rates('ROE'),
                self._line_rates('ROA')
            ],
            rows=[1, 1, 2, 2],
            cols=[1, 2, 1, 2]
        )
        self._call(fig=fig, mode=mode, filename='rates')
        return


class _marketcap(object):
    """
    Company Guide :: Market-Cap
    """
    def __init__(self, parent:label or None):
        self._p = parent

    def __call__(self, mode:str = 'show'):
        fig = go.Figure(
            data=[self._bar()],
            layout=go.Layout(
                title=f"<b>{self._p.title})</b> Market-Cap",
                plot_bgcolor='white',
                legend=dict(
                    orientation="h",
                    xanchor="right",
                    yanchor="bottom",
                    x=0.96,
                    y=1
                ),
                xaxis=dict(
                    title='기말'
                ),
                yaxis=dict(
                    title='[억원]',
                    showgrid=True,
                    gridcolor='lightgrey',
                    zeroline=True,
                    zerolinecolor='lightgrey'
                )
            )
        )
        if mode.startswith('fig'):
            return fig
        elif mode.startswith('show'):
            fig.show()
        elif mode.startswith('save'):
            plot(fig, filename=os.path.join(getattr(self._p, 'path'), f"marketcap.html"), auto_open=False)
        else:
            raise KeyError
        return

    @property
    def df(self) -> pd.DataFrame:
        if not hasattr(self, f'__src'):
            self.__setattr__(f'__src', get_market_cap(self._p.ticker, datetime.now().strftime("%Y%m%d")))
        return self.__getattribute__(f'__src')

    def _bar(self):
        return go.Bar(
            name='시가총액',
            x=self.df.index,
            y=self.df.시가총액,
            showlegend=True,
            visible=True,
            text=self.df.시가총액.apply(int2won),
            textposition="inside",
            texttemplate='%{text}',
            hovertemplate="%{x}<br>%{text}<extra></extra>"
        )


# class _product(object):
#     def __init__(self, ticker:str, name:str):
#         self._t, self._n = ticker, name
#     def __call__(self, call: str = 'figure', mode:str='bars'):
#         _call_validator(call)
#         if mode == 'bars':
#             layout = self.layout
#             data = self.traces
#         elif mode == 'pie':
#             layout = self.layout
#             layout.xaxis = None
#             layout.yaxis = None
#             data = self.pie
#         else:
#             raise KeyError
#
#         if call in ['figure', 'show']:
#             fig = go.Figure(data=data, layout=layout)
#             if call == 'figure':
#                 return fig
#             else:
#                 fig.show()
#                 return
#         elif call.startswith('trace'):
#             return data
#         else:
#             return self.df
#     @property
#     def df(self) -> pd.DataFrame:
#         if not hasattr(self, '__df'):
#             self.__setattr__('__df', get_products(self._t))
#         return self.__getattribute__('__df')
#     @property
#     def traces(self) -> list:
#         return [
#             go.Bar(
#                 name=f"{c}",
#                 x=self.df.index,
#                 y=self.df[c],
#                 showlegend=True,
#                 legendgroup=c,
#                 visible=True,
#                 marker=dict(color=colors[n]),
#                 opacity=0.9,
#                 textposition="inside",
#                 texttemplate=c + "<br>%{y:.2f}%",
#                 hovertemplate=c + "<br>%{y:.2f}%<extra></extra>"
#             ) for n, c in enumerate(self.df.columns)
#         ]
#     @property
#     def pie(self) -> list:
#         df = get_products_recent(self._t, self.df)
#         return [
#             go.Pie(
#                 labels=df.index,
#                 values=df,
#                 showlegend=True,
#                 visible=True,
#                 automargin=True,
#                 opacity=0.9,
#                 textfont=dict(color='white'),
#                 textinfo='label+percent',
#                 insidetextorientation='radial',
#                 hoverinfo='label+percent',
#             )
#         ]
#
#     @property
#     def layout(self) -> go.Layout:
#         return go.Layout(
#             title=f"<b>{self._n}({self._t})</b> Products",
#             plot_bgcolor='white',
#             barmode='stack',
#             legend=dict(
#                 orientation="h",
#                 xanchor="right",
#                 yanchor="bottom",
#                 x=0.96,
#                 y=1
#             ),
#             xaxis=dict(
#                 title='기말'
#             ),
#             yaxis=dict(
#                 title='비율 [%]',
#                 showgrid=True,
#                 gridcolor='lightgrey',
#                 zeroline=True,
#                 zerolinecolor='lightgrey'
#             ),
#         )
#
#
# class _expenses(object):
#     def __init__(self, ticker:str, name:str, stat:_state):
#         self._t, self._n, self._s = ticker, name, stat
#     def __call__(self, call: str = 'figure'):
#         _call_validator(call)
#         if call in ['figure', 'show']:
#             fig = make_subplots(
#                 rows=2, cols=2,
#                 subplot_titles=["Profit Rate", "Sales Cost Rate", "Sales and Management Cost Rate", "R&D Investment Rate"],
#                 x_title="기말",
#                 y_title="[%]",
#             ).add_traces(data=self.traces, rows=[1, 1, 2, 2], cols=[1, 2, 1, 2])
#             fig.update_layout(self.layout)
#             fig.update_yaxes(dict(showgrid=True, gridcolor='lightgrey'))
#             if call == 'figure':
#                 return fig
#             else:
#                 fig.show()
#                 return
#         elif call.startswith('trace'):
#             return self.traces
#         else:
#             return self.df
#     @property
#     def df(self) -> pd.DataFrame:
#         if not hasattr(self, '__df'):
#             self.__setattr__('__df', get_expenses(self._t))
#         return self.__getattribute__('__df')
#     @property
#     def traces(self) -> list:
#         return [
#             go.Scatter(
#                 name=c,
#                 x=(self.df if n else self._s.df).index,
#                 y=(self.df[c].dropna() if n else self._s.df[c]).astype(float),
#                 showlegend=True,
#                 visible=True,
#                 mode='lines+markers+text',
#                 textposition="top center",
#                 texttemplate="%{y:.2f}%",
#                 hovertemplate='%{x}: %{y:.2f}%<extra></extra>'
#             ) for n, c in enumerate(("영업이익률", "매출원가율", "판관비율", "R&D투자비중"))
#         ]
#     @property
#     def layout(self) -> dict:
#         return dict(
#             title=f"<b>{self._n}({self._t})</b> Profit Rate and Expenses",
#             plot_bgcolor='white',
#             legend=dict(
#                 orientation="h",
#                 xanchor="right",
#                 yanchor="bottom",
#                 x=1,
#                 y=1.04
#             ),
#         )
#
#
# class _consensus(object):
#     def __init__(self, ticker:str, name:str):
#         self._t, self._n = ticker, name
#
#     def __call__(self, call: str = 'figure'):
#         _call_validator(call)
#         if call in ['figure', 'show']:
#             fig = go.Figure(data=self.traces, layout=self.layout)
#             if call == 'figure':
#                 return fig
#             else:
#                 fig.show()
#                 return
#         elif call.startswith('trace'):
#             return self.traces
#         else:
#             return self.df
#     @property
#     def df(self) -> pd.DataFrame:
#         if not hasattr(self, '__df'):
#             self.__setattr__('__df', get_consensus(self._t))
#         return self.__getattribute__('__df')
#     @property
#     def traces(self) -> list:
#         return [
#             go.Scatter(
#                 name=c,
#                 x=self.df.index,
#                 y=self.df[c],
#                 showlegend=True,
#                 visible=True,
#                 mode='lines',
#                 line=dict(color=colors[n] if n else 'black', dash=None if n else 'dot'),
#                 xhoverformat='%Y/%m/%d',
#                 yhoverformat=',d',
#                 hovertemplate="%{y}원<extra></extra>"
#             ) for n, c in enumerate(("목표주가", "종가"))
#         ]
#     @property
#     def layout(self) -> go.Layout:
#         return go.Layout(
#             title=f"<b>{self._n}({self._t})</b> Consensus",
#             plot_bgcolor='white',
#             legend=dict(
#                 orientation="h",
#                 xanchor="right",
#                 yanchor="bottom",
#                 x=1,
#                 y=1.04
#             ),
#             hovermode="x unified",
#             xaxis=dict(
#                 title='날짜',
#                 showticklabels=True,
#                 showgrid=True,
#                 gridcolor='lightgrey',
#             ),
#             yaxis=dict(
#                 title='[원]',
#                 showgrid=True,
#                 gridcolor='lightgrey',
#             )
#         )
#
# class _foreigner(object):
#     def __init__(self, ticker:str, name:str):
#         self._t, self._n, self._m = ticker, name, 'plot'
#     def __call__(self, call: str = 'figure', mode: str='plot'):
#         _call_validator(call)
#         self._m = mode
#         if call in ['figure', 'show']:
#             fig = make_subplots(
#                 rows=1 if mode == 'plot' else 3, cols=1,
#                 x_title='날짜',
#                 subplot_titles=None if mode == 'plot' else ['3M', '1Y', '3Y'],
#                 vertical_spacing=None if mode == 'plot' else 0.08,
#                 specs=[
#                     [{'secondary_y': True}]
#                 ] if mode == 'plot' else [
#                     [{"secondary_y": True}],
#                     [{"secondary_y": True}],
#                     [{"secondary_y": True}]
#                 ]
#             )
#             fig.add_traces(
#                 data=self.traces,
#                 rows=[1, 1, 1, 1, 1, 1] if mode == 'plot' else [1, 1, 2, 2, 3, 3],
#                 cols=[1, 1, 1, 1, 1, 1],
#                 secondary_ys=[False, True, False, True, False, True]
#             )
#             fig.update_layout(self.layout)
#             return fig if call == 'figure' else fig.show()
#         elif call.startswith('trace'):
#             return self.traces
#         else:
#             return self.df
#     @property
#     def df(self) -> pd.DataFrame:
#         if not hasattr(self, '__df'):
#             self.__setattr__('__df', get_foreign_rate(self._t))
#         return self.__getattribute__('__df')
#     @property
#     def traces(self):
#         return [
#             go.Scatter(
#                 name=t if self._m == 'plot' else c,
#                 x=self.df[t][c].dropna().index,
#                 y=self.df[t][c].dropna(),
#                 showlegend=True if (self._m == 'plot' and '종가' in c) or (not self._m == 'plot' and t == '3M') else False,
#                 legendgroup=t if self._m == 'plot' else c,
#                 visible=True if (not self._m == 'plot') or (self._m == 'plot' and t == '3M') else 'legendonly',
#                 mode='lines',
#                 line=dict(color='black' if '종가' in c else colors[0], dash='dot' if '종가' in c else None),
#                 xhoverformat="%Y/%m/%d",
#                 yhoverformat=',d' if '종가' in c else '.2f',
#                 hovertemplate='%{y}' + ('원' if '종가' in c else '%') + '<extra></extra>'
#             ) for t, c in self.df.columns
#         ]
#     @property
#     def layout(self):
#         return dict(
#             title=f"<b>{self._n}({self._t})</b> Foreign Rate",
#             plot_bgcolor='white',
#             legend=dict(
#                 orientation="h",
#                 xanchor="right",
#                 yanchor="bottom",
#                 x=1,
#                 y=1.04
#             ),
#             hovermode="x unified",
#             xaxis=dict(
#                 tickformat="%Y/%m/%d",
#                 showticklabels=True,
#                 showgrid=True,
#                 gridcolor='lightgrey',
#             ),
#             xaxis2=dict(
#                 tickformat="%Y/%m/%d",
#                 showticklabels=True,
#                 showgrid=True,
#                 gridcolor='lightgrey',
#             ),
#             xaxis3=dict(
#                 tickformat="%Y/%m/%d",
#                 showticklabels=True,
#                 showgrid=True,
#                 gridcolor='lightgrey',
#             ),
#             yaxis=dict(
#                 title='[원]',
#                 showgrid=True,
#                 gridcolor='lightgrey',
#             ),
#             yaxis2=dict(
#                 title='[%]'
#             ),
#             yaxis3=dict(
#                 title='[원]',
#                 showgrid=True,
#                 gridcolor='lightgrey',
#             ),
#             yaxis4=dict(
#                 title='[%]'
#             ),
#             yaxis5=dict(
#                 title='[원]',
#                 showgrid=True,
#                 gridcolor='lightgrey',
#             ),
#             yaxis6=dict(
#                 title='[%]'
#             )
#         )
#
# class _multiple(object):
#     label = [
#         "per", "pbr", "div", "bps", "eps", "dps",
#         "adj_close",
#         "per_low", "per_midlow", "per_mid", "per_midhigh", "per_high",
#         "pbr_low", "pbr_midlow", "pbr_mid", "pbr_midhigh", "pbr_high"
#     ]
#     def __init__(self, ticker:str, name:str):
#         self._t, self._n = ticker, name
#     def __call__(self):
#         return
#     @property
#     def df(self) -> pd.DataFrame:
#         if not hasattr(self, '__df'):
#             per_bnd, pbr_bnd = get_multiple_band(self._t)
#             self.__setattr__('__df', (get_multiple_series(self._t), per_bnd, pbr_bnd))
#         return self.__getattribute__('__df')
#     def traces(self, select:str='all'):
#         df1, df2, df3 = self.df
#         traces = [
#             go.Scatter(
#                 name=c,
#                 x=df1.index,
#                 y=df1[c],
#                 showlegend=True,
#                 legendgroup=c
#             ) for c in df1.columns
#         ]
