from snowball.fundamental.fetch import fnguide
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd


class _trace(fnguide):

    _c = [
        '#1f77b4',  # muted blue
        '#ff7f0e',  # safety orange
        '#2ca02c',  # cooked asparagus green
        '#d62728',  # brick red
        '#9467bd',  # muted purple
        '#8c564b',  # chestnut brown
        '#e377c2',  # raspberry yogurt pink
        '#7f7f7f',  # middle gray
        '#bcbd22',  # curry yellow-green
        '#17becf'   # blue-teal
    ]

    @property
    def PRODUCTS_ALL_BAR(self) -> go.Figure:
        traces = [
            go.Bar(
                name=f"{c}",
                x=self.products_all.index,
                y=self.products_all[c],
                showlegend=True,
                legendgroup=c,
                visible=True,
                marker=dict(color=self._c[n]),
                opacity=0.9,
                textposition="inside",
                texttemplate=c + "<br>%{y:.2f}%",
                hovertemplate=c + "<br>%{y:.2f}%<extra></extra>"
            ) for n, c in enumerate(self.products_all.columns)
        ]
        layout = dict(
            title=f"{self.name}({self.ticker}) Products",
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
            xaxis_rangeslider=dict(
                visible=False
            )
        )
        return go.Figure(data=traces, layout=layout)

    @property
    def PRODUCTS_RECENT_BAR(self) -> go.Figure:
        traces = [
            go.Bar(
                name=c,
                x=[self.name],
                y=[self.products_recent[c]],
                showlegend=True,
                visible=True,
                marker=dict(color=self._c[n]),
                opacity=0.9,
                text=c,
                textposition="inside",
                texttemplate="%{text}<br>%{y:.2f}%",
                hovertemplate=c + "<br>%{y:.2f}%<extra></extra>"
            ) for n, c in enumerate(self.products_recent.index)
        ]
        layout = dict(
            title=f"{self.name}({self.ticker}) Products @{self.products_recent.name}",
            plot_bgcolor='white',
            barmode='stack',
            legend=dict(
                orientation="h",
                xanchor="right",
                yanchor="bottom",
                x=0.96,
                y=1
            ),
            yaxis=dict(
                title='비율 [%]',
                showgrid=True,
                gridcolor='lightgrey',
                zeroline=True,
                zerolinecolor='lightgrey'
            ),
            xaxis_rangeslider=dict(
                visible=False
            )
        )
        return go.Figure(data=traces, layout=layout)

    @property
    def PRODUCTS_RECENT_PIE(self) -> go.Figure:
        traces = [
            go.Pie(
                labels=self.products_recent.index,
                values=self.products_recent,
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
        layout = dict(
            title=f"{self.name}({self.ticker}) Products @{self.products_recent.name}",
            plot_bgcolor='white',
            legend=dict(
                orientation="h",
                xanchor="right",
                yanchor="bottom",
                x=0.96,
                y=1
            ),
        )
        return go.Figure(data=traces, layout=layout)

    @property
    def ASSET(self) -> go.Figure:
        traces = [
            go.Bar(
                name=c,
                x=self.asset.index,
                y=self.asset[c],
                showlegend=True,
                visible=True,
                opacity=0.9,
                meta=round(100 * self.asset[c] / self.asset.자산총계, 2),
                text=self.asset[f"{c}LB"],
                texttemplate="%{text}<br>(%{meta}%)",
                textposition="inside",
                hoverinfo='skip'
            ) for n, c in enumerate(['자본총계', '부채총계'])
        ]
        trace = go.Scatter(
            name='자산총계',
            x=self.asset.index,
            y=self.asset.자산총계,
            showlegend=False,
            visible=True,
            mode="text",
            text=self.asset.자산총계LB,
            textposition="top center",
            texttemplate="총 자산: %{text}",
            hoverinfo='skip'
        )

        layout = dict(
            title=f"{self.name}({self.ticker}) Asset",
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
        return go.Figure(data=traces, layout=layout).add_trace(trace)

    @property
    def PROFIT(self) -> go.Figure:
        traces = [
            go.Bar(
                name=c,
                x=self.profit.index,
                y=self.profit[c],
                showlegend=True,
                visible=True,
                opacity=0.9,
                marker=dict(color=self._c[n]),
                text=self.profit[f"{c}LB"],
                textposition="inside",
                texttemplate="%{text}",
                hovertemplate=c + ": %{text}<extra></extra>"
            ) for n, c in enumerate(self.profit.columns) if not c.endswith('LB')
        ]
        layout = dict(
            title=f"{self.name}({self.ticker}) Profit",
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
        return go.Figure(data=traces, layout=layout)

    @property
    def EXPENSE(self) -> go.Figure:
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=["Profit Rate", "Sales Cost Rate", "Sales and Management Cost Rate", "R&D Investment Rate"],
            x_title="기말",
            y_title="[%]",
        )
        trace = go.Scatter(
            name='영업이익률',
            x=self.statement.index,
            y=self.statement['영업이익률'].astype(float),
            showlegend=True,
            visible=True,
            mode='lines+markers+text',
            textposition="top center",
            texttemplate="%{y:.2f}%",
            hoverinfo='skip'
        )
        traces = [
            go.Scatter(
                name=c,
                x=self.expenses.index,
                y=self.expenses[c].astype(float),
                showlegend=True,
                visible=True,
                mode='lines+markers+text',
                textposition="top center",
                texttemplate="%{y:.2f}%",
                hoverinfo='skip'
            ) for n, c in enumerate(("매출원가율", "판관비율", "R&D투자비중"))
        ]
        fig.add_traces(data=[trace] + traces, rows=[1, 1, 2, 2], cols=[1, 2, 1, 2])
        fig.update_layout(dict(
            title=f"{self.name}({self.ticker}) Profit Rate and Expenses",
            plot_bgcolor='white',
            barmode='stack',
            legend=dict(
                orientation="h",
                xanchor="right",
                yanchor="bottom",
                x=1,
                y=1.04
            ),
        ))
        fig.update_yaxes(dict(showgrid=True, gridcolor='lightgrey'))
        return fig

    @property
    def SUPPLY(self) -> go.Figure:
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=["Consensus", "Foreigner: 3Y", "Foreigner: 1Y", "Foreigner: 3M"],
            horizontal_spacing=0.08, vertical_spacing=0.08,
            specs=[
                [{}, {'secondary_y':True}],
                [{'secondary_y':True}, {'secondary_y':True}]
            ],
            x_title="날짜", y_title='종가[원]'
        )
        for n, c in enumerate(self.consensus):
            if c == '투자의견': continue
            fig.add_trace(
                go.Scatter(
                    name=c,
                    x=self.consensus.index,
                    y=self.consensus[c],
                    showlegend=False if c.endswith('종가') else True,
                    legendgroup=c,
                    mode='lines',
                    line=dict(dash='dot' if c == '종가' else None, color='black' if c == '종가' else self._c[0]),
                    xhoverformat="%Y/%m/%d",
                    yhoverformat=",d",
                    hovertemplate="%{x}<br>" + c + ": %{y}원<extra></extra>"
                ), row=1, col=1
            )
        for n, c in enumerate(('3Y', '1Y', '3M')):
            df = self.foreigner[c].dropna()
            for col in df.columns[::-1]:
                trace = go.Scatter(
                    name=col,
                    x=df.index,
                    y=df[col],
                    showlegend=True if not n else False,
                    legendgroup=col,
                    mode='lines',
                    line=dict(dash='dot' if col == '종가' else None, color='black' if col == '종가' else self._c[1]),
                    xhoverformat='%Y/%m/%d',
                    yhoverformat=",d" if col == '종가' else ".2f",
                    hovertemplate="%{x}<br>" + col + ": %{y}" + ("원" if col == '종가' else '%') + "<extra></extra>"
                )
                fig.add_trace(
                    trace, row={0:1, 1:2, 2:2}[n], col={0:2, 1:1, 2:2}[n],
                    secondary_y=False if col == '종가' else True
                )
        fig.update_layout(dict(
            title=f"{self.name}({self.ticker}) Consensus and Foreign Rate",
            plot_bgcolor='white',
            margin=dict(r=0),
            legend=dict(
                orientation="h",
                xanchor="right",
                yanchor="bottom",
                x=1,
                y=1.04
            ),
        ))
        fig.update_xaxes(dict(showticklabels=True, tickformat="%Y/%m/%d", showgrid=True, gridcolor="lightgrey"))
        fig.update_yaxes(dict(showgrid=True, gridcolor='lightgrey'), secondary_y=False)
        fig.update_yaxes(dict(title='[%]'), secondary_y=True)
        return fig

    @property
    def MULTIFACTOR(self) -> go.Figure:
        traces = [
            go.Scatterpolar(
                name=col,
                r=self.multi_factor[col].astype(float),
                theta=self.multi_factor.index,
                fill='toself',
                showlegend=True,
                visible=True,
                hovertemplate=col + '<br>팩터: %{theta}<br>값: %{r}<extra></extra>'
            ) for n, col in enumerate(self.multi_factor.columns)
        ]
        layout = dict(
            title=f"{self.name}({self.ticker}) Multi-Factors",
            plot_bgcolor='white',
        )
        return go.Figure(data=traces, layout=layout)

if __name__ == "__main__":

    tester = _trace(ticker='012330')

    # tester.PRODUCTS_ALL_BAR.show()
    # tester.PRODUCTS_RECENT_BAR.show()
    # tester.PRODUCTS_RECENT_PIE.show()
    # tester.ASSET.show()
    # tester.PROFIT.show()
    # tester.EXPENSE.show()
    # tester.SUPPLY.show()
    tester.MULTIFACTOR.show()