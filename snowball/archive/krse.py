from pykrx.stock import (
    get_market_cap_by_ticker,
    get_market_fundamental,
    get_market_ohlcv_by_ticker,
    get_market_ohlcv_by_date,
    get_nearest_business_day_in_a_week,
    get_etf_ohlcv_by_ticker
)
from tqdm import tqdm
from datetime import datetime, timedelta
from pytz import timezone
import numpy as np
import pandas as pd
import requests, time, os, json
import urllib.request as req


class _krseTime(object):
    def __init__(self):
        self._now = datetime.now(timezone('Asia/Seoul'))
        self._date = self._now.strftime("%Y%m%d")
        return

    @property
    def rdate(self) -> str:
        if not hasattr(self, '__rdate'):
            self.__setattr__('__rdate', get_nearest_business_day_in_a_week(date=self._date, prev=True))
        return self.__getattribute__('__rdate')

    @property
    def is_open(self) -> bool:
        if not hasattr(self, '__is_open'):
            today = self._now.strftime("%Y%m%d") == self.rdate
            clock = 859 <= int(self._now.strftime("%H%M")) <= 1531
            self.__setattr__('__is_open', today and clock)
        return self.__getattribute__('__is_open')

    @property
    def dates(self) -> dict:
        if not hasattr(self, '__dates'):
            base = {'0D': self.rdate}
            td = datetime.strptime(self.rdate, "%Y%m%d")
            dm = lambda x: (td - timedelta(x)).strftime("%Y%m%d")
            loop = [('1D', 1), ('1W', 7), ('1M', 30), ('3M', 91), ('6M', 183), ('1Y', 365), ('2Y', 730)]
            base.update({l: get_nearest_business_day_in_a_week(date=dm(d)) for l, d in loop})
            self.__setattr__('__dates', base)
        return self.__getattribute__('__dates')

    @property
    def wdate(self) -> str:
        if not hasattr(self, f'__wdate'):
            src = requests.get(url='http://www.wiseindex.com/Index/Index#/G1010.0.Components').text
            tic = src.find("기준일")
            toc = tic + src[tic:].find("</p>")
            self.__setattr__(f'__wdate', src[tic + 6: toc].replace('.', ''))
        return self.__getattribute__(f'__wdate')


class _krseGroup(_krseTime):
    _dir = os.path.join(os.path.dirname(__file__), rf'krse')
    _labels = {
        'WICS': {
            'G1010': '에너지',
            'G1510': '소재',
            'G2010': '자본재',
            'G2020': '상업서비스와공급품',
            'G2030': '운송',
            'G2510': '자동차와부품',
            'G2520': '내구소비재와의류',
            'G2530': '호텔,레스토랑,레저 등',
            'G2550': '소매(유통)',
            'G2560': '교육서비스',
            'G3010': '식품과기본식료품소매',
            'G3020': '식품,음료,담배',
            'G3030': '가정용품과개인용품',
            'G3510': '건강관리장비와서비스',
            'G3520': '제약과생물공학',
            'G4010': '은행',
            'G4020': '증권',
            'G4030': '다각화된금융',
            'G4040': '보험',
            'G4050': '부동산',
            'G4510': '소프트웨어와서비스',
            'G4520': '기술하드웨어와장비',
            'G4530': '반도체와반도체장비',
            'G4535': '전자와 전기제품',
            'G4540': '디스플레이',
            'G5010': '전기통신서비스',
            'G5020': '미디어와엔터테인먼트',
            'G5510': '유틸리티'
        },
        'WI26' : {
            'WI100': '에너지',
            'WI110': '화학',
            'WI200': '비철금속',
            'WI210': '철강',
            'WI220': '건설',
            'WI230': '기계',
            'WI240': '조선',
            'WI250': '상사,자본재',
            'WI260': '운송',
            'WI300': '자동차',
            'WI310': '화장품,의류',
            'WI320': '호텔,레저',
            'WI330': '미디어,교육',
            'WI340': '소매(유통)',
            'WI400': '필수소비재',
            'WI410': '건강관리',
            'WI500': '은행',
            'WI510': '증권',
            'WI520': '보험',
            'WI600': '소프트웨어',
            'WI610': 'IT하드웨어',
            'WI620': '반도체',
            'WI630': 'IT가전',
            'WI640': '디스플레이',
            'WI700': '통신서비스',
            'WI800': '유틸리티',
        }
    }
    _wise_url = 'http://www.wiseindex.com/Index/GetIndexComponets?ceil_yn=0&dt=%s&sec_cd=%s'

    def _fetch(self, name:str) -> pd.DataFrame:
        loop, data = tqdm(self._labels[name].items()), list()
        for c, l in loop:
            loop.set_description(desc=f'{name} / {l}({c}) ...')
            for n in range(6):
                req = requests.get(self._wise_url % (self.wdate, c))
                if req.status_code == 200:
                    for _ in req.json()['list']:
                        data.append([_['CMP_CD'], _['CMP_KOR'], _['SEC_NM_KOR'], _['IDX_NM_KOR'][5:], self.wdate])
                    break
                print(
                    f"\t- Failed fetching WISE category {name} / {l}({c})" if n == 5 else \
                    f"\t- HTTP Error while fetching WISE category {name} / {l}({c})... redirecting... ({n + 1})"
                )
                if n < 5:
                    time.sleep(5)
        return pd.DataFrame(data=data, columns=['종목코드', '종목명', '산업', '섹터', 'DT']).set_index(keys='종목코드')

    @property
    def wiselabel(self) -> dict:
        return self._labels

    @property
    def wics(self) -> pd.DataFrame:
        if not hasattr(self, f'__wics'):
            fetch = pd.read_csv(os.path.join(self._dir, 'wics.csv'), index_col='종목코드', encoding='utf-8')
            fetch.index = fetch.index.astype(str).str.zfill(6)
            if not str(fetch['DT'][0]) == self.wdate:
                fetch = self._fetch(name='WICS')
                fetch.to_csv(os.path.join(self._dir, 'wics.csv'), index=True, encoding='utf-8')
            self.__setattr__(f'__wics', fetch.drop(columns=['DT']))
        return self.__getattribute__(f'__wics')

    @property
    def wi26(self) -> pd.DataFrame:
        if not hasattr(self, f'__wi26'):
            fetch = pd.read_csv(os.path.join(self._dir, 'wi26.csv'), index_col='종목코드', encoding='utf-8')
            fetch.index = fetch.index.astype(str).str.zfill(6)
            if not str(fetch['DT'][0]) == self.wdate:
                fetch = self._fetch(name='WI26')
                fetch.drop(columns=['산업'], inplace=True)
                fetch.to_csv(os.path.join(self._dir, 'wi26.csv'), index=True, encoding='utf-8')
            self.__setattr__(f'__wi26', fetch.drop(columns=['DT']))
        return self.__getattribute__(f'__wi26')


