from snowball.archive import symbols
from snowball.timeseries import TimeSeries
from snowball.fundamental import KrseStock




class _memory(object):
    def loc(self, attrib:str):
        return True if hasattr(self, f"__{attrib}") else False
    def get(self, attrib:str):
        return self.__getattribute__(f"__{attrib}")
    def set(self, attrib:str, value):
        self.__setattr__(f"__{attrib}", value)
_mem = _memory()


def __getattr__(name):
    attr = name.lower()
    if attr in ['timeseries', 'krsestock']:
        return
    if not _mem.loc(attr):
        if attr == 'krsir':
            _mem.set(attr, TimeSeries('722Y001', '한국은행 기준금리'))
        elif attr == 'krty1y':
            _mem.set(attr, TimeSeries('817Y002', '국고채(1년)'))
        elif attr == 'krty2y':
            _mem.set(attr, TimeSeries('817Y002', '국고채(2년)'))
        elif attr == 'krty3y':
            _mem.set(attr, TimeSeries('817Y002', '국고채(3년)'))
        elif attr == 'krty5y':
            _mem.set(attr, TimeSeries('817Y002', '국고채(5년)'))
        elif attr == 'krty10y':
            _mem.set(attr, TimeSeries('817Y002', '국고채(10년)'))
        elif attr == 'krcd91d':
            _mem.set(attr, TimeSeries('817Y002', 'CD(91일)'))
        elif attr == 'krcp91d':
            _mem.set(attr, TimeSeries('817Y002', 'CP(91일)'))
        elif attr == 'krlcapcb3y':
            _mem.set(attr, TimeSeries('817Y002', '회사채(3년, AA-)'))
        elif attr == 'krjunkcb3y':
            _mem.set(attr, TimeSeries('817Y002', '회사채(3년, BBB-)'))
        elif attr == 'krwusdex':
            _mem.set(attr, TimeSeries('817Y002', '회사채(3년, BBB-)'))
    return _mem.get(attr)
