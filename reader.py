from re import compile
from os import path, walk, listdir
from numpy import array, cross

class Check(object):
    def __init__(self, f_path, reps=[], subdir='',
                 pad='', v=False, *args, **kw):
        """
        f_path: absolute path of directory to read
        reps: list of values to report [F, F_n, t, n_iter, ...]
        subdir: subdirectory not part of nam
        v: verbosity
        """
        self.f_path = f_path
        self.nam = path.basename(f_path.rstrip(subdir).rstrip('/\\'))
        self.subdir = subdir
        self.v = v
        self.reps = reps
        self.to_float = ['F', 'F_n', 'E0', 'E', 'Temp', 'area', 'm', 'dE', 't']

        if self.v>1: print '{0}in calc'.format(pad)
        self.pad = pad + "  "
        if self.v: print '{0}f_path: {1}'.format(self.pad, self.f_path)

        # get n_atoms
        self._readPOSCAR()
        # get energy data
        self._readOSZICAR()
        # get time data
        self._readOUTCAR()
        if self.v>1: print '{0}end calc'.format(self.pad[:-2])

    def _readPOSCAR(self):
        # TODO: ignore comments
        try:
            nams = listdir(self.f_path)
        except OSError, e:
            raise IOError(e if self.v else '{} does not exist'.format(self.subdir))
        for nam in ['POSCAR', 'CONTCAR']:
            if nam in nams: break
            raise IOError('No structure files detected')
        path = self.getPath(nam)
        if self.v: print '{0}reading structure'.format(self.pad)
        with open(path, 'r') as f:
            # TODO: read more data
            # with ASE
            lines =  f.readlines()
            if not lines: raise IOError('No POSCAR found')
            a = array(map(float, lines[2].split()))
            b = array(map(float, lines[3].split()))
            elms = lines[5].split()
        nums = map(int, lines[6].split())
        n_atoms = sum(nums)
        if self.v: print "{0}n_atoms: {1}".format(self.pad, n_atoms)

        self.area = cross(a, b)[2]
        self.elements = {elms[i]: nums[i] for i in range(len(elms))}
        self.n_atoms = n_atoms

    def _readOSZICAR(self):
        # regex to get data
        rex = '(?:[A-Z]{3}:\s*(?P<e_step>[0-9]+)[+\-.0-9E ]+\s*)?' #
        rex += '(?P<io_step>[0-9]+)\s*' # ionic step
        rex += '(?:T=\s*(?P<Temp>[.0-9]+)\s*)?' # Temp
        rex += '(?:E=\s*(?P<E>[+\-.0-9E]+)\s*)?' # Total E (+Kinetic)
        rex += 'F=\s*(?P<F>[+\-.0-9E]+)\s*' # Total Free Energy
        rex += 'E0=\s*(?P<E0>[+\-.0-9E]+)\s*' # energy for sigma -> 0
        rex += '(?:d E =\s*(?P<dE>[+\-.0-9E]+)\s*)?' # E diff
        rex += '(?:EK=\s*(?P<EK>[+\-.0-9E]+)\s*)?' # Kinetic Energy
        rex += '(?:SP=\s*(?P<SP>[+\-.0-9E]+)\s*)?' # thermostat PE
        rex += '(?:SK=\s*(?P<SK>[+\-.0-9E]+)\s*)?' # thermostat KE
        rex += '(?:mag=\s*(?P<m>[+\-.0-9E]+)\s*)?' # magnetic
        if self.v>2: print "{0}regex: {1}".format(self.pad, rex)
        regex = compile(rex)
        # read file
        try:
            self._search('OSZICAR', regex)
        # TODO: distinguish between no file and no match?
        except IOError:
            if self.v: print "ERROR, no matches found."
            self._set_blank()

    def _readOUTCAR(self):
        # regex to get data
        # TODO: read more data
        rex = 'Total CPU time used \(sec\):\s*(?P<t>[+\-.0-9E]+)'
        if self.v>3: print "{0}regex: {1}".format(self.pad, rex)
        regex = compile(rex)
        # read file
        try:
            self._search('OUTCAR', regex)
        # TODO: distinguish between no file and no match?
        except IOError:
             if self.v: print "ERROR, no matches found."
             self.t = 0

    def _search(self, nam, regex):
        pad = self.pad
        v = self.v
        path = self.getPath(nam)
        with open(path, 'r') as f:
            txt = f.read()
            if v: print "{0}.. {1} loaded".format(pad, nam)
        matches = [{k: v for k, v in m.groupdict().iteritems() if not v is None}
                   for m in regex.finditer(txt)]
        if not matches:
            # TODO: distinguish between no file and no match?
            raise IOError
            #raise Exception('No matches found.')
        if v: print '{0}{1} matches found'.format(pad, len(matches))
        if v>2:
            print '{0}matches:'.format(pad)
            pad += "  "
            for m in matches:
                for k, v in m.iteritems():
                    print '{0}{k}: {v}'.format(pad, k=k, v=v)
                print "-----"
        last_match = {k: float(val) if k in self.to_float else int(val)
                      for k, val in  matches[-1].iteritems()}
        if v>3: print "last_match:", last_match
        # store last match
        self.update(**last_match)
        # store more matches
        if nam == 'OSZICAR':
            self.F_n = self.F / self.n_atoms
            for i, m in enumerate(matches):
                matches[i]['F_n'] = '{:.6f}'.format(float(m['F']) /
                                                    self.n_atoms)
            self.matches = matches

    def getPath(self, nam):
        return path.join(self.f_path, nam)

    def update(self, **stuff):
        # TODO: better way?
        vars(self).update(**stuff)

    def vars(self):
        return dict(vars(self))

    def get(self, key, default=None):
        return self.vars().get(key, default)

    def _set_blank(self):
        self.F = 0
        self.io_step = 0
        self.dE = 0
        self.E0 = 0
        self.m = 0
        self.t = 0

    def __str__(self):
        if self.get('raw'): return str(self.vars())
        res = ''
        if self.reps:
            min_lenght = 8
            for r in self.reps:
                lenght = max(min_lenght, len(str(self.matches[0][r])))
                res += ('{:>'+str(lenght)+'}').format(r) + " "
            res = res[:-1] + "\n"
            for m in self.matches:
                for r in self.reps:
                    lenght = max(min_lenght, len(m[r]))
                    res += ('{:>'+str(lenght)+'}').format(m[r]) + " "
                res = res[:-1] + "\n"
        else:
            not_float = ['io_step', 'nam', 'n_atoms']
            # to_float ['F', 'F_n', 'E0', 'E', 'Temp', 'area', 'm', 'dE', 't']
            for k, v in self.vars().iteritems():
                if k == 't':
                    time = "{:.3f} h".format(v/3600) if v else "hasn't finished"
                    res += "{:>7}: {}\n".format(k, time)
                elif k in self.to_float:
                    res += "{:>7}: {:.3f}\n".format(k, v)
                elif k in not_float:
                    res += "{:>7}: {}\n".format(k, v)
                
        return res[:-1]
