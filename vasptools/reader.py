
from .result import Result
from os import path, walk
import re

try:
    from ase.io import read as read_xml
except ImportError:
    raise ImportError('ase was not found.')

import logging

logger = logging.getLogger('log')


def read(filename, directory='.', ignore=[], subdir='', **kwargs):

    directories = getdirs(directory)

    # remove unwanted directories
    for dirname in ignore:
        directories.remove(dirname)

    if directories:
        result = read_directories(filename, directories, **kwargs)
    else:
        result = read_file(filename)
    return result


def read_file(filename):
    name = path.basename(filename)
    atoms = read_xml(filename)
    result = Result(name=name, atoms=atoms)
    return result


def read_directories(filename, directories):
    results = []
    for dirname in directories:
        filename = path.join(dirname, filename)
        result = read_file(filename)
        results.append(result)

    return results


def hasdirs(fpath):
    root, directories, files = next(walk(fpath))
    return bool(directories)


def getdirs(fpath):
    return next(walk(fpath))[1]


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


def read_oszicar(directory):
    filename = path.join(directory, 'OSZICAR')
    with open(filename, 'r') as f:
        text = f.read()

    matches = [match.groupdict()
               for match in oszicar_regex.finditer(text)]

    logger.debug(f'{len(matches)} matches found.')
    logger.debug(f'matches:\n{matches}')

    # TODO: parse matches

    return
