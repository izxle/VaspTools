from .result import Result


class Report:
    def __init__(self, results,
                 ads: bool=False,
                 surf_en: bool=False):
        self.results = results
        self.ads = ads
        self.surf_en = surf_en

        if isinstance(results, list):
            if not all(isinstance(r, Result) for r in results):
                raise ValueError()
            pass

        elif isinstance(results, Result):
            pass

        if ads:
            pass
        if surf_en:
            pass

    def repr_single(self):
        return

    def repr_multi(self):
        return

    def __str__(self):
        return

