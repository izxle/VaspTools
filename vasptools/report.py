from .result import Result


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
            f'{r.oszicar}\n')
        return text


class ReportCompare(Report):
    def __init__(self):
        super.__init__()


class ReportAdsorption(Report):
    def __init__(self):
        super.__init__()


class ReportSurface(Report):
    def __init__(self):
        super.__init__()

