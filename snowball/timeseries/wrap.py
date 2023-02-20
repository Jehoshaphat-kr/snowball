from snowball.timeseries.handle import _handle
import plotly.graph_objects as go
import pandas as pd


class _trace(_handle):

    @property
    def candle(self) -> go.Candlestick:
        if self.ohlcv.empty:
            return go.Candlestick()
        if not hasattr(self, '__candle'):
            self.__setattr__('__candle', go.Candlestick(
                name=self.name, x=self.ohlcv.index,
                open=self.ohlcv.시가, high=self.ohlcv.고가, low=self.ohlcv.저가, close=self.ohlcv.종가,
                visible=True, showlegend=True,
                increasing_line=dict(color='red'), decreasing_line=dict(color='royalblue'),
                xhoverformat="%Y/%m/%d", yhoverformat=self.dtype
            ))
        return self.__getattribute__('__candle')

    @property
    def volume(self) -> go.Bar:
        return go.Bar()

    def _lining(self, sr:pd.Series):
        if not hasattr(self, f'__line{sr.name}'):
            self.__setattr__('__line', go.Scatter(
                name=f"{self.name}", x=sr.index, y=sr,
                visible=True, showlegend=True,
                xhoverformat="%Y/%m/%d", yhoverformat=self.dtype,
                hovertemplate='%{x}<br>%{y}' + f'{self.unit}<extra></extra>'
            ))
        return self.__getattribute__('__line')

    @property
    def line(self):
        src = self.src if self.ohlcv.empty else self.ohlcv[col]
        return self._lining(sr=src)


if __name__ == "__main__":
    obj = _trace(ticker='012330')

    fig = go.Figure(
        layout=dict(paper_bgcolor='white')
    )
    # fig.add_trace(obj.candle)
    fig.add_trace(obj.line())
    fig.show()