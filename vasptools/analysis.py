
from .reader import read, hasdirs
from .report import ReportSingle, ReportCompare, ReportAdsorption, ReportSurface
from .result import Result


def generate_report(results: list, ads: bool=False, surf_en: bool=False, reps=None, **kwargs):

    if isinstance(results, Result):
        report = ReportSingle(results, reps=reps)
    elif isinstance(results, list):
        if not all(isinstance(r, Result) for r in results):
            raise ValueError()

        if ads:
            report = ReportAdsorption(results)
        elif surf_en:
            report = ReportSurface(results)
        else:
            report = ReportCompare(results, reps=reps)

    else:
        raise ValueError()

    return report
