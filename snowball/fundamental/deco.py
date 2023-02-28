from plotly.subplots import make_subplots
from snowball.define import colors
from snowball.fundamental.fetch import (
    get_summary,
    get_statement,
    get_asset,
    get_profit,
    get_market_cap,
    get_products,
    get_products_recent,
    get_expenses,
    get_consensus,
    get_foreign_rate,
    get_nps,
    get_multiple_series,
    get_multiple_band,
    get_multi_factor,
    get_benchmark_return,
    get_benchmark_multiple,
    get_short_sell,
    get_short_balance
)
import plotly.graph_objects as go
import pandas as pd


def _call_validator(x:str):
    if not x in ['show', 'source', 'figure', 'trace']:
        raise KeyError
    return


class _summary(object):
    def __init__(self, ticker:str):
        self._t = ticker
    def __call__(self, call:str = 'show'):
        _call_validator(call)
        if call == 'show':
            print(self.text)
            return
        return self.text
    @property
    def text(self) -> str:
        if not hasattr(self, '__load'):
            self.__setattr__('__load', get_summary(self._t))
        return self.__getattribute__('__load')


class _state(object):
    __by = 'annual'
    def __init__(self, ticker:str):
        self._t = ticker
    def __call__(self, call:str = 'source'):
        _call_validator(call)
        if call == 'show':
            print(self.df)
            return
        return self.df
    @property
    def by(self) -> str:
        return self.__by
    @by.setter
    def by(self, by:str):
        self.__by = by.lower()
    @property
    def df(self) -> pd.DataFrame:
        if not hasattr(self, f'__{self.by}'):
            self.__setattr__(f'__{self.by}', get_statement(self._t, by=self.by))
        return self.__getattribute__(f'__{self.by}')


class _asset(object):
    def __init__(self, ticker:str, name:str, stat:_state):
        self._t, self._n, self._s = ticker, name, stat
    def __call__(self, call:str='figure'):
        _call_validator(call)
        if call in ['figure', 'show']:
            fig = go.Figure(data=self.traces, layout=self.layout)
            if call == 'figure':
                return fig
            else:
                fig.show()
                return
        elif call.startswith('trace'):
            return self.traces
        else:
            return self.df
    @property
    def df(self) -> pd.DataFrame:
        if not hasattr(self, '__load'):
            self.__setattr__('__load', get_asset(self._s.df))
        return self.__getattribute__('__load')
    @property
    def traces(self) -> list:
        traces = [
            (go.Bar if n else go.Scatter)(
                name=c,
                x=self.df.index,
                y=self.df[c],
                showlegend=True if n else False,
                visible=True,
                opacity=0.9 if n else 1.0,
                meta=round(100 * self.df[c] / self.df.자산총계, 2) if n else None,
                text=self.df[f"{c}LB"],
                texttemplate="%{text}<br>(%{meta}%)" if n else "총 자산: %{text}",
                textposition="inside" if n else "top center",
                hoverinfo="all" if n else "skip",
                hovertemplate=c[:2] + ': %{y}%<extra></extra>' if n else None
            ) for n, c in enumerate(['자산총계', '부채총계', '자본총계'])
        ]
        traces[0].mode='text'
        return traces
    @property
    def layout(self) -> go.Layout:
        return go.Layout(
            title=f"<b>{self._n}({self._t})</b> Asset",
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
                title='자산 [억원]',
                showgrid=True,
                gridcolor='lightgrey',
                zeroline=True,
                zerolinecolor='lightgrey'
            ),
        )


