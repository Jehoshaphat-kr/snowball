from snowball.fundamental.fetch import fnguide
import plotly.graph_objects as go
import pandas as pd


class _trace(fnguide):

    @property
    def PRODUCTS_ALL(self):
        print(self.products_all)
        traces = [
            go.Bar(
                name=f"{self.name} 제품", x=self.products_all.index, y=self.products_all[c],
                legendgroup=f"{self.name}prod_all",
            ) for c in self.products_all.columns
        ]

        return


if __name__ == "__main__":

    obj = _trace(ticker='012330')

    # fig = go.Figure()
    # fig.show()