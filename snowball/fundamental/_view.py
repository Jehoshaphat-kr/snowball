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
    get_multiple_band,
    get_benchmark_return,
    get_multi_factor,
    get_benchmark_multiple,
    get_short_sell,
    get_short_balance
)
import plotly.graph_objects as go
import pandas as pd
import os


def _call(fig: go.Figure or make_subplots or str, mode: str, filedir: str):
    if mode.startswith('fig'):
        return fig
    elif mode.startswith('show'):
        fig.show()
    elif mode.startswith('save'):
        plot(fig, filename=filedir, auto_open=False)
    else:
        raise KeyError
    return


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
            marker=dict(
                color='green' if '자본' in col else 'red'
            ),
            opacity=0.8,
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
        _call(fig=fig, mode=mode, filedir=os.path.join(getattr(self._p, 'path'), f"asset.html"))
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
        _call(fig=fig, mode=mode, filedir=os.path.join(getattr(self._p, 'path'), f"profit.html"))
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
                x=1.0,
                y=1.04
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
        _call(fig=fig, mode=mode, filedir=os.path.join(getattr(self._p, 'path'), f"rates.html"))
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
        return _call(fig=fig, mode=mode, filedir=os.path.join(getattr(self._p, 'path'), f"marketcap.html"))

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
            opacity=0.9,
            text=self.df.시가총액.apply(int2won),
            textposition="inside",
            texttemplate='%{text}',
            hovertemplate="%{x}<br>%{text}<extra></extra>"
        )


class _product(object):
    """
    Company Guide :: Product
    """

    def __init__(self, parent: label or None):
        self._p = parent

    def __call__(self, mode: str = 'show'):
        if mode.startswith('fig'):
            return self.yearly(mode), self.recent(mode)
        self.yearly(mode)
        self.recent(mode)
        return

    @property
    def df(self) -> pd.DataFrame:
        if not hasattr(self, '__df'):
            self.__setattr__('__df', get_products(self._p.ticker))
        return self.__getattribute__('__df')

    def _bar_products(self) -> list:
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

    def _pie_product(self) -> list:
        df = get_products_recent(self._p.ticker, self.df)
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

    def yearly(self, mode: str = 'show'):
        fig = go.Figure(
            data=self._bar_products(),
            layout=go.Layout(
                title=f"<b>{self._p.name}({self._p.ticker})</b> Products",
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
        )
        _call(fig=fig, mode=mode, filedir=os.path.join(getattr(self._p, 'path'), f"products_yy.html"))
        return

    def recent(self, mode: str = 'show'):
        fig = go.Figure(
            data=self._pie_product(),
            layout = go.Layout(
                title=f"<b>{self._p.name}({self._p.ticker})</b> Products",
                plot_bgcolor='white',
                legend=dict(
                    orientation="h",
                    xanchor="right",
                    yanchor="bottom",
                    x=0.96,
                    y=1
                ),
            )
        )
        _call(fig=fig, mode=mode, filedir=os.path.join(getattr(self._p, 'path'), f"products.html"))
        return


class _expenses(object):
    """
    Company Guide :: Expenses
    """

    def __init__(self, parent: label or None):
        self._p = parent

    def __call__(self, mode: str = 'show'):
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=["Profit Rate", "Sales Cost Rate", "Sales and Management Cost Rate", "R&D Investment Rate"],
            x_title="기말",
            y_title="[%]",
        )
        fig.add_traces(
            data=[
                getattr(self._p.statement, '_line_rates')('영업이익률'),
                self._line(col="매출원가율"),
                self._line(col="판관비율"),
                self._line(col="R&D투자비중")
            ],
            rows=[1, 1, 2, 2],
            cols=[1, 2, 1, 2]
        )
        fig.update_layout(
            title=f"<b>{self._p.name}({self._p.ticker})</b> Profit Rate and Expenses",
            plot_bgcolor='white',
            legend=dict(
                orientation="h",
                xanchor="right",
                yanchor="bottom",
                x=1,
                y=1.04
            ),
        )
        fig.update_yaxes(dict(showgrid=True, gridcolor='lightgrey'))
        return _call(fig=fig, mode=mode, filedir=os.path.join(getattr(self._p, 'path'), f"expenses.html"))

    @property
    def df(self) -> pd.DataFrame:
        if not hasattr(self, '__df'):
            self.__setattr__('__df', get_expenses(self._p.ticker))
        return self.__getattribute__('__df')

    def _line(self, col:str):
        return go.Scatter(
            name=col,
            x=self.df.index,
            y=self.df[col].astype(float),
            showlegend=True,
            visible=True,
            mode='lines+markers+text',
            textposition="top center",
            texttemplate="%{y:.2f}%",
            hovertemplate='%{x}: %{y:.2f}%<extra></extra>'
        )