class _profit(object):
    def __init__(self, ticker:str, name:str, stat:_state):
        self._t, self._n, self._s = ticker, name, stat
    def __call__(self, call: str = 'figure'):
        _call_validator(call)
        if call in ['figure', 'show']:
            fig = go.Figure(data=self.traces, layout=self.layout)
            if call == 'figure':
                return fig
            else:
                fig.show()
                return
        elif call.startswith('trace'):
            return self.traces
        else:
            return self.df
    @property
    def df(self) -> pd.DataFrame:
        if not hasattr(self, '__df'):
            self.__setattr__('__df', get_profit(self._s.df))
        return self.__getattribute__('__df')
    @property
    def traces(self) -> list:
        return [
            go.Bar(
                name=c,
                x=self.df.index,
                y=self.df[c],
                showlegend=True,
                visible=True,
                opacity=0.9,
                marker=dict(color=colors[n]),
                text=self.df[f"{c}LB"],
                textposition="inside",
                texttemplate="%{text}",
                hovertemplate=c + ": %{text}<extra></extra>"
            ) for n, c in enumerate(self.df.columns) if not c.endswith('LB')
        ]
    @property
    def layout(self) -> go.Layout:
        return go.Layout(
            title=f"<b>{self._n}({self._t})</b> Profit",
            plot_bgcolor='white',
            barmode='group',
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
            ),
        )


class _marketcap(object):
    def __init__(self, ticker:str, name:str, date:str):
        self._t, self._n, self._d = ticker, name, date
    def __call__(self, call: str = 'figure'):
        _call_validator(call)
        if call in ['figure', 'show']:
            fig = go.Figure(data=self.traces, layout=self.layout)
            if call == 'figure':
                return fig
            else:
                fig.show()
                return
        elif call.startswith('trace'):
            return self.traces
        else:
            return self.df
    @property
    def df(self) -> pd.DataFrame:
        if not hasattr(self, '__df'):
            self.__setattr__('__df', get_market_cap(self._t, self._d))
        return self.__getattribute__('__df')
    @property
    def traces(self) -> list:
        return [
            go.Bar(
                name='시가총액',
                x=self.df.index,
                y=self.df.시가총액,
                showlegend=True,
                visible=True,
                text=self.df.시가총액LB,
                textposition="inside",
                texttemplate="%{text}",
                hovertemplate="%{x}<br>%{text}<extra></extra>"
            )
        ]
    @property
    def layout(self) -> go.Layout:
        return go.Layout(
            title=f"<b>{self._n}({self._t})</b> Market-Cap",
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


class _product(object):
    def __init__(self, ticker:str, name:str):
        self._t, self._n = ticker, name
    def __call__(self, call: str = 'figure', mode:str='bars'):
        _call_validator(call)
        if mode == 'bars':
            layout = self.layout
            data = self.traces
        elif mode == 'pie':
            layout = self.layout
            layout.xaxis = None
            layout.yaxis = None
            data = self.pie
        else:
            raise KeyError

        if call in ['figure', 'show']:
            fig = go.Figure(data=data, layout=layout)
            if call == 'figure':
                return fig
            else:
                fig.show()
                return
        elif call.startswith('trace'):
            return data
        else:
            return self.df
    @property
    def df(self) -> pd.DataFrame:
        if not hasattr(self, '__df'):
            self.__setattr__('__df', get_products(self._t))
        return self.__getattribute__('__df')
    @property
    def traces(self) -> list:
        return [
            go.Bar(
                name=f"{c}",
                x=self.df.index,
                y=self.df[c],
                showlegend=True,
                legendgroup=c,
                visible=True,
                marker=dict(color=colors[n]),
                opacity=0.9,
                textposition="inside",
                texttemplate=c + "<br>%{y:.2f}%",
                hovertemplate=c + "<br>%{y:.2f}%<extra></extra>"
            ) for n, c in enumerate(self.df.columns)
        ]
    @property
    def pie(self) -> list:
        df = get_products_recent(self._t, self.df)
        return [
            go.Pie(
                labels=df.index,
                values=df,
                showlegend=True,
                visible=True,
                automargin=True,
                opacity=0.9,
                textfont=dict(color='white'),
                textinfo='label+percent',
                insidetextorientation='radial',
                hoverinfo='label+percent',
            )
        ]

    @property
    def layout(self) -> go.Layout:
        return go.Layout(
            title=f"<b>{self._n}({self._t})</b> Products",
            plot_bgcolor='white',
            barmode='stack',
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
                title='비율 [%]',
                showgrid=True,
                gridcolor='lightgrey',
                zeroline=True,
                zerolinecolor='lightgrey'
            ),
        )


