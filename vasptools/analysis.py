
from .reader import read, hasdirs
from .report import Report


def generate_report(results: list, ads: bool=False, surf_en: bool=False, **kwargs):

    report = Report(results)

    return report
