from snowball.archive import label
from snowball.fundamental.fetch import get_summary


class summary(label):
    def __call__(self, **kwargs):
        return