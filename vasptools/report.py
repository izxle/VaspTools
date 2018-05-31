from .result import Result
import numpy as np


class Report:
    def __init__(self):
        pass


class ReportSingle(Report):
    def __init__(self, result, reps=None):
        super().__init__()
        self.result = result
        self.reps = reps

    def __str__(self):
        r = self.result

        if self.reps is None:
            oszicar = str(r.oszicar)
        else:
            oszicar = r.oszicar.report(self.reps)

        if isinstance(r.time, float):
            time = f'time: {r.time/3600:8.4f} h | {r.time:9.3f} s'
        else:
            time = r.time

        text = (
            f'{r.name}\n'
            f'{oszicar}\n'
            f'{time}')

        return text


class ReportCompare(Report):
    _line_lenght = 62
    def __init__(self, results, reps=('F', 'time')):
        super().__init__()
        self.results = results
        if not reps:
            reps = ('F', 'time')
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

            if rep == 'time':
                nan_mask = np.isnan(values)
                vals = values[nan_mask == False]
                relative_values = np.zeros(len(values))
                if len(vals) > 0:
                    max_val = max(vals)
                    min_val = min(vals)
                    relative_values = (vals - min_val) * self._line_lenght / (max_val - min_val)
                relative_values[nan_mask] = self._line_lenght

            else:
                max_val = max(values)
                min_val = min(values)
                relative_values = (values - min_val) * self._line_lenght / (max_val - min_val)

            text += f' name       | {rep:9} |\n'
            for res, rval in zip(self.results, relative_values):
                text += (f'{res.name[:11]:11} | {res.get(rep):9.3f} |'
                         f'{"*" * int(round(rval))}\n')
            text += f"{'':25}{'':->{self._line_lenght}}>\n"
        return text


class ReportAdsorption(Report):
    def __init__(self):
        super().__init__()


class ReportSurface(Report):
    def __init__(self):
        super().__init__()

