import sys, os, re
from tempfile import mkstemp
from shutil import move

#TODO: separate functions into different scripts
#TODO: use argparse
#TODO: add decorators a print for verbosity

def getPath(nam, f_path=None, v=False):
    f_path = f_path if f_path else os.getcwd()
    if v>2: print '  f_path:', f_path 
    return os.path.join(f_path, nam)

def replace(*args, **kw):
    #just playing with a pythonic way of replacing sed 's///g'
    v = kw['v']
    if v: print '  replace args:', args
    #get useful args
    nam = args[0]
    pattern = args[1]
    subst = args[2]
    file_path = getPath(nam, v=v)
    if v: print '  file path:', file_path
    #display invalid args
    if len(args)>3: print 'Found extra (useless) args:', args[3:]
    #make tmp file
    fh, abs_path = mkstemp()
    #open original file and write replaced patterns to tmp file
    with open(abs_path,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(re.sub(pattern, subst, line))
    #close fh y replace old with new file
    os.close(fh)
    os.remove(file_path)
    move(abs_path, file_path)

def chk(*args, **kw):
    # checks the last enery of a calculation
    v = kw.get('v', False)
    if v: print '  check args:', args, kw
    #get useful args
    nam = kw.get('f', 'OSZICAR')
    POSCAR = kw.get('POSCAR', 'POSCAR')
    if v>2: print '  nam:', nam
    if kw.get('not', '\t\n\t\n')in nam: return
    file_path = getPath(nam, v=v)
    POSCAR_path = getPath(POSCAR, v=v)
    if v: print '  path:', file_path
    if v>3: print '  POSCAR:', POSCAR
    #TODO: chk other stuff?
    
    #CHK energy

    #TODO: fix regex to find last
    rex = '(?P<n>[0-9]+)\s*' # convergence number
    rex += 'F=\s*(?P<F>{num})\s*' # total free energy
    rex += 'E0=\s*(?P<E0>{num})\s*' # energy for sigma -> 0
    rex += '(?:d E =\s*(?P<dE>{num})\s*)?' # E diff between this and last step
    rex += '(?:mag=\s*(?P<m>{num})\s*)?' # mag
    rex = rex.format(num='[+\-.0-9E]+')
    if v>1: print '  regex:', rex
    regex = re.compile(rex)
    with open(file_path, 'r') as f:
        text = f.read()
        if v: print '  .. file loaded.\n  len(text):', len(text)
    with open(POSCAR_path, 'r') as f:
        n_atoms = f.readlines()[6]
        if v: print '  n_atoms =', n_atoms
    matches = [m for m in regex.finditer(text)]
    #FIX for when empty matches
    if not matches: return 0.0
    if v>2: print '  mathces:', matches
    if v: print '  {0} matches found'.format(len(matches))
    last_match = matches[-1]
    res =  last_match.groupdict()
    if v: print '  last match:', res
    return float(res['F'])/float(n_atoms)
    
def compare(*args, **kw):
    # returns str of list of filename energy for every sub directory
    v = kw.get('v', False)
    a = kw.get('a', True)
    cwd = os.getcwd()
    if v: print '  cwd:', cwd
    nam = kw.get('f', 'OSZICAR')
    POSCAR = kw.get('POSCAR', 'POSCAR')
    if a:
        args = (path[len(cwd) + 1:] for path, dirs, nams in os.walk(cwd) 
                if nam in nams and not kw.get('not', '\t') in path)
    else:
        args = [cwd]
    args = list(args)
    if v: print 'directories:', args
    res = {}
    pad = 0
    for f_path in args:
        if v: '  f_path:', f_path
        pad = max(pad, len(f_path))
        kw['f'] = getPath(nam, f_path=f_path)
        kw['POSCAR'] = getPath(POSCAR, f_path=f_path)
        res[f_path] = chk(**kw)
    txt = ''
    #for f_path, f_energy in sorted(res.iteritems(), key=lambda x: x[1]):
    #    txt += ('{0:'+str(pad)+'.'+str(pad)+'}:'+
    #           '{1:14.7f}').format(f_path[-pad:], f_energy)
    txt = '\n'.join([('{0:'+str(pad)+'.'+str(pad)+'}'+
                      '{1:14.7f}').format(f_path[-pad:], f_energy)
                      for f_path, f_energy in sorted(res.iteritems(),
                                                     key=lambda x: x[1])])
    return txt

def getEnergies(*args, **kw):
    return [float(vals.split(':')[1])
            for vals in compare(*args, **kw).replace(' ', '').split()]

def substract(*args, **kw):
    # to calculate binding energy
    v = kw.get('v', False)
    bind = kw.get('bind', False)

    if bind:
        data = {'cohesive': None, 'structs': {}}
        for ix, nam in enumerate(args):
            if ix==0:
                data['cohesive'] = nam
            else:
                data['structs'][nam] = None
        if data['cohesive']:
            os.chdir(data['cohesive'])
            cohEnergy = max(getEnergies(*args, **kw))
            os.chdir(os.pardir)
        for nam in data['structs'].iterkeys():
            os.chdir(nam)
            data['structs'][nam] = min(getEnergies(*args, **kw))
            os.chdir(os.pardir)
        res = '\n'.join(['{0} : {1:+4.7f}'.format(nam, cohEnergy - energy) 
                         for nam, energy in data['structs'].iteritems()])
    return res

def main(*args, **kw):
    v = kw['v']
    cmd = args[0]
    args = args[1:]
    if v: print '  main args:', cmd, args

    if cmd in 'replace':
        replace(*args, **kw)

    elif cmd in "chk check":
        print chk(*args, **kw)

    elif cmd in 'compare':
        print compare(*args, **kw)

    elif cmd in 'substract':
        print substract(*args, **kw)

if __name__=='__main__':
    #TODO: add argparse
    args = list(sys.argv[1:])
    
    v = False
    kw = {'v': v}
    flags = filter(lambda x: re.search('^-.+', x), args)
    if '-v' in flags:
        v = True 
        print "args:", args
    for flag in flags:
        if '-v' in flag: # all
            kw['v'] = flag.count('v')
            del args[args.index(flag)]
        elif '-f' in flag: # chk
            ix = args.index(flag)
            if v: print "-f index:", ix
            del args[ix]
            if v: print " args:", args
            kw['f'] = args[ix]
        elif '-d' in flag: # comp
            kw['d'] = True
            del args[args.index(flag)]
        elif '-a' in flag: #compare
            kw['a'] = True
            del args[args.index(flag)]
        elif '-bind' in flag: # substract
            kw['bind'] = True
            del args[args.index(flag)]
        elif '-not' in flag: # chk, comp
            ix = args.index(flag)
            if v: print "-not index:", ix
            del args[ix]
            if v: print " args:", args
            kw['not'] = args.pop(ix)
            
                
    if kw['v']:
        print '  args:', args 
        print '  kwargs:', kw
    main(*args, **kw)
    
