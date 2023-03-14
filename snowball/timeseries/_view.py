from snowball.timeseries._interface import _handle
import plotly.graph_objects as go


class _trace(_handle):

    def trace_ohlcv(self):
        if not hasattr(self, '__candle'):
            self.__setattr__(
                '__candle',
                go.Candlestick(
                    name=self.name,
                    x=self.ohlcv.index,
                    open=self.ohlcv.시가,
                    high=self.ohlcv.고가,
                    low=self.ohlcv.저가,
                    close=self.ohlcv.종가,
                    visible=True,
                    showlegend=True,
                    increasing_line=dict(
                        color='red'
                    ),
                    decreasing_line=dict(
                        color='royalblue'
                    ),
                    xhoverformat='%Y/%m/%d',
                    yhoverformat=self.dtype
                )
            )
        return self.__getattribute__('__candle')

    def trace_volume(self):
        if not hasattr(self, '__vol'):
            self.__setattr__(
                '__vol',
                go.Bar(
                    name=f'{self.name} V',
                    x=self.ohlcv.index,
                    y=self.ohlcv.거래량,
                    marker=dict(
                        color=self.ohlcv.거래량.pct_change().apply(lambda x: 'royalblue' if x < 0 else 'red')
                    ),
                    visible=True,
                    showlegend=False,
                    xhoverformat='%Y/%m/%d',
                    yhoverformat=',',
                    hovertemplate='%{x}<br>%{y}<extra></extra>'
                )
            )
        return self.__getattribute__('__vol')

    def trace_ma(self, col:str):
        return go.Scatter(
            name=f'MA{col}',
            x=self.ma.index,
            y=self.ma[col],
            showlegend=True,
            visible=True,
            mode='lines',
            xhoverformat='%Y/%m/%d',
            yhoverformat='.2f',
            hovertemplate=f'MA{col}' + '@%{x}<br>%{y}<extra></extra>'
        )

    def trace_trendline(self, col:str):
        df = self.trendline[col].dropna()
        return go.Scatter(
            name=f'TR{col}',
            x=df.index,
            y=df,
            showlegend=True,
            visible=True,
            mode='lines',
            line=dict(
                dash='dot'
            ),
            xhoverformat='%Y/%m/%d',
            yhoverformat='.2f',
            hovertemplate=f'TR: {col}' + '@%{x}<br>%{y}<extra></extra>'
        )