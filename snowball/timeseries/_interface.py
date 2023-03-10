from datetime import timedelta, datetime
from scipy.stats import linregress
from snowball.timeseries._fetch import _fetch
import pandas as pd
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
np.seterr(divide='ignore', invalid='ignore')


def fit(series:pd.Series) -> pd.Series or pd.DataFrame:
    """
    :param series : Time-series(index datetime) 1D data
    :return: regression data
    """
    data = pd.DataFrame(data={'Time':series.index, 'Data':series})

    x = (data.Time.diff()).dt.days.fillna(1).astype(int).cumsum()
    y = data.Data
    s, i, _, _, _ = linregress(x=x, y=y)
    regression = s * x + i
    regression.name = 'Regression'
    _ = pd.concat(objs=[data, regression], axis=1)
    return _[['Time', 'Regression']].set_index(keys='Time')


def tip2tip(series:pd.Series, top_bottom:str, limit_far:int=5) -> pd.Series:
    """
    Used to determine support or resistant line
    :param series     : Time-series data
    :param top_bottom : [str] 'top' to find resist line, 'bottom' to find support line
    :param limit_far  : [bool]
    :return: Time-series data
    """
    idx, col = series.index.name, series.name
    series = series.reset_index(level=0)
    series['n'] = (series[idx].diff()).dt.days.fillna(1).astype(int).cumsum()
    series = series.set_index(keys=idx)

    i, r = -1, 2
    tip_y1 = (series[col].nlargest(1) if top_bottom == 'top' else series[col].nsmallest(1)).iloc[i]
    tip_y2 = (series[col].nlargest(r) if top_bottom == 'top' else series[col].nsmallest(r)).iloc[i]
    tip_x1 = series[series[col] == tip_y1]['n'].iloc[i]
    tip_x2 = series[series[col] == tip_y2]['n']
    while abs(tip_x1 - tip_x2.iloc[i]) < limit_far:
        if len(tip_x2) >= 2:
            i -= 1
            continue
        i, r = -1, (r + 1)
        tip_y2 = (series[col].nlargest(r) if top_bottom == 'top' else series[col].nsmallest(r)).iloc[i]
        tip_x2 = series[series[col] == tip_y2]['n']
    tip_x2 = tip_x2.iloc[-1]

    slope = (tip_y2 - tip_y1) / (tip_x2 - tip_x1)
    intercept = tip_y2 - ((tip_y2 - tip_y1) / (tip_x2 - tip_x1)) * tip_x2
    return slope * series.n + intercept
    # print(tip_x1, tip_y1)
    # print(tip_x2, tip_y2)


    # tip_v = price[key].max() if key == '고가' else price[key].min()
    # tip = price[price[key] == tip_v]
    # tip_i, tip_n = tip.index[-1], tip['N'].values[-1]
    # regression = lambda x, y: ((y - tip_v) / (x - tip_n), y - ((y - tip_v) / (x - tip_n)) * x)
    #
    # r_cond, l_cond = price.index > tip_i, price.index < tip_i
    # r_side = price[r_cond].drop_duplicates(keep='last').sort_values(by=key, ascending=not key == '고가')
    # l_side = price[l_cond].drop_duplicates(keep='first').sort_values(by=key, ascending=not key == '고가')
    #
    # r_regress, l_regress = pd.Series(dtype=float), pd.Series(dtype=float)
    # for n, side in enumerate((r_side, l_side)):
    #     n_prev = len(price)
    #     for x, y in zip(side.N, side[key]):
    #         slope, intercept = regression(x=x, y=y)
    #         regress = slope * price.N + intercept
    #         cond = price[key] >= regress if key == '고가' else price[key] <= regress
    #
    #         n_curr = len(price[cond])
    #         if n_curr < n_prev and n_curr < 3:
    #             if n:
    #                 l_regress = regress
    #             else:
    #                 r_regress = regress
    #             break
    #         n_prev = n_curr
    #
    # if r_regress.empty:
    #     return l_regress
    # if l_regress.empty:
    #     return r_regress
    # r_error = math.sqrt((r_regress - price[key]).pow(2).sum())
    # l_error = math.sqrt((l_regress - price[key]).pow(2).sum())
    # return r_regress if r_error < l_error else l_regress

# def delimit(price:pd.DataFrame, key:str) -> pd.Series:
#     tip_v = price[key].max() if key == '고가' else price[key].min()
#     tip = price[price[key] == tip_v]
#     tip_i, tip_n = tip.index[-1], tip['N'].values[-1]
#     regression = lambda x, y: ((y - tip_v) / (x - tip_n), y - ((y - tip_v) / (x - tip_n)) * x)
#
#     r_cond, l_cond = price.index > tip_i, price.index < tip_i
#     r_side = price[r_cond].drop_duplicates(keep='last').sort_values(by=key, ascending=not key == '고가')
#     l_side = price[l_cond].drop_duplicates(keep='first').sort_values(by=key, ascending=not key == '고가')
#
#     r_regress, l_regress = pd.Series(dtype=float), pd.Series(dtype=float)
#     for n, side in enumerate((r_side, l_side)):
#         n_prev = len(price)
#         for x, y in zip(side.N, side[key]):
#             slope, intercept = regression(x=x, y=y)
#             regress = slope * price.N + intercept
#             cond = price[key] >= regress if key == '고가' else price[key] <= regress
#
#             n_curr = len(price[cond])
#             if n_curr < n_prev and n_curr < 3:
#                 if n:
#                     l_regress = regress
#                 else:
#                     r_regress = regress
#                 break
#             n_prev = n_curr
#
#     if r_regress.empty:
#         return l_regress
#     if l_regress.empty:
#         return r_regress
#     r_error = math.sqrt((r_regress - price[key]).pow(2).sum())
#     l_error = math.sqrt((l_regress - price[key]).pow(2).sum())
#     return r_regress if r_error < l_error else l_regress


