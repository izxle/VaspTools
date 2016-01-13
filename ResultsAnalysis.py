# -*- coding: utf-8 -*-

#!/bin/env/ python

# TODO: replace my functions with ones from ASE

from numpy import sort, array, polyfit
import sys, os, re
import argparse
########
#TODO: add scipy @ PC-YLN-U
#REMOVE @ PC-YLN-U
from numpy import linspace
from scipy.optimize import leastsq, minimize_scalar
#import matplotlib.pyplot as plt
########

class Calc(object):
    def __init__(self, f_path, v, raw=False, i=[], reps=[], subdir='',
                 *args, **kw):
        self.f_path = f_path
        self.nam = os.path.basename(f_path.rstrip('/\\'+subdir))
        self.ignore = i # ignored folders
        self.v = v # verbosity
        self.raw = raw
        self.reps = reps
        self.subdir = subdir

class Check(Calc):
    def __init__(self, pad='', *args, **kw):
        Calc.__init__(self, *args, **kw)
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
        #TODO: ignore comments
        #path = self.getPath('CONTCAR')
        #if self.v: print '{0}reading CONTCAR'.format(self.pad)
        path = self.getPath('POSCAR')
        if self.v: print '{0}reading POSCAR'.format(self.pad)
        with open(path, 'r') as f:
            #TODO: read more data
            # like how many atoms from which element
            n_atoms = sum(map(int, f.readlines()[6].split()))
            if self.v: print "{0}n_atoms: {1}".format(self.pad, n_atoms)
        self.n_atoms = n_atoms

    def _readOSZICAR(self):
        # regex to get data
        rex = '(?:[A-Z]{3}:\s*(?P<n>[0-9]+)[+\-.0-9E ]+\s*)?' # steps
        rex += '(?P<n_iter>[0-9]+)\s*' # convergence number
        rex += 'F=\s*(?P<F>[+\-.0-9E]+)\s*' # total free energy
        rex += 'E0=\s*(?P<E0>[+\-.0-9E]+)\s*' # energy for sigma -> 0
        rex += '(?:d E =\s*(?P<dE>[+\-.0-9E]+)\s*)?' # E diff
        rex += '(?:mag=\s*(?P<m>[+\-.0-9E]+)\s*)?' # mag
        if self.v>2: print "{0}regex: {1}".format(self.pad, rex)
        regex = re.compile(rex)
        # read file
        try:
            self._search('OSZICAR', regex)
        #TODO: distinguish between no file and no match?
        except IOError:
            if self.v: print "ERROR, no matches found."
            self.F = 0
            self.n_iter = 0
            self.dE = 0
            self.E0 = 0
            self.m = 0

    def _readOUTCAR(self):
        # regex to get data
        #TODO: read more data
        rex = 'Total CPU time used \(sec\):\s*(?P<t>{num})'
        rex = rex.format(num='[+\-.0-9E]+')
        if self.v>2: print "{0}regex: {1}".format(self.pad, rex)
        regex = re.compile(rex)
        # read file
        try:
            self._search('OUTCAR', regex)
        #TODO: distinguish between no file and no match?
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
            #TODO: distinguish between no file and no match?
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
        last_match = dict([(k, float(val))
                           for k, val in  matches[-1].iteritems()])
        if v>3: print "last_match:", last_match
        # store last match
        self.update(**last_match)
        # store more matches
        if nam=='OSZICAR':
            self.matches = matches
            self.F_n = self.F / self.n_atoms
    #def compare(self, comp):
    #    k = ""
    #    if comp=="dE":
    #        k = "dE"
    #
    #    data = array([m.get(k, 0.0) for m in self.matches])
    #    print data


    def getPath(self, nam):
        return os.path.join(self.f_path, nam)

    def update(self, **stuff):
        #TODO: better way?
        vars(self).update(**stuff)

    def vars(self):
        return dict(vars(self))

    def get(self, key):
        return self.vars()[key]

    def __str__(self):
        if self.raw: return str(self.vars())
        res = ''
        if self.reps:
            min_lenght = 6
            for r in self.reps:
                lenght = max(min_lenght, len(str(self.matches[0][r])))
                res += ('{:>'+str(lenght)+'}').format(r) + " "
            res += "\n"
            for m in self.matches:
                for r in self.reps:
                    lenght = max(min_lenght, len(m[r]))
                    res += ('{:>'+str(lenght)+'}').format(m[r]) + " "
                res += "\n"
        else:
            for k, v in self.vars().iteritems():
                # unwanted keys
                if k in 'vpadignorerawmatchesreps' and k != 't': continue
                # wanted keys
                if k in 'FadE0t':
                    res += "{0:>7}: {1:.3f}\n".format(k, float(v))
                else:
                    res += "{0:>7}: {1}\n".format(k, v)
            res = res[:-1]
        return res
