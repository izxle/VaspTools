
from .result import Result, Oszicar
from os import path, walk
import re
from glob import glob

try:
    from ase.io import read as read_xml
except ImportError:
    raise ImportError('ase was not found.')

import logging

logger = logging.getLogger('log')


def read(filename='vasprun.xml', directory='.', ignore=None, subdir=''):

    directories = getdirs(directory)

    # remove unwanted directories
    if ignore is not None:
        for dirname in ignore:
            abs_dirname = path.abspath(path.join(directory, dirname))
            directories.remove(abs_dirname)


    if directories:
        result = read_directories(filename, directories, subdir)
    else:
        file_path = path.join(directory, filename)
        abs_path = path.abspath(file_path)
        result = read_result(abs_path)
    return result


def read_result(filename):
    atoms = read_xml(filename)
    directory, outname = path.split(filename)
    name = path.abspath(directory)
    oszicar = read_oszicar(directory)
    time = read_time(directory)

    result = Result(name=name, atoms=atoms, oszicar=oszicar, time=time)
    return result


def read_directories(filename: str, directories: list, subdir: str):

    results = []
    try:
        directories.sort(key=float)
    except ValueError:
        directories = sorted(directories)

    for dirname in directories:
        file_path = path.join(dirname, subdir, filename)
        result = read_result(file_path)
        results.append(result)

    return results


def hasdirs(fpath):
    # root, directories, files = next(walk(fpath))
    return bool(glob(fpath + '/*/'))


def getdirs(fpath):
    directories = [path.abspath(p)
                   for p in glob(fpath + '/*/')]
    return directories


def float_match_values(match):
    return {k: float(v) for k, v in match.groupdict().items()}


def read_time(directory):
    filename = path.join(directory, 'OUTCAR')

    # TODO: read more from OUTCAR, maybe create OUTCAR object
    with open(filename, 'r') as f:
        text = f.read()

    regex = re.compile('Total CPU time used \(sec\):\s*([+\-.0-9E]+)')
    m = regex.search(text)
    if m:
        group = m.group(1)
        time = float(group)
    else:
        time = float('NaN')

    return time


def read_oszicar(directory):
    filename = path.join(directory, 'OSZICAR')
    oszicar = Oszicar(filename=filename)

    # logger.debug(f'{len(matches)} matches found.')
    # logger.debug(f'matches:\n{matches}')

    return oszicar
