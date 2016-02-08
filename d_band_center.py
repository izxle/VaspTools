#!/bin/env python

from os import path, getcwd, listdir
import numpy as np
import argparse
from ase.io import read

def getDOSdata(nam, atoms, write=False):
    with open(nam, "r") as f:
        lines = f. readlines()
    natoms = int(lines[0].split()[0])
    nedos = int(lines[5].split()[2])
    efermi = float(lines[5].split()[3])
    columns = len(lines[nedos + 7].split())
    spin = columns in [7, 9, 19, 33] # from henkelman
    lines = lines[5:]
    # 'correct' data
    res = []
    for i in xrange(natoms + 1):
        if atoms:
            if i not in atoms:
                continue
        # get raw data
        raw_data = np.array([line.split() for line in lines[1: nedos]], float)
        lines = lines[nedos + 1:]
        # 'correct' data
        raw_data[:, 0] -= efermi
        if i == 0:
            data = raw_data
            if spin:
                data[:, 2] *= -1
                data[:, 4] *= -1
        else:
            if spin:
                data = np.empty((nedos - 1, 7))
                data[:, :2] = raw_data[:, :2]
                data[:, 2] = -1 * raw_data[:, 1]
                if columns == 19:
                    data[:, 3] = np.sum(raw_data[:, 3:8:2], 1)
                    data[:, 4] = -1 * np.sum(raw_data[:, 4:9:2], 1)
                    data[:, 5] = np.sum(raw_data[:, 9:18:2], 1)
                    data[:, 6] = -1 * np.sum(raw_data[:, 10:19:2], 1)
                elif columns == 7:
                    data[:, 3:] = raw_data[:, 3:]
                    data[:, 4] *= -1
                    data[:, 6] *= -1
                else:
                    raise ValueError('Unsupported DOS file with {} columms at '
                                     'atom number {}'.format(colums, i))
            else:
                if columns == 9:
                    data = np.empty((nedos - 1, 4))
                    data[:, :2] = raw_data[:, :2]
                    data[:, 2] = -1 * raw_data[:, 1]
                    data[:, 3] = np.sum(raw_data[:, 3:5], 1)
                    data[:, 4] = -1 * np.sum(raw_data[:, 5:9], 1)
                elif columns == 4:
                    data = raw_data
                else:
                    raise ValueError('Unsupported DOS file with {} columms at '
                                     'atom number {}'.format(colums, i))
        res.append(data)
        if write:
            # format data
            txt = '\n'.join([' '.join(['{:12.8f}'.format(col)
                                       for col in line]) 
                             for line in data])
            # write data
            with open("DOS" + str(i), "w") as fdos:
                fdos.write(txt)
    return res
    
def writeDosSum(DOSdata, sum_file):
    ne = len(DOSdata[1])
    nc = len(DOSdata[1][0])
    data = np.empty((ne, nc + 2))
    data[:, 0] = DOSdata[0][:, 0]
    data[:, 1:-2] = np.add.reduce(DOSdata[1:])[:, 1:]
    data[:, -2] = np.add.reduce(data[:, 1:6:2], 1)
    data[:, -1] = np.add.reduce(data[:, 2:7:2], 1)
    
    txt = '\n'.join([' '.join(['{:15.8f}'.format(col)
                              for col in line]) 
                    for line in data])
    with open(sum_file, 'w') as fdos:
        fdos.write(txt)

def getDataFromSum(sum_file):
    data = {}
    data['raw'] = np.loadtxt(sum_file, unpack=True)
    n_columns = len(data['raw'])
    maxL = int(n_columns / 2) - 2
    data['vals'] = data['raw'][0]
    
    orbitals = ['s', 'p', 'd', 'f']
    for i in xrange(1, n_columns, 2):
        tmp = {'+': data['raw'][i],
               '-': data['raw'][i + 1]}
        if i / 2 <= maxL:
            data[orbitals[int(i / 2)]] = tmp
        else:
            data['sum'] = tmp
    return data

def getWeightedData(data, orbital):
    res = [np.array([data[orbital][s][i] * data["vals"][i]
                    for i in range(len(data[orbital][s]))])
           for s in ["+", "-"]]
    res.append([res[0][i] + res[1][i] for i in range(len(res[0]))])
    return res

def get_band_centers(data, orbital):
    res = []
    data['w'] = {}
    data['center'] = {}
    n = len(data[orbital]["+"])
    for s in ["+", "-"]:
        data['w'][s] = np.array([data[orbital][s][i] * data["vals"][i]
                                 for i in range(n)])
        data['center'][s] = sum(data['w'][s]) / sum(data[orbital][s])
    data['center']['avg'] = sum(data['center'].itervalues()) / 2
    return data['center']

def getArgs(args):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    nam = 'DOSCAR'
    parser.add_argument('file', nargs='?', default=nam,
                        help='name of the DOS file to read')
    parser.add_argument('orbital', nargs='?', default="d")
    parser.add_argument('--sum',
                        help='name of the DOS.SUM file to use')
    parser.add_argument('--sum-name', dest='sum_name',
                        help='Identifier for the DOS.SUM file to be written')
    parser.add_argument('-n', nargs='+', default = [],
                        help='The index number of the atoms to be read')
    parser.add_argument('-l', nargs='+', default = [],
                        help='Read info of atoms in selected layers')
    parser.add_argument('--layers', type=int, default = 4,
                        help='Number of layers in structure')
    parser.add_argument('-f', default=getcwd(),
                        help='directory where script will be ran')
    parser.add_argument('--write', action='store_true', default=False,
                        help='write a DOSi file for each atom')

    if args:
        res = parser.parse_args(args.split())
    else:
        res = parser.parse_args()
    
    pre = res.f
    res.file = path.join(pre, res.file)
    
    if res.l:
        nam = 'CONTCAR' if 'CONTCAR' in listdir(res.f) else 'POSCAR'
        nam = path.join(pre, nam)
        struct = read(nam)
        max_val = max([a.z for a in struct])
        th = max_val / res.layers
        struct.set_tags([min(int(a.z / th) + 1, res.layers) for a in struct])
        res.n = [a.index + 1 for a in struct if a.tag in res.l]
        
    if not res.n: res.n = 'all'
    
    return res

def parseIntSet(inp):
    res = []
    limits = []
    for elm in inp:
        try:
            tmp = int(elm)
            res.append(tmp)
            limits.append(tmp)
        except ValueError:
            init, fin = map(int, elm.split('-'))
            limits.append((init, fin))
            res += range(init, fin + 1)
    s_atoms = '.'.join([str(elm) if isinstance(elm, int) else
                        '{}.to.{}'.format(elm[0], elm[1])
                        for elm in limits])
    return res, s_atoms

def main(argv=None):
    args = getArgs(argv)
    if args.sum:
        sum_file = args.sum
    else:
        if args.l:
            atoms = args.n
            s_atoms = 'layer.' + '.'.join([str(a) for a in args.l])
        elif isinstance(args.n, str):
            s_atoms = args.n
            atoms = None
        else:
            atoms, s_atoms = parseIntSet(args.n)
        DOSdata = getDOSdata(args.file, atoms, args.write)
        if args.sum_name:
            s_atoms = args.sum_name
        sum_file = path.join(args.f, 'DOS.SUM.' + s_atoms)
        writeDosSum(DOSdata, sum_file)
        
    data = getDataFromSum(sum_file)
    centers = get_band_centers(data, args.orbital)
    for k, v in centers.iteritems():
        print '{:>4} {:>15.11f}'.format(k, v)
    
if __name__ == '__main__':
    main()