class _consensus(object):
    def __init__(self, parent:label or None):
        self._p = parent

    def __call__(self, mode:str = 'show'):
        fig = go.Figure(
            data=[
                self._line(col='목표주가'),
                self._line(col='종가')
            ],
            layout=go.Layout(
                title=f"<b>{self._p.name}({self._p.ticker})</b> Consensus",
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
        )
        return _call(fig=fig, mode=mode, filedir=os.path.join(getattr(self._p, 'path'), f"consensus.html"))

    @property
    def df(self) -> pd.DataFrame:
        if not hasattr(self, '__df'):
            self.__setattr__('__df', get_consensus(self._p.ticker))
        return self.__getattribute__('__df')

    def _line(self, col:str):
        return go.Scatter(
            name=col,
            x=self.df.index,
            y=self.df[col],
            showlegend=True,
            visible=True,
            mode='lines',
            line=dict(
                color='black' if col.endswith('종가') else colors[1],
                dash='dot' if col.endswith('종가') else None
            ),
            meta=self.df.괴리율 if col.endswith('종가') else None,
            xhoverformat='%Y/%m/%d',
            yhoverformat=',d',
            hovertemplate="%{y}원" + ("(%{meta}%)" if col.endswith('종가') else '') + "<extra></extra>"
        )


class _foreigner(object):
    def __init__(self, parent:label or None):
        self._p = parent

    def __call__(self, mode:str='show'):
        fig = make_subplots(
            rows=1, cols=1,
            x_title='날짜',
            specs=[
                [{'secondary_y': True}]
            ]
        )
        fig.add_traces(
            data=[self._line(c1, c2) for c1, c2 in self.df.columns],
            rows=[1, 1, 1, 1, 1, 1],
            cols=[1, 1, 1, 1, 1, 1],
            secondary_ys=[False, True, False, True, False, True]
        )
        fig.update_layout(
            title=f"<b>{self._p.name}({self._p.ticker})</b> Foreign Rate",
            plot_bgcolor='white',
            margin=dict(r=0),
            legend=dict(
                orientation="h",
                xanchor="right",
                yanchor="bottom",
                x=0.96,
                y=1
            ),
            hovermode="x unified",
            xaxis=dict(
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
            updatemenus=[
                dict(
                    type="buttons",
                    direction="right",
                    active=0,
                    xanchor='left', x=0.0,
                    yanchor='bottom', y=1.0,
                    buttons=list([
                        dict(
                            label="3개월",
                            method="update",
                            args=[{"visible": [True, True, False, False, False, False]}]
                        ),
                        dict(
                            label="1년",
                            method="update",
                            args=[{"visible": [False, False,True, True, False, False]}]
                        ),
                        dict(
                            label="3년",
                            method="update",
                            args=[{"visible": [False, False, False, False, True, True]}]
                        ),
                    ]),
                )
            ]

        )
        return _call(fig=fig, mode=mode, filedir=os.path.join(getattr(self._p, 'path'), f"foreigner.html"))

    @property
    def df(self) -> pd.DataFrame:
        if not hasattr(self, '__df'):
            self.__setattr__('__df', get_foreign_rate(self._p.ticker))
        return self.__getattribute__('__df')

    def _line(self, c1:str, c2:str):
        return go.Scatter(
            name=c2,
            x=self.df[c1][c2].dropna().index,
            y=self.df[c1][c2].dropna(),
            showlegend=True,
            visible=True if c1 == '3M' else False,
            mode='lines',
            line=dict(color='black' if '종가' in c2 else colors[0], dash='dot' if '종가' in c2 else None),
            xhoverformat="%Y/%m/%d",
            yhoverformat=',d' if '종가' in c2 else '.2f',
            hovertemplate='%{y}' + ('원' if '종가' in c2 else '%') + '<extra></extra>'
        )


class _multiple(object):
    def __init__(self, parent:label or None):
        self._p = parent
        return

    def __call__(self, mode:str='show'):
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=["PER & EPS", "PBR & BPS", "PER Band", "PBR Band"],
            x_title="날짜",
            vertical_spacing=0.1, horizontal_spacing=0.08,
            specs=[
                [{'secondary_y': True}, {'secondary_y': True}],
                [{'secondary_y': False}, {'secondary_y': False}]
            ]
        )
        fig.add_traces(
            data=[
                self._line('multiple', 'PER'), self._line('multiple', 'EPS'),
                self._line('multiple', 'PBR'), self._line('multiple', 'BPS'),
            ] + self._line_bands('per_band') + self._line_bands('pbr_band'),
            rows=[1, 1, 1, 1] + [2] * 12,
            cols=[1, 1, 2, 2] + [1] * 6 + [2] * 6,
            secondary_ys=[False, True, False, True] + [False] * 12
        )
        fig.update_layout(
            title=f"<b>{self._p.name}({self._p.ticker})</b> Multiples",
            plot_bgcolor='white',
            margin=dict(r=0),
            legend=dict(
                orientation="h",
                xanchor="right",
                yanchor="bottom",
                x=0.98,
                y=1.02
            ),
        )
        fig.update_xaxes(
            tickformat="%Y/%m/%d",
            showticklabels=True,
            showgrid=True,
            gridcolor='lightgrey',
        )
        fig.update_yaxes(
            showgrid=True,
            gridcolor='lightgrey',
        )
        return _call(fig=fig, mode=mode, filedir=os.path.join(getattr(self._p, 'path'), f"multiples.html"))

    @property
    def df(self) -> pd.DataFrame:
        if not hasattr(self, '__df'):
            per_bnd, pbr_bnd = get_multiple_band(self._p.ticker)
            df = pd.concat(
                objs=dict(
                    multiple=get_multiple_series(self._p.ticker),
                    per_band=per_bnd,
                    pbr_band=pbr_bnd
                ),
                axis=1
            )
            self.__setattr__('__df', df)
        return self.__getattribute__('__df')

    def _line(self, c1:str, c2:str):
        df = self.df[c1][c2].dropna()
        cd = c2.endswith('가') or c2 == 'EPS' or c2 == 'BPS'
        nm = '종가' if c2.endswith('가') else c2
        if c2.endswith('가'):
            p = self._p.ohlcv.종가
            df = p[p.index > df.index[0]]
        return go.Scatter(
            name=nm,
            x=df.index,
            y=df,
            showlegend=False if c2.endswith('가') or ('X' in c2) else True,
            mode='lines',
            line=dict(
                color='black' if c2.endswith('가') else None,
                dash='dot' if c2.endswith('가') else None
            ),
            xhoverformat='%Y/%m/%d',
            yhoverformat=',d' if cd else '.2f',
            hovertemplate=nm + '<br>%{x}<br>%{y}' + f'{"원" if cd else ""}<extra></extra>'
        )

    def _line_bands(self, col:str):
        return [self._line(col, c) for c in self.df[col].columns]


class _benchmark(object):
    def __init__(self, parent:label or None):
        self._p = parent
        return

    def __call__(self, mode:str = 'show'):
        fig = go.Figure(
            data=[self._line(c1, c2) for c1, c2 in self.df.columns],
            layout=go.Layout(
                title=f"<b>{self._p.name}({self._p.ticker})</b> Benchmark",
                plot_bgcolor='white',
                legend=dict(
                    orientation="h",
                    xanchor="right",
                    yanchor="bottom",
                    x=1,
                    y=1
                ),
                hovermode="x unified",
                xaxis=dict(
                    title='날짜',
                    tickformat="%Y/%m/%d",
                    showticklabels=True,
                    showgrid=True,
                    gridcolor='lightgrey',
                ),
                yaxis=dict(
                    title='[%]',
                    showgrid=True,
                    gridcolor='lightgrey',
                ),
                updatemenus=[
                    dict(
                        type="buttons",
                        direction="right",
                        active=0,
                        x=0.1, y=1.0,
                        buttons=list([
                            dict(
                                label="3개월",
                                method="update",
                                args=[{"visible": [True, True, True, False, False, False, False, False, False]}]
                            ),
                            dict(
                                label="1년",
                                method="update",
                                args=[{"visible": [False, False, False, True, True, True, False, False, False]}]
                            ),
                            dict(
                                label="3년",
                                method="update",
                                args=[{"visible": [False, False, False, False, False, False, True, True, True]}]
                            ),
                        ]),
                    )
                ]
            )
        )
        return _call(fig=fig, mode=mode, filedir=os.path.join(getattr(self._p, 'path'), f"benchmark.html"))

    @property
    def df(self) -> pd.DataFrame:
        if not hasattr(self, '__df'):
            self.__setattr__('__df', get_benchmark_return(self._p.ticker))
        return self.__getattribute__('__df')

    def _line(self, c1:str, c2:str):
        ky = self.df[c1].columns[0]
        df = self.df[c1][c2].dropna()
        return go.Scatter(
            name=c2,
            x=df.index,
            y=df,
            showlegend=True,
            visible=True if c1 == '3M' else False,
            mode='lines',
            line=dict(
                color='black' if c2 == ky else None,
                dash='dot' if c2 == ky else None
            ),
            xhoverformat='%Y/%m/%d',
            yhoverformat='.2f',
            hovertemplate='%{y}%<extra></extra>'
        )


class _factors(object):
    def __init__(self, parent:label or None):
        self._p = parent
        return

    def __call__(self, mode:str='show'):
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[None, 'PER', 'EV/EBITDA', 'ROE'],
            x_title='기말',
            horizontal_spacing=0.08, vertical_spacing=0.1,
            specs=[
                [{'type':'polar'}, {'type':'bar'}],
                [{'type':'bar'}, {'type':'bar'}]
            ],
        )
        fig.add_traces(
            data=[self._polar(c) for c in self.df[0].columns] + [self._bar(c1, c2) for c1, c2 in self.df[1].columns],
            rows=[1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2],
            cols=[1, 1, 2, 2, 2, 1, 1, 1, 2, 2, 2]
        )
        fig.update_layout(
            title=f"<b>{self._p.name}({self._p.ticker})</b> Factors",
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
        )
        return _call(fig=fig, mode=mode, filedir=os.path.join(getattr(self._p, 'path'), f"benchmark.html"))

    @property
    def df(self):
        if not hasattr(self, '__df'):
            dff, dfm = get_multi_factor(self._p.ticker), get_benchmark_multiple(self._p.ticker)
            self.__setattr__('__df', (dff, dfm))
        return self.__getattribute__('__df')

    def _polar(self, col:str) -> go.Scatterpolar or None:
        df, _ = self.df
        return go.Scatterpolar(
            name=col,
            r=df[col].astype(float),
            theta=df.index,
            fill='toself',
            showlegend=True,
            visible=True,
            hovertemplate=col + '<br>%{theta} : %{r}<extra></extra>'
        )

    def _bar(self, c1:str, c2:str) -> go.Bar or None:
        _, df = self.df
        n = df.columns.tolist().index((c1, c2)) % 3
        return go.Bar(
            name=c2,
            x=df.index,
            y=df[c1][c2],
            showlegend=True if c1 == 'PER' else False,
            legendgroup=c2,
            visible=True,
            marker=dict(color=colors[n]),
            opacity=0.9,
            text=df[c1][c2],
            textposition='inside',
            texttemplate='%{text}' + '%' if c1 == 'ROE' else '',
            hovertemplate=f'{c2}<br>{c1}' + ': %{y}' + f'{"%" if c1 == "ROE" else ""}<extra></extra>'
        )


