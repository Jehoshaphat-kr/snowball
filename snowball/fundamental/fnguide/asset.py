from snowball.fundamental.fnguide._fetch import get_asset
import pandas as pd
import plotly.graph_objects as go


class asset(object):
    def __init__(self, stat:pd.DataFrame):
        self._s = stat

    def __call__(self, mode:str='default'):
        return

    @property
    def src(self) -> pd.DataFrame:
        if not hasattr(self, '__src'):
            self.__setattr__('__src', get_asset(self._s))
        return self.__getattribute__('__src')

    @property
    def traces(self) -> list:
        traces = [
            (go.Bar if n else go.Scatter)(
                name=c,
                x=self.src.index,
                y=self.src[c],
                showlegend=True if n else False,
                visible=True,
                opacity=0.9 if n else 1.0,
                meta=round(100 * self.src[c] / self.src.자산총계, 2) if n else None,
                text=self.src[f"{c}LB"],
                texttemplate="%{text}<br>(%{meta}%)" if n else "총 자산: %{text}",
                textposition="inside" if n else "top center",
                hoverinfo="all" if n else "skip",
                hovertemplate=c[:2] + ': %{y}%<extra></extra>' if n else None
            ) for n, c in enumerate(['자산총계', '부채총계', '자본총계'])
        ]
        traces[0].mode = 'text'
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