#..

class Compare(Calc):
    def __init__(self, pad='', *args, **kw):
        """
        Compares data in calcs in one dictionary
        """
        Calc.__init__(self, *args, **kw)
        if self.v>1: print '{0}in compare'.format(pad)
        if self.v: print '{0}f_path: {1}'.format(pad, self.f_path)
        self.pad = pad

        self._run()
        self._formatData()

    def _run(self):
        self.calcs = []
        # get dirs
        dirs = next(os.walk(self.f_path))[1]
        # ignore templates
        if "template" in dirs: dirs.remove("template")
        # sort list
        try:
            # mutate list
            dirs.sort(key=float)
        except ValueError:
            dirs = sort(dirs)
        if self.v: print "{0}dirs: {1}".format(self.pad, dirs)
        # get data
        for subdir in dirs:
            if self.v: print "{0}in {1}".format(self.pad, subdir)
            if subdir in self.ignore: continue
            f_path = self.getPath(subdir, self.subdir)
            calc = Check(f_path=f_path, pad=self.pad+'  ',
                         v=self.v, raw=self.raw, subdir=self.subdir)
            self.calcs.append(calc)

    def getPath(self, nam, subdir=''):
        return os.path.join(self.f_path, os.path.join(nam, subdir))

    def _formatData(self):
        reps = self.reps
        nams = []
        vals = dict([(rep, []) for rep in reps])
        for calc in self.calcs:
            try:
                nams.append(calc.nam)
                for rep in reps:
                    try:
                        val = float(calc.get(rep))
                    except AttributeError:
                        if self.v:
                            print "{0}{1} has no '{2}'".format(self.pad,
                                                                calc.nam, rep)
                        raise ZeroDivisionError
                    #if rep == "F_n": val /= calc.n_atoms
                    vals[rep].append(val)
            except ZeroDivisionError:
                nams.pop()
        if self.v>2:
            print "{0}nams:     {1}".format(self.pad, nams)
            for rep in reps:
                print "{0}{1:<4}: {2}".format(self.pad, rep, vals[rep])
        self.nams = nams
        self.vals = vals

    def __str__(self):
        if self.raw:
            return str([str(rep) for rep in self.reps])
        #FORMAT for displaying
        res = ""
        for rep in self.reps:
            data = array(self.vals[rep])
            if rep == 'F' or rep == 'F_n':
                header = 'FEnergy'
                data *= -1
            elif rep == 't':
                header = 'Time  s'
            pos_data = data[data > 0.0]
            if len(pos_data)==0:
                if rep == 'F' or rep == 'F_n':
                    print "ERROR: all F >= 0."
                elif rep=='t':
                    print "ERROR: all t <= 0."
                #TODO: display positive values for F?
                maxV = 0
                minV = 0
            else:
                maxV = max(pos_data)
                minV = min(pos_data)

            relV = (data - minV) * 64 / (maxV - minV)
            relV.clip(0)

            if self.v>1: print 'data to print:', data

            res += '  nam | {0} |\n'.format(header)
            res += '\n'.join(['{0:>5} | {1:7.5f} |{2}'
                              .format(nam, val, "*" * int(rV))
                              for nam, val, rV in zip(self.nams, data, relV)])
            res += "\n" + ' '*16 + '-'*64 + '>\n'
            res += ' '*14
            res += ''.join(["{0:<5.1f}".format(
                            int((ix*(maxV - minV)/64) + minV))
                            for ix in range(0,64,5)])
            res += '\n'

        return res
#..