#..

class Folder(object):
    def __init__(self, f_path, reps=[], subdir='',
                 i=[], pad='', v=False, *args, **kw):
        """
        Compares data in calcs in one dictionary
        """
        self.f_path = f_path
        self.nam = path.basename(f_path)
        self.v = v
        self.subdir = subdir
        self.reps = reps
        self.pad = pad
        self.ignore = i

        if self.v>1: print '{0}in compare'.format(pad)
        if self.v: print '{0}f_path: {1}'.format(pad, self.f_path)

        self._run()

    def _run(self):
        self.calcs = []
        # get dirs
        dirs = next(walk(self.f_path))[1]
        # ignore templates
        for dir in self.ignore:
            if dir in dirs:
                dirs.remove(dir)
            else:
                print "{} does not exist".format(dir)
        # sort list
        try:
            # mutate list
            dirs.sort(key=float)
        except ValueError:
            dirs = sorted(dirs)
        if self.v: print "{0}dirs: {1}".format(self.pad, dirs)
        # get data
        for subdir in dirs:
            if self.v: print "{0}in {1}".format(self.pad, subdir)
            f_path = self.getPath(subdir, self.subdir)
            try:
                calc = Check(f_path=f_path, pad=self.pad+'  ',
                             v=self.v, subdir=self.subdir)
                self.calcs.append(calc)
            except IOError, e:
                print "{}: {}".format(subdir, e)
        self._formatData()

    def getPath(self, nam, subdir=''):
        return path.join(self.f_path, path.join(nam, subdir))

    def _formatData(self):
        nams = []
        vals = {}
        for calc in self.calcs:
            nams.append(calc.nam)
            for rep in self.reps:
                try:
                    vals[rep].append(calc.get(rep, 0))
                except KeyError:
                    vals[rep] = [calc.get(rep, 0)]
        self.nams = nams
        self.vals = vals

    def __str__(self):
        res = ""
        for rep in self.reps:
            # get data
            data = array(self.vals[rep])
            # headers
            if rep == 'F' or rep == 'F_n':
                header = 'FEnergy'
                data *= -1
            elif rep == 't':
                header = 'Time  s'
            else:
                header = rep
            # format data
            pos_data = data[data > 0.0]
            if len(pos_data)==0:
                if rep == 'F' or rep == 'F_n':
                    print "ERROR: all F >= 0."
                elif rep=='t':
                    print "ERROR: all t <= 0."
                # TODO: display positive values for F?
                maxV = 0
                minV = 0
            else:
                maxV = max(pos_data)
                minV = min(pos_data)

            relV = (data - minV) * 62 / (maxV - minV)
            relV.clip(0)

            if self.v>1: print 'data to print:', data

            res += '  nam | {0:>9} |\n'.format(header)
            res += '\n'.join(['{0:>5} | {1:9.5f} |{2}'
                              .format(nam, val, "*" * int(round(rV)))
                              for nam, val, rV in zip(self.nams, data, relV)])
            res += "\n" + ' '*18 + '-'*62 + '>\n'

        return res
#..