class _expenses(object):
    def __init__(self, ticker:str, name:str, stat:_state):
        self._t, self._n, self._s = ticker, name, stat
    def __call__(self, call: str = 'figure'):
        _call_validator(call)
        if call in ['figure', 'show']:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=["Profit Rate", "Sales Cost Rate", "Sales and Management Cost Rate", "R&D Investment Rate"],
                x_title="기말",
                y_title="[%]",
            ).add_traces(data=self.traces, rows=[1, 1, 2, 2], cols=[1, 2, 1, 2])
            fig.update_layout(self.layout)
            fig.update_yaxes(dict(showgrid=True, gridcolor='lightgrey'))
            if call == 'figure':
                return fig
            else:
                fig.show()
                return
        elif call.startswith('trace'):
            return self.traces
        else:
            return self.df
    @property
    def df(self) -> pd.DataFrame:
        if not hasattr(self, '__df'):
            self.__setattr__('__df', get_expenses(self._t))
        return self.__getattribute__('__df')
    @property
    def traces(self) -> list:
        return [
            go.Scatter(
                name=c,
                x=(self.df if n else self._s.df).index,
                y=(self.df[c].dropna() if n else self._s.df[c]).astype(float),
                showlegend=True,
                visible=True,
                mode='lines+markers+text',
                textposition="top center",
                texttemplate="%{y:.2f}%",
                hovertemplate='%{x}: %{y:.2f}%<extra></extra>'
            ) for n, c in enumerate(("영업이익률", "매출원가율", "판관비율", "R&D투자비중"))
        ]
    @property
    def layout(self) -> dict:
        return dict(
            title=f"<b>{self._n}({self._t})</b> Profit Rate and Expenses",
            plot_bgcolor='white',
            legend=dict(
                orientation="h",
                xanchor="right",
                yanchor="bottom",
                x=1,
                y=1.04
            ),
        )


class _consensus(object):
    def __init__(self, ticker:str, name:str):
        self._t, self._n = ticker, name

    def __call__(self, call: str = 'figure'):
        _call_validator(call)
        if call in ['figure', 'show']:
            fig = go.Figure(data=self.traces, layout=self.layout)
            if call == 'figure':
                return fig
            else:
                fig.show()
                return
        elif call.startswith('trace'):
            return self.traces
        else:
            return self.df
    @property
    def df(self) -> pd.DataFrame:
        if not hasattr(self, '__df'):
            self.__setattr__('__df', get_consensus(self._t))
        return self.__getattribute__('__df')
    @property
    def traces(self) -> list:
        return [
            go.Scatter(
                name=c,
                x=self.df.index,
                y=self.df[c],
                showlegend=True,
                visible=True,
                mode='lines',
                line=dict(color=colors[n] if n else 'black', dash=None if n else 'dot'),
                xhoverformat='%Y/%m/%d',
                yhoverformat=',d',
                hovertemplate="%{y}원<extra></extra>"
            ) for n, c in enumerate(("목표주가", "종가"))
        ]
    @property
    def layout(self) -> go.Layout:
        return go.Layout(
            title=f"<b>{self._n}({self._t})</b> Consensus",
            plot_bgcolor='white',
            legend=dict(
                orientation="h",
                xanchor="right",
                yanchor="bottom",
                x=1,
                y=1.04
            ),
            hovermode="x unified",
            xaxis=dict(
                title='날짜',
                showticklabels=True,
                showgrid=True,
                gridcolor='lightgrey',
            ),
            yaxis=dict(
                title='[원]',
                showgrid=True,
                gridcolor='lightgrey',
            )
        )