class Murnaghan(Calc):
    def __init__(self, skip=0, plot=False, *args, **kw):
        Calc.__init__(self, *args, **kw)
        self.args = args
        self.kw = kw
        self.skip = skip
        self.plot = plot
        self._compare()
        self.calc()

    def _compare(self):
        comp = Compare(*self.args, **self.kw)
        self.comp = comp
        self.lenghts = array(map(lambda x: float(x), comp.nams))
        self.vols = self.lenghts ** 3
        self.energies = comp.vals['F']

    def calc(self):
        v = self.vols
        e = self.energies
        n = len(e)
        # make a vector to evaluate fits on with a lot of points so it looks smooth
        vfit = linspace(min(v),max(v),100)
        # parabolic fit
        a,b,c = polyfit(v[:n - self.skip], e[:n - self.skip], 2)
        # initial guesses
        v0 = -b/(2*a)
        e0 = a*v0**2 + b*v0 + c
        b0 = 2*a*v0
        bP = 4
        # initial guesses in the same order used in the Murnaghan function
        x0 = [e0, b0, bP, v0]

        murnpars, ier = leastsq(self.objective, x0, args=(e, v))

        self.murnpars = murnpars

        self.minE = murnpars[0]
        self.minV = murnpars[3]
        self.minLenght = self.minV**(1.0 / 3)
        self.BULKeVA = murnpars[1]
        self.BULKGPa = murnpars[1] * 160.21773
        # more precise
        def f(x):
            return self.Murnaghan(self.murnpars, x)

        self.min = minimize_scalar(f)

        self.minE = self.min.fun
        self.minV = self.min.x
        self.minLenght = self.minV**(1.0 / 3)

        if self.plot:
            # now we make a figure summarizing the results
            plt.plot(v,e,'ro')
            plt.plot(vfit, self.Murnaghan(murnpars, vfit), label='Murnaghan fit')
            plt.xlabel('Volume ($\AA^3$)')
            plt.ylabel('Energy (eV)')
            plt.legend(loc='best')

            # add some text to the figure in figure coordinates
            ax = plt.gca()
            plt.text(0.4,0.5,'Min volume = %1.2f $\AA^3$' % murnpars[3],
                transform = ax.transAxes)
            plt.text(0.1,0.6, ('Bulk modulus = %1.2f eV/$\AA^3$ = %1.2f GPa' %
                            (murnpars[1], murnpars[1]*160.21773)),
                transform = ax.transAxes)
            plt.show()


    def Murnaghan(self, parameters, vol):
        '''
        given a vector of parameters and volumes, return a vector of energies.
        equation From PRB 28,5480 (1983)
        '''
        E0 = parameters[0]
        B0 = parameters[1]
        BP = parameters[2]
        V0 = parameters[3]

        E = E0 + B0*vol/BP*(((V0/vol)**BP)/(BP-1)+1) - V0*B0/(BP-1.)

        return E

    # we define an objective function that will be minimized
    def objective(self, pars, y, x):
        #we will minimize this function
        err =  y - self.Murnaghan(pars, x)
        return err

    def __str__(self):
        res = "Minimum\n"
        res += "lenght: {0:7.5f}  volume: {1:9.5f}  energy: {2:-6.3f}\n"
        res += "Bulk Modulus: {3:6.3e} eV/A^3   {4:5.3f} GPa"
        return res.format(self.minLenght, self.minV, self.minE,
                           self.BULKeVA, self.BULKGPa, A=u"\u212B")


def getArgs(argv=[]):
    kw = {'description': '',
          'formatter_class': argparse.ArgumentDefaultsHelpFormatter}
    parser = argparse.ArgumentParser(**kw)

    opts = {('-v',): {'action':'count', 'help': 'verbosity',
                      'default': 0},
            ('--verb', '--verbose'): {'type': int, 'dest': 'v',
                                      'default': 0},
            ('-s', '--skip'): {'type': int, 'dest': 'skip',
                               'default': 0, 'help': "only for Murnaghan."},
            ('-p', '--path'): {'dest': 'f_path', 'default': os.getcwd()},
            ('-f', '--folder'): {'dest': 'f_path',
                                 'default': os.getcwd()},
            ('--sd', '--subdir', '--sub-directory'): {'dest': 'subdir',
                                                      'default': ''},
            ('-i', '--ignore'): {'nargs': '+', 'dest': 'i', 'default': []},
            ('--rep', '--reps', '--report'): {'nargs': '+', 'dest': 'reps',
                                              'default': []},
            ('-r', '--raw'): {'action': 'store_true', 'dest': 'r',
                              'default': False}, # raw, list type data
            ('-m', '--murnaghan'): {'action': 'store_true', 'default': False,
                                    'dest': 'm'},
            ('-g', '--graph', '--plot'): {'action': 'store_true',
                                          'default': False, 'dest': 'plot'}
           }
    for arg, kwarg in opts.items():
        parser.add_argument(*arg, **kwarg)

    args = vars(parser.parse_args(argv))
    if args['v']: print 'args:', args
    for k, v in dict(args).iteritems():
        if v is None:
            del args[k]
    if args['v']>1: print "None values deleted", args

    return args

def main(argv=[]):
    kwargs = getArgs(argv)
    hasdirs = next(os.walk(kwargs['f_path']))[1]
    if not hasdirs:
        kwargs['pad'] = "  "
        res = Check(**kwargs)
    elif kwargs['m']:
        res = Murnaghan(**kwargs)
        print res.murnpars
    else:
        if not kwargs['reps']:
            kwargs['reps'] = ['F', 't']
        res = Compare(**kwargs)
    print res


if __name__=='__main__':
    main(sys.argv[1:])
