from snowball.fundamental.fetch import fnguide
import plotly.graph_objects as go
import pandas as pd


class _tproduct(object):
    def __init__(self, _data:pd.DataFrame):
        self._d = _data.copy()

    def bars(self):
        if not hasattr(self, '__bars'):
            traces = [
                go.Bar(
                    name=f"{c}", x=self._d.index, y=self._d[c], visible=True,
                    legendgroup=f"{c}", showlegend=True,
                    opacity=0.7 + 0.1 * n if n < 4 else 1,
                    textposition="inside", texttemplate=c + "<br>%{y:.2f}",
                    hovertemplate=c + "<br>%{y:.2f}<extra></extra>"
                ) for n, c in enumerate(self._d.columns[::-1])
            ]
            self.__setattr__('__bars', traces)
        return self.__getattribute__('__bars')

    def bar(self):
        return go.Bar(
            name=
        )

    def pies(self):
        if not hasattr(self, '__pies'):
            traces = [
                go.Pie(
                    labels=self._d.columns, values=self._d.loc[i],
                    visible=True, showlegend=True, automargin=True,
                    textfont=dict(color='white'), textinfo='label+percent', insidetextorientation='radial',
                    hoverinfo='label+percent',
                )
            ]




class _trace(fnguide):

    @property
    def PRODUCTS_ALL(self):
        return [
            go.Bar(
                name=f"{c}", x=self.products_all.index, y=self.products_all[c], visible=True,
                legendgroup=f"{self.name}prod_all", showlegend=True,
                opacity=0.7 + 0.1*n if n < 4 else 1,
                textposition="inside", texttemplate=c + "<br>%{y:.2f}",
                hovertemplate=c + "<br>%{y:.2f}<extra></extra>"
            ) for n, c in enumerate(self.products_all.columns[::-1])
        ]

    @property
    def PRODUCTS_RECENT(self):

        return go.Pie


if __name__ == "__main__":

    obj = _trace(ticker='012330')

    # fig = go.Figure(obj.PRODUCTS_ALL)
    # fig.layout = dict(barmode='stack')

    fig = go.Figure(obj.PRODUCTS_RECENT)
    fig.show()