class _foreigner(object):
    def __init__(self, ticker:str, name:str):
        self._t, self._n, self._m = ticker, name, 'plot'
    def __call__(self, call: str = 'figure', mode: str='plot'):
        _call_validator(call)
        self._m = mode
        if call in ['figure', 'show']:
            fig = make_subplots(
                rows=1 if mode == 'plot' else 3, cols=1,
                x_title='날짜',
                subplot_titles=None if mode == 'plot' else ['3M', '1Y', '3Y'],
                vertical_spacing=None if mode == 'plot' else 0.08,
                specs=[
                    [{'secondary_y': True}]
                ] if mode == 'plot' else [
                    [{"secondary_y": True}],
                    [{"secondary_y": True}],
                    [{"secondary_y": True}]
                ]
            )
            fig.add_traces(
                data=self.traces,
                rows=[1, 1, 1, 1, 1, 1] if mode == 'plot' else [1, 1, 2, 2, 3, 3],
                cols=[1, 1, 1, 1, 1, 1],
                secondary_ys=[False, True, False, True, False, True]
            )
            fig.update_layout(self.layout)
            return fig if call == 'figure' else fig.show()
        elif call.startswith('trace'):
            return self.traces
        else:
            return self.df
    @property
    def df(self) -> pd.DataFrame:
        if not hasattr(self, '__df'):
            self.__setattr__('__df', get_foreign_rate(self._t))
        return self.__getattribute__('__df')
    @property
    def traces(self):
        return [
            go.Scatter(
                name=t if self._m == 'plot' else c,
                x=self.df[t][c].dropna().index,
                y=self.df[t][c].dropna(),
                showlegend=True if (self._m == 'plot' and '종가' in c) or (not self._m == 'plot' and t == '3M') else False,
                legendgroup=t if self._m == 'plot' else c,
                visible=True if (not self._m == 'plot') or (self._m == 'plot' and t == '3M') else 'legendonly',
                mode='lines',
                line=dict(color='black' if '종가' in c else colors[0], dash='dot' if '종가' in c else None),
                xhoverformat="%Y/%m/%d",
                yhoverformat=',d' if '종가' in c else '.2f',
                hovertemplate='%{y}' + ('원' if '종가' in c else '%') + '<extra></extra>'
            ) for t, c in self.df.columns
        ]
    @property
    def layout(self):
        return dict(
            title=f"<b>{self._n}({self._t})</b> Foreign Rate",
            plot_bgcolor='white',
            legend=dict(
                orientation="h",
                xanchor="right",
                yanchor="bottom",
                x=1,
                y=1.04
            ),
            hovermode="x unified",
            xaxis=dict(
                tickformat="%Y/%m/%d",
                showticklabels=True,
                showgrid=True,
                gridcolor='lightgrey',
            ),
            xaxis2=dict(
                tickformat="%Y/%m/%d",
                showticklabels=True,
                showgrid=True,
                gridcolor='lightgrey',
            ),
            xaxis3=dict(
                tickformat="%Y/%m/%d",
                showticklabels=True,
                showgrid=True,
                gridcolor='lightgrey',
            ),
            yaxis=dict(
                title='[원]',
                showgrid=True,
                gridcolor='lightgrey',
            ),
            yaxis2=dict(
                title='[%]'
            ),
            yaxis3=dict(
                title='[원]',
                showgrid=True,
                gridcolor='lightgrey',
            ),
            yaxis4=dict(
                title='[%]'
            ),
            yaxis5=dict(
                title='[원]',
                showgrid=True,
                gridcolor='lightgrey',
            ),
            yaxis6=dict(
                title='[%]'
            )
        )

class _multiple(object):
    label = [
        "per", "pbr", "div", "bps", "eps", "dps",
        "adj_close",
        "per_low", "per_midlow", "per_mid", "per_midhigh", "per_high",
        "pbr_low", "pbr_midlow", "pbr_mid", "pbr_midhigh", "pbr_high"
    ]
    def __init__(self, ticker:str, name:str):
        self._t, self._n = ticker, name
    def __call__(self):
        return
    @property
    def df(self) -> pd.DataFrame:
        if not hasattr(self, '__df'):
            per_bnd, pbr_bnd = get_multiple_band(self._t)
            self.__setattr__('__df', (get_multiple_series(self._t), per_bnd, pbr_bnd))
        return self.__getattribute__('__df')
    def traces(self, select:str='all'):
        df1, df2, df3 = self.df
        traces = [
            go.Scatter(
                name=c,
                x=df1.index,
                y=df1[c],
                showlegend=True,
                legendgroup=c
            ) for c in df1.columns
        ]
