
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
    # TODO: read other files if xml isn't ready
    logger.info(f'reading {filename}')
    atoms = read_xml(filename)
    directory, outname = path.split(filename)
    name = path.abspath(directory)
    oszicar = read_oszicar(directory)
    time = read_time(directory)

    result = Result(name=name, atoms=atoms, oszicar=oszicar, time=time)
    logger.debug(f'result:\n{result}')
    return result


def read_directories(filename: str, directories: list, subdir: str):

    results = []
    try:
        directories.sort(key=float)
    except ValueError:
        directories = sorted(directories)

    for dirname in directories:
        directory = path.join(dirname, subdir)
        file_path = path.join(directory, filename)
        if all_vasp_outputs(directory, filename):
            logger.info(f'attempting to read {file_path}')
            result = read_result(file_path)
            logger.debug(f'appending result:\n{results}')
            results.append(result)
        else:
            logger.info(f'skipping {dirname}: no valid output files')

    return results


def all_vasp_outputs(fpath, filename='vasprun.xml'):
    outputfiles = ['OSZICAR', filename, 'OUTCAR']
    return all(path.isfile(path.join(fpath, fname))
               for fname in outputfiles)


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
    logger.info(f'reading OSZICAR in {directory}')
    filename = path.join(directory, 'OSZICAR')
    oszicar = Oszicar(filename=filename)
    logger.debug(f'OSZICAR:\n{oszicar}')

    # logger.debug(f'{len(matches)} matches found.')
    # logger.debug(f'matches:\n{matches}')

    return oszicar
