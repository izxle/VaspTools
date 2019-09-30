from .result import Result
import numpy as np
from os import path
from numbers import Number
from collections import Counter


class Report:
    _float_format = '9.4f'
    _name_len = 11
    def __init__(self, subdir=''):
        self.subdir = subdir
        self.time = 0

    def time_to_str(self, time, units=True):
        if not isinstance(time, Number) or np.isnan(time):
            return "Didn't finish"

        elif time < 60:
            rel_time = time
            formatter = '6.3f'
            unit = 's'
        elif time / 60 < 60:
            rel_time = time / 60
            unit = 'min'
            formatter = '7.4f'
        else:
            rel_time = time / 3600
            unit = 'h'
            formatter = '8.4f'

        text = f'{rel_time:{formatter}}'

        if units:
            text += f' {unit}'
            if unit != 's':
                text += f' | {time:9.2f} s'

        return text


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

        time = self.time_to_str(r.time)

        text = (
            f'{r.name}\n'
            f'{results}\n'
            f'{time}')

        return text


class ReportCompare(Report):
    _line_len = 62
    _float_format = '9.3f'
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

        # TODO: sort results to name

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
                # TODO: fix bug when name is one character
                text += (f'{name[:self._name_len]:{self._name_len}} | {res.get(rep):{self._float_format}} |'
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
        ads_en = (whole.E0 - slab.E0 - n * ads.E0) / n
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

    def __lt__(self, other):
        return self.ads_en < other.ads_en

    def __gt__(self, other):
        return self.ads_en > other.ads_en

    def __eq__(self, other):
        return (self.name, self.ads_en) == (other.name, other.ads_en)


class ReportCompareAdsorption(Report):
    def __init__(self, results, slab, ads, subdir='', relative=False):
        super().__init__(subdir)
        self.slab = slab
        self.ads = ads
        self.results = results
        self.relative = relative

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
        if relative:
            if relative is True:
                ref = min(ads_energies, key=ads_energies.get)
                self.reference = ref
                ref_en = ads_energies[ref].ads_en
            else:
                ref_en = relative
            self.ref_en =ref_en


    def __str__(self):
        text = f'{"Relative " if self.relative else ""}Adsorption Energies\n'

        for name, report in self.ads_energies.items():
            energy = report.ads_en - self.ref_en if self.relative else report.ads_en
            text += f'{name[:self._name_len]:{self._name_len}} {energy:{self._float_format}}\n'

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
    def __init__(self, results, bulk, area=None, subdir=''):
        super().__init__(subdir)
        self.results = results
        self.bulk = bulk

        surf_energies = dict()
        for slab in results:
            report = ReportSimpleSurface(slab=slab,
                                         bulk=bulk,
                                         area=area)
            # name handling
            root, basename = path.split(report.name)
            if basename == self.subdir:
                name = root
            else:
                name = report.name
            name = path.basename(name)
            surf_energies[name] = report

        self.surf_energies = surf_energies

    def __str__(self):
        text = 'Surface Energies\n'

        for name, report in self.surf_energies.items():
            text += f'{name[:self._name_len]:{self._name_len}} {report.surface_energy:{self._float_format}}\n'

        return text