class _krse(_krseGroup):
    _insi = False
    _pdir = os.path.join(os.path.dirname(__file__), rf'krse/perf.csv')
    def _get_marketcap(self) -> pd.DataFrame:
        return get_market_cap_by_ticker(date=self.rdate, market="ALL", alternative=True)

    def _get_multiples(self) -> pd.DataFrame:
        return get_market_fundamental(date=self.rdate, market="ALL", alternative=True)

    def _get_ipo(self) -> pd.DataFrame:
        io = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download'
        ipo = pd.read_html(io=io, header=0)[0][['회사명', '종목코드', '상장일']]
        ipo = ipo.rename(columns={'회사명': '종목명', '상장일': 'IPO'}).set_index(keys='종목코드')
        ipo.index = ipo.index.astype(str).str.zfill(6)
        ipo.IPO = pd.to_datetime(ipo.IPO)
        return ipo[ipo.IPO <= datetime.strptime(self.rdate, "%Y%m%d")]

    def _init_p(self) -> pd.DataFrame:
        if not hasattr(self, '__p'):
            shares = pd.concat(objs={
                'prev': get_market_cap_by_ticker(date=self.dates['1Y'], market='ALL')['상장주식수'],
                'curr': get_market_cap_by_ticker(date=self.dates['0D'], market='ALL')['상장주식수']
            }, axis=1)
            even = shares[shares.prev == shares.curr].index.tolist()

            prc = pd.concat({
                f'TD{k}': get_market_ohlcv_by_ticker(date=date, market='ALL', alternative=False)['종가']
                for k, date, in tqdm(self.dates.items(), desc='기간별 수익률 계산(주식)')
            }, axis=1)

            _p = pd.concat(
                objs={f'R{k}': round(100 * (prc['TD0D'] / prc[f'TD{k}'] - 1), 2) for k in self.dates.keys()},
                axis=1
            )
            _p = _p[_p.index.isin(even)].drop(columns=['R0D'])
            _p['DT'] = self.rdate
            self.__setattr__('__p',_p)
        return self.__getattribute__('__p')

    def _update_p(self, tickers: list) -> pd.DataFrame:
        if not len(tickers):
            return pd.DataFrame()

        objs, proc = list(), tqdm(tickers)
        for ticker in proc:
            proc.set_description(f'Fetch Returns - {ticker}')
            c = get_market_ohlcv_by_date(ticker=ticker, fromdate=self.dates['2Y'], todate=self.dates['0D'])['종가']
            objs.append({
                label: round(100 * c.pct_change(periods=dt)[-1], 2)
                for label, dt in [('R1D', 1), ('R1W', 5), ('R1M', 21), ('R3M', 63), ('R6M', 126), ('R1Y', 252)]
            })
        p = pd.DataFrame(data=objs, index=tickers)
        p['DT'] = self.rdate
        return p

    def performance(self, tickers:list or pd.Series or np.array):
        read = pd.read_csv(filepath_or_buffer=self._pdir, index_col='종목코드', encoding='utf-8')
        read.index = read.index.astype(str).str.zfill(6)
        if self.is_open and not self._insi:
            return read[read.index.isin(tickers)].drop(columns=['DT'])

        init = self._init_p()
        p = pd.concat(objs=[init, read[~read.index.isin(init.index)]], axis=0)
        new = self._update_p(tickers=[t for t in tickers if not t in p.index])

        pick = p[p.index.isin(tickers)]
        upd = self._update_p(tickers=pick[pick['DT'].astype(str) != self.rdate].index)

        push = pd.concat(objs=[init, new, upd], axis=0)
        save = pd.concat(objs=[push, read[~read.index.isin(push.index)]], axis=0)
        save.index.name = '종목코드'
        save.to_csv(self._pdir, index=True, encoding='utf-8')
        return save[save.index.isin(tickers)].drop(columns=['DT'])

    @property
    def insist(self) -> bool:
        return self._insi

    @insist.setter
    def insist(self, insist):
        self._insi = insist

    @property
    def overview(self) -> pd.DataFrame:
        if not hasattr(self, '__basis'):
            path = os.path.join(os.path.dirname(__file__), rf'krse/basis.csv')
            _base = pd.read_csv(path, index_col='종목코드', encoding='utf-8')
            _base.index = _base.index.astype(str).str.zfill(6)
            _base.IPO = pd.to_datetime(_base.IPO)
            if not self.is_open and not str(_base['DT'][0]) == self.rdate:
                _base = pd.concat(objs = [self._get_ipo(), self._get_marketcap(), self._get_multiples()], axis=1)
                _base['DT'] = self.rdate
                _base.index.name = '종목코드'
                _base.to_csv(path, index=True, encoding='utf-8')
            self.__setattr__('__basis', _base.drop(columns=['DT']))
        return self.__getattribute__('__basis')


