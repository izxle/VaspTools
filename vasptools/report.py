from .result import Result
import numpy as np


class Report:
    def __init__(self):
        pass


class ReportSingle(Report):
    def __init__(self, result):
        super().__init__()
        self.result = result

    def __str__(self):
        r = self.result
        text = (
            f'{r.name}\n'
            f'{r.oszicar}'
            f'time: {r.time/3600:8.4f} h | {r.time:9.3f} s')
        return text


class ReportCompare(Report):
    def __init__(self, results, reps=('F', 'time')):
        super().__init__()
        self.results = results
        self.reps = reps
        self.values = dict()
        for rep in reps:
            self.values[rep] = []
            for res in results:
                self.values[rep].append(res.get(rep))

    def __str__(self):
        text = ''
        for rep in self.reps:
            text += '\n'
            values = np.array(self.values[rep], dtype=float)
            max_val = max(values)
            min_val = min(values)
            relative_values = (values - min_val) * 62 / (max_val - min_val)
            text += f' name       | {rep:9} |\n'
            for res, rval in zip(self.results, relative_values):
                text += (f'{res.name[:11]:11} | {res.get(rep):9.3f} |'
                         f'{"*" * int(round(rval))}\n')
            text += f"{'':25}{'':->62}>\n"
        return text


class ReportAdsorption(Report):
    def __init__(self):
        super().__init__()


class ReportSurface(Report):
    def __init__(self):
        super().__init__()