class _handle(_fetch):

    @property
    def typical(self) -> pd.Series:
        return (self.ohlcv.고가 + self.ohlcv.저가 + self.ohlcv.종가)/3 if self.isohlcv() else self.close

    @property
    def max52w(self) -> int or float:
        if self.ohlcv.empty:
            return None
        return self.ohlcv[self.ohlcv.index >= (self.ohlcv.index[-1] - timedelta(365))].max()['종가']

    @property
    def min52w(self) -> int or float:
        if self.ohlcv.empty:
            return None
        return self.ohlcv[self.ohlcv.index >= (self.ohlcv.index[-1] - timedelta(365))].min()['종가']

    @property
    def relreturn(self) -> pd.DataFrame:
        """
        Relative return in given period (3M / 6M / 1Y / 2Y / 3Y / 5Y), start normalized with 0%
        :return:
                            3M          6M          1Y          2Y           3Y           5Y
        Time
        2019-03-05         NaN         NaN         NaN         NaN          NaN     0.000000
        2019-03-06         NaN         NaN         NaN         NaN          NaN     8.702613
        2019-03-07         NaN         NaN         NaN         NaN          NaN    10.758197
        ...                ...         ...         ...         ...          ...          ...
        2023-03-07   95.714286   97.027804  131.478874  443.248387   973.163089  1215.957992
        2023-03-08   99.047619  100.383509  135.421337  452.500793   991.440806  1238.370902
        2023-03-09   95.238095   96.548418  130.915665  441.926615   970.551987  1212.756148
        """
        if hasattr(self, '__rr'):
            return self.__getattribute__('__rr')
        c = self.close
        objs = {
            label: 100 * (c[c.index >= c.index[-1] - timedelta(dt)].pct_change().fillna(0) + 1).cumprod() - 100
            for label, dt in [('3M', 92), ('6M', 183), ('1Y', 365), ('2Y', 730), ('3Y', 1095), ('5Y', 1825)]
        }
        self.__setattr__('__rr', pd.concat(objs=objs, axis=1))
        return self.__getattribute__('__rr')

    @property
    def trendline(self) -> pd.DataFrame:
        """
        Price trend line(: linear regression) calculated by typical price
        :return:
                               1M             2M             3M             6M             1Y
        Time
        2022-03-10            NaN            NaN            NaN            NaN  106012.474116
        2022-03-11            NaN            NaN            NaN            NaN  106056.048390
        2022-03-14            NaN            NaN            NaN            NaN  106186.771210
        ...                   ...            ...            ...            ...            ...
        2023-03-07  195156.104735  182785.820622  163967.529793  138070.188302  121786.361110
        2023-03-08  197885.345819  184600.862307  164944.454908  138349.457048  121829.935383
        2023-03-09  200614.586903  186415.903992  165921.380023  138628.725794  121873.509657
        """
        if hasattr(self, '__tl'):
            return self.__getattribute__('__tl')
        objs = list()
        for gap, days in [('1M', 30), ('2M', 61), ('3M', 92), ('6M', 183), ('1Y', 365)]:
            fitted = fit(series=self.typical[self.typical.index >= (self.typical.index[-1] - timedelta(days))])
            objs.append(fitted.rename(columns={'Regression': gap}))
        self.__setattr__('__tl', pd.concat(objs=objs, axis=1))
        return self.__getattribute__('__tl')

    @property
    def trendstrength(self) -> pd.DataFrame:
        """
        Price trend line(: linear regression) strength
        :return:
                    1M     2M      3M      6M      1Y
        247540  2.2986  2.288  1.2847  0.3191  0.0411
        """
        objs = dict()
        for col in self.trendline.columns:
            tr = self.trendline[col].dropna()
            dx, dy = (tr.index[-1] - tr.index[0]).days, 100 * (tr[-1] / tr[0] - 1)
            slope = round(dy / dx, 4)
            objs[col] = slope # Slope Strength
        return pd.DataFrame(data=objs, index=[self.ticker])

    @property
    def boundline(self) -> pd.DataFrame:
        """

        :return:
        """
        if self.isohlcv():
            resist = tip2tip(self.ohlcv.고가, 'top')
            support = tip2tip(self.ohlcv.저가, 'bottom')
        else:
            resist = tip2tip(self.typical, 'top')
            support = tip2tip(self.typical, 'bottom')
        df = pd.concat(objs=dict(resist= resist, support=support), axis=1)
        return df

if __name__ == "__main__":
    """
    TESTER TICKERS
    
    049520: 유아이엘
    054630: 에이디칩스
    032800: 판타지오
    104620: 노랑풍선
    091990: 셀트리온헬스케어
    068760: 셀트리온제약
    263750: 펄어비스
    293490: 카카오게임즈
    247540: 에코프로비엠
    """
    pd.set_option('display.expand_frame_repr', False)

    test = _handle(ticker='293490')
    # print(test.ohlcv)
    # print(test.typical)
    # print(test.max52w)
    # print(test.relreturn)
    # print(test.trendline)
    # print(test.trendstrength)
    print(test.boundline)