class _krseETF(object):
    _dir = os.path.join(os.path.dirname(__file__), r'krse/etf.csv')
    def __init__(self, dates:dict):
        self.dates = dates
        return

    @property
    def overview(self) -> pd.DataFrame:
        if not hasattr(self, '__overview'):
            url = 'https://finance.naver.com/api/sise/etfItemList.nhn'
            key_prev = ['itemcode', 'itemname', 'nowVal', 'marketSum']
            key_curr = ['종목코드', '종목명', '종가', '시가총액']
            df = pd.DataFrame(json.loads(req.urlopen(url).read().decode('cp949'))['result']['etfItemList'])
            df = df[key_prev].rename(columns=dict(zip(key_prev, key_curr)))
            df['시가총액'] = df['시가총액'] * 100000000
            self.__setattr__('__overview', df.set_index(keys='종목코드'))
        return self.__getattribute__('__overview')

    @property
    def group(self) -> pd.DataFrame:
        df = pd.read_csv(self._dir, index_col='종목코드')
        df.index = df.index.astype(str).str.zfill(6)
        return df

    @property
    def returns(self) -> pd.DataFrame:
        if not hasattr(self, '__performance'):
            prc = pd.concat({
                f'TD{k}': get_etf_ohlcv_by_ticker(date=date)['종가']
                for k, date in tqdm(self.dates.items(), desc='기간별 수익률 계산(ETF)')
            }, axis=1)
            rtrn = pd.concat({
                f'R{k}': round(100 * (prc['TD0D'] / prc[f'TD{k}'] - 1), 2) for k in self.dates.keys()
            }, axis=1)
            rtrn.index.name = '종목코드'
            self.__setattr__('__performance', rtrn[~rtrn['R1D'].isna()].drop(columns=['R0D']))
        return self.__getattribute__('__performance')

    def islatest(self) -> bool:
        curr, prev = self.overview.copy(), self.group.copy()
        to_be_delete = prev[~prev.index.isin(curr.index)]
        to_be_update = curr[~curr.index.isin(prev.index)]
        if to_be_delete.empty and to_be_update.empty:
            return True

        for kind, frm in [('삭제', to_be_delete), ('추가', to_be_update)]:
            if not frm.empty:
                print("-" * 70, f"\n▷ ETF 분류 {kind} 필요 항목: {'없음' if frm.empty else '있음'}\n{frm}")
        return False