
from .reader import read
from .report import ReportCompare, ReportCompareAdsorption, ReportCompareSurface
from .report import ReportSingle, ReportSingleAdsorption, ReportSimpleSurface
from .result import Result


def generate_report(results: list, ads: bool=False, surf_en: bool=False, reps=None, subdir=''):

    if isinstance(results, Result):
        if ads:
            slab = read(directory=ads.slab)
            adsorbate = read(directory=ads.adsorbate)
            report = ReportSingleAdsorption(whole=results,
                                            slab=slab,
                                            ads=adsorbate)
        elif surf_en:
            bulk = read(directory=surf_en.bulk)
            report = ReportSimpleSurface(slab=results,
                                         bulk=bulk,
                                         area=surf_en.area)
        else:
            report = ReportSingle(results, reps=reps)



    elif isinstance(results, list):
        if not all(isinstance(r, Result) for r in results):
            raise ValueError()

        if ads:
            slab = read(directory=ads.slab)
            adsorbate = read(directory=ads.adsorbate)
            report = ReportCompareAdsorption(results=results,
                                             slab=slab,
                                             ads=adsorbate,
                                             subdir=subdir,
                                             relative=ads.relative)
        elif surf_en:
            bulk = read(directory=surf_en.bulk)
            report = ReportCompareSurface(results=results,
                                          bulk=bulk,
                                          area=surf_en.area)
        else:
            report = ReportCompare(results, reps=reps, subdir=subdir)
        # else:
        #     raise NotImplementedError()

    else:
        raise ValueError()

    return report
