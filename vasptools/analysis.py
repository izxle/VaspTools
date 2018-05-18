
from .reader import read, hasdirs
from .report import Report


def generate_report(filename, directory='.', ignore=[], subdir=''):
    results = read(filename=filename,
                   directory=directory,
                   ignore=ignore,
                   subdir=subdir)
    report = Report(results)
    return report
