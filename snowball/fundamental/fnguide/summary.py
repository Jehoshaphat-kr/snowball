from snowball.fundamental.fnguide._fetch import get_summary


class summary(object):
    def __init__(self, par):
        self._s = par

    def __call__(self, mode:str='default'):
        if mode == 'src':
            return self.src
        elif mode == 'show' or mode == 'default':
            print(self.src)
        else:
            raise KeyError
        return

    @property
    def src(self) -> str:
        if not hasattr(self, '_text'):
            self.__setattr__('_text', get_summary(self._s.ticker))
        return self.__getattribute__('_text')
