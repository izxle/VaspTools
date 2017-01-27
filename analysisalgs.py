from reader import *
from myfunctions import printv

class Ediff(object):
    def __init__(self, complet, parts, v=False):
        self.rep = parts.pop('v')
        self.complet = complet
        self.v = v
        # modifyers
        self.area = parts.pop('area', False)
        # calc
        self._get_data_from_parts(parts)
        self.ads = parts['ads']
        # run
        self._process_data()
        
        
    def _process_data(self):
        if isinstance(self.complet, Check):
            res = {self.complet.nam: {'Ediff': self._get_energy_diff(self.complet),
                                      'complet': self.complet.F,
                                      'area': self.area if type(self.area)==float 
                                              else self.complet.area
                                     }
                  }
        elif isinstance(self.complet, Folder):
            res = {calc.nam: {'Ediff': self._get_energy_diff(calc),
                              'complet': calc.F,
                              'area': self.area if type(self.area)==float
                                      else calc.area
                             }
                   for calc in self.complet.calcs}
        self.res = res

    def _get_energy_diff(self, complet):
        # sum relative energy of parts
        parts_energy = 0
        for nam, part in self.parts.items():
            if part['ratio']:
                elm, num = part['ratio']
                ratio = complet.elements.get(elm) / float(num)
            else:
                ratio = 1
            relE = part['energy'] * ratio
            self.parts[nam]['relE'][complet.nam] = relE
            parts_energy += relE
        #
        res = complet.F - parts_energy
        if self.ads:
            ads_ratio = complet.elements.get(self.ads_elm) / self.ads_num
            if self.v: printv('ads_ratio: ', ads_ratio)
            res /= ads_ratio
            
        if self.area:
            if isinstance(self.area, bool):
                area = complet.get('area') * 2
            res /= area
            
        return res

    def _get_data_from_parts(self, parts):
        v = self.v
        res = {}
        p = 0 # pad counter to avoid collision
        for cat, path in parts.items():
            if not path: continue
            if v: printv("  cat: {} path: {}".format(cat, path))
            if cat == 'part':
                for part in path:
                    if v: printv("init read part ", part)
                    tmp = Check(part, v=v)
                    nam = '{}-{}'.format(p, tmp.nam)
                    res[nam] = {'energy': tmp.F,
                                'ratio': {},
                                'relE': {}}
                    if v: 
                        printv(res)
                        printv("fin read part")
            elif cat == 'bulk' or cat == 'ads':
                if v: printv("init read part", path)
                tmp = Check(path, v=v)
                nam = '{}-{}'.format(p, cat)
                res[nam] = {'energy': tmp.F,
                            'ratio': tmp.elements.items()[0],
                            'relE': {}}
                if cat == 'ads':
                    self.ads_elm, self.ads_num = res[nam]['ratio']
                if v: 
                    printv(res)
                    printv("fin read part")
        self.parts = res

    def __str__(self):
        res = ""
        for nam, val in sorted(self.res.items()):
            res += "{:12}: {:11.5f}\n".format(nam, val['Ediff'])
            if self.rep:
                res += "  {:10}: {:11.5f}\n".format(nam, val['complet'])
                for part_nam, part in self.parts.items():
                    res += "  {:10}: {:11.5f}\n".format(part_nam,
                                                        part['relE'][nam])
                if self.area:
                    res += "  {:10}: {:11.5f}\n".format("area", val['area'])
            if self.rep: res += "\n"
        return res[:-2]
#..

def MDynn(folder):
    calcs = folder.calcs

    res = str(calcs[0])
    res.replace("io_step", "   time")
    prev = int(res.split("\n")[-1].split()[0])
    
    for i in xrange(1, len(calcs)):
        lines = str(calcs[i]).split("\n")[1:]
        for i_line in xrange(len(lines)):
            line = lines[i_line]
            orig = line.split()[0]
            new_val = int(orig) + prev
            lines[i_line] = "{:>8}".format(new_val) + line[8:]
        prev = lines[-1].split()[0]
        res += "\n" + "\n".join(lines)    
        
    return res