class _short(object):
    def __init__(self, parent:label or None):
        self._p = parent
        return

    def __call__(self, mode:str='show'):
        fig = make_subplots(
            rows=1, cols=1,
            specs=[[{'secondary_y': True}]]
        )
        fig.add_traces(
            data=[self._line(c) for c in self.df.columns],
            rows=[1,1,1], cols=[1,1,1],
            secondary_ys=[True, True, False]
        )
        fig.update_layout(
            title=f"<b>{self._p.name}({self._p.ticker})</b> Short",
            plot_bgcolor='white',
            legend=dict(
                orientation="h",
                xanchor="right",
                yanchor="bottom",
                x=1,
                y=1
            ),
            hovermode="x unified",
            xaxis=dict(
                title='날짜',
                tickformat="%Y/%m/%d",
                showticklabels=True,
                showgrid=True,
                gridcolor='lightgrey',
            ),
            yaxis=dict(
                title='[KRW]',
                showgrid=True,
                gridcolor='lightgrey'
            ),
            yaxis2=dict(
                title='[%]',
            ),
        )
        return _call(fig=fig, mode=mode, filedir=os.path.join(getattr(self._p, 'path'), f"short.html"))

    @property
    def df(self) -> pd.DataFrame:
        if not hasattr(self, '__df'):
            short = get_short_sell(self._p.ticker)
            balance = get_short_balance(self._p.ticker)
            ohlcv = self._p.ohlcv[self._p.ohlcv.index >= short.index[0]].copy()
            df = ohlcv.join(short.차입공매도비중, how='left').join(balance.대차잔고비중, how='left')
            self.__setattr__('__df', df[['차입공매도비중', '대차잔고비중', '종가']])
        return self.__getattribute__('__df')

    def _line(self, col:str):
        df = self.df[col].dropna().copy()
        return go.Scatter(
            name=col,
            x=df.index,
            y=df,
            showlegend=True,
            visible='legendonly' if '차입공매도' in col else True,
            mode='lines',
            line=dict(
                color='black' if col == '종가' else 'red' if '대차' in col else 'royalblue',
                dash='dot' if col == '종가' else None
            ),
            xhoverformat='%Y/%m/%d',
            yhoverformat=',d' if col == '종가' else '.2f',
            hovertemplate='%{y}' + ('원' if col == '종가' else '%') + '<extra></extra>'
        )
