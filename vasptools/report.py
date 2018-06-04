from .result import Result
import numpy as np
from os import path
from collections import Counter


class Report:
    _float_format = '9.4f'
    _name_len = 11
    def __init__(self, subdir=''):
        self.subdir = subdir


class ReportSingle(Report):
    def __init__(self, result, subdir='', reps=None):
        super().__init__(subdir=subdir)
        self.result = result
        self.reps = reps

    def __str__(self):
        r = self.result

        if self.reps is None:
            results = str(r)
        else:
            results = r.report(self.reps)

        if isinstance(r.time, float):
            time = f'time: {r.time/3600:8.4f} h | {r.time:9.3f} s'
        else:
            time = r.time

        text = (
            f'{r.name}\n'
            f'{results}\n'
            f'{time}')

        return text


class ReportCompare(Report):
    _line_len = 62
    def __init__(self, results, subdir: str='', reps=('F', 'time')):
        super().__init__(subdir=subdir)
        self.results = results
        if not reps:
            reps = ('F', 'time')
        self.reps = reps
        self.values = dict()
        for rep in reps:
            self.values[rep] = []
            for res in results:
                self.values[rep].append(res.get(rep))

        self.names = []

    def __str__(self):
        text = ''
        for rep in self.reps:
            text += '\n'
            values = np.array(self.values[rep], dtype=float)

            if rep == 'time':
                nan_mask = np.isnan(values)
                vals = values[nan_mask == False]
                relative_values = np.zeros(len(values))
                if len(vals) > 0:
                    max_val = max(vals)
                    min_val = min(vals)
                    relative_values = (vals - min_val) * self._line_len / (max_val - min_val)
                relative_values[nan_mask] = self._line_len

            else:
                max_val = max(values)
                min_val = min(values)
                relative_values = (values - min_val) * self._line_len / (max_val - min_val)

            text += f' name       | {rep:9} |\n'
            for res, rval in zip(self.results, relative_values):
                root, basename = path.split(res.name)
                if basename == self.subdir:
                    name = root
                else:
                    name = res.name
                name = path.basename(name)
                text += (f'{name[:11]:11} | {res.get(rep):9.3f} |'
                         f'{"*" * int(round(rval))}\n')
            text += f"{'':25}{'':->{self._line_len}}>\n"
        return text


class ReportSingleAdsorption(Report):
    def __init__(self, whole, slab, ads):
        super().__init__()
        self.whole = whole
        self.slab = slab
        self.ads = ads

        self.name = whole.name

        # use first element to calculate ratio
        element = ads.atoms.get_chemical_symbols()[0]
        self.ads_element = element
        n = whole.elements[element] / ads.elements[element]
        self.ratio = n
        ads_en = whole.E0 - slab.E0 - n * ads.E0
        self.ads_en = ads_en

    def __str__(self):
        text = (
            f'{self.name}\n'
            f'adsorption energy: {self.ads_en:{self._float_format}}\n'
            f'  slab + ads       {self.whole.E0:{self._float_format}}\n'
            f'  slab             {self.slab.E0:{self._float_format}}\n'
            f'{self.ratio:3} x ads ({self.ads_element:>2})     {self.ratio * self.ads.E0:{self._float_format}}\n'
            f'  ads              {self.ads.E0:{self._float_format}}\n'
        )
        return text


class ReportCompareAdsorption(Report):
    def __init__(self, results, slab, ads, subdir=''):
        super().__init__(subdir)
        self.slab = slab
        self.ads = ads
        self.results = results

        ads_energies = dict()
        for whole in results:
            report = ReportSingleAdsorption(whole=whole,
                                            slab=slab,
                                            ads=ads)
            # name handling
            root, basename = path.split(report.name)
            if basename == self.subdir:
                name = root
            else:
                name = report.name
            name = path.basename(name)
            ads_energies[name] = report

        self.ads_energies = ads_energies

    def __str__(self):
        text = 'Adsorption Energies\n'

        for name, report in self.ads_energies.items():
            text += f'{name[:self._name_len]:{self._name_len}} {report.ads_en:{self._float_format}}\n'

        return text


class ReportSimpleSurface(Report):
    def __init__(self, slab, bulk, area=None):
        super().__init__()
        self.slab = slab
        self.bulk = bulk
        if area:
            self.area = area
        else:
            self.area = slab.area

        self.name = slab.name

        element = bulk.atoms.get_chemical_symbols()[0]
        self.bulk_element = element
        n = slab.elements[element] / bulk.elements[element]
        self.ratio = n

        self.surface_energy = (slab.E0 - n * bulk.E0) / (2 * self.area)

    def __str__(self):
        text = (
            f'{self.name}\n'
            f'surface energy:    {self.surface_energy:{self._float_format}}\n'
            f'  area             {self.area:{self._float_format}}\n'
            f'  slab             {self.slab.E0:{self._float_format}}\n'
            f'{self.ratio:3} x bulk ({self.bulk_element:>2})    {self.ratio * self.bulk.E0:{self._float_format}}\n'
            f'  bulk             {self.bulk.E0:{self._float_format}}\n'
        )
        return text


class ReportCompareSurface(Report):
    def __init__(self, results, bulk, subdir=''):
        super().__init__(subdir)
        self.results = results
        self.bulk = bulk
        # TODO: finish ReportCompareSurface
