from snowball.timeseries._view import _trace
from plotly.subplots import make_subplots
from plotly.offline import plot
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

class TimeSeries(_trace):
    range_selector = dict(
        buttons=list([
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=3, label="3m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(step="all")
        ])
    )

    def __init__(self, ticker:str, label:str=str()):
        super().__init__(ticker=ticker, label=label)
        self.__p = os.path.join(os.path.join(os.environ['USERPROFILE']), rf'Desktop/snob/{self.ticker} {self.name}')
        if not os.path.isdir(self.__p):
            os.makedirs(self.__p)
        return

    @property
    def path(self) -> str:
        return self.__p

    @path.setter
    def path(self, path:str):
        if not os.path.isdir(path):
            os.makedirs(path)
        self.__p = path

    def _ohlcv(self):
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.8, 0.2],
            shared_xaxes=True,
            vertical_spacing=0.02
        )
        fig.add_traces(
            data=[

            ],
            rows=[1],
            cols=[1]
        )
        fig.update_layout(
            title=f'<b>{self.name}({self.ticker})</b> OHLCV',
            plot_bgcolor='white',
            xaxis=dict(
                showticklabels=False,
                showgrid=True,
                gridcolor='lightgrey',
                rangeselector=range_selector
            ),
            xaxis2=dict(
                title='날짜',
                showgrid=True,
                gridcolor='lightgrey',
                tickformat='%Y/%m/%d',
            ),
            xaxis_rangeslider=dict(visible=False)
        )


if __name__ == "__main__":
    # 006400 삼성SDI
    # 051910 LG화학
    # 012330 현대모비스
    # 035420 네이버
    # 015760 한국전력공사
    series = TimeSeries('035420')
