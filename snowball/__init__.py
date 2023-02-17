from snowball.archive import symbols

from snowball.timeseries.wrap import TimeSeries





# class _memory(object):
#     def loc(self, attrib:str):
#         return True if hasattr(self, f"__{attrib}") else False
#     def get(self, attrib:str):
#         return self.__getattribute__(f"__{attrib}")
#     def set(self, attrib:str, value):
#         self.__setattr__(f"__{attrib}", value)
# _mem = _memory()
#
#
# def __getattr__(name):
#     attr = name.lower()
#     if not _mem.loc(attr):
#         if attr == 'ecossymbol':
#             _mem.set(attr, _ecosSymbol())
#         if attr == 'indexlist':
#             _mem.set(attr, _krseIndexList())
#     return _mem.get(attr)
