
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


def read(filename, directory='.', ignore=[], subdir=''):

    directories = getdirs(directory)

    # remove unwanted directories
    for dirname in ignore:
        directories.remove(dirname)

    file_path = path.join(directory, filename)

    if directories:
        result = read_directories(file_path, directories, subdir)
    else:
        result = read_result(file_path)
    return result


def read_result(filename):
    path.split(filename)
    atoms = read_xml(filename)
    directory, outname = path.split(filename)
    root, basename = path.split(directory)
    oszicar = read_oszicar(directory)
    result = Result(name=basename, atoms=atoms, oszicar=oszicar)
    return result


def read_directories(filename: str, directories: list, subdir: str):

    results = []
    for dirname in directories:
        file_path = path.join(dirname, subdir, filename)
        result = read_result(file_path)
        results.append(result)

    return results


def hasdirs(fpath):
    # root, directories, files = next(walk(fpath))
    return bool(glob(fpath + '/*/'))


def getdirs(fpath):
    return glob(fpath + '/*/')


oszicar_regex_string = (  # electronic step
    '(?:[A-Z]{3}:\s*(?P<e_step>[0-9]+)[+\-.0-9E ]+\s*)?' 
    '(?P<io_step>[0-9]+)\s*'  # ionic step
    '(?:T=\s*(?P<Temp>[.0-9]+)\s*)?'  # temperature
    '(?:E=\s*(?P<E>[+\-.0-9E]+)\s*)?'  # total energy (Potential+Kinetic)
    'F=\s*(?P<F>[+\-.0-9E]+)\s*'  # total free energy
    'E0=\s*(?P<E0>[+\-.0-9E]+)\s*'  # energy for sigma -> 0
    '(?:d E =\s*(?P<dE>[+\-.0-9E]+)\s*)?'  # energy difference
    '(?:EK=\s*(?P<EK>[+\-.0-9E]+)\s*)?'  # Kinetic energy
    '(?:SP=\s*(?P<SP>[+\-.0-9E]+)\s*)?'  # thermostat PotentialEnergy
    '(?:SK=\s*(?P<SK>[+\-.0-9E]+)\s*)?'  # thermostat KineticEnergy
    '(?:mag=\s*(?P<m>[+\-.0-9E]+)\s*)?'  # magnetic moment
    )
oszicar_regex = re.compile(oszicar_regex_string)
float_params = ['F', 'F_n', 'E0', 'E', 'Temp', 'area', 'm', 'dE', 't']


def float_match_values(match):
    return {k: float(v) for k, v in match.groupdict().items()}


def read_oszicar(directory):
    filename = path.join(directory, 'OSZICAR')
    oszicar = Oszicar(filename=filename)

    # logger.debug(f'{len(matches)} matches found.')
    # logger.debug(f'matches:\n{matches}')

    return oszicar
