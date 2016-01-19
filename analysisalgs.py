from reader import *

def AdsEnergy(info, parts, v=False):
    if v: print "init adsEnergy"
    if v: print "type(info):", type(info)
    if v>1: print "parts:", parts
    # modifyers
    area = parts.get('area', False)
    # calc
    if isinstance(info, Check):
        res = energy_diff(info, parts, area, v=v)
    elif isinstance(info, Folder):
        res = {calc.nam: energy_diff(calc, parts, area, v=v)
               for calc in info.calcs}
    # TODO: include parts used in calculation in report
    return res

def energy_diff(total, parts, area=None, v=False):
    if not area:
        area = 1
    elif area == True:
        area = total.get('area')
    #
    res = total.F - sum_energy(parts, ref=total, v=v)
    res /= area
    return res

def sum_energy(parts, ref, v=False):
    res = 0
    for cat, path in parts.iteritems():
        if not path: continue
        if v: print "  cat: {} path: {}".format(cat, path)
        if cat == 'part':
            for part in path:
                if v: print "init read part", part
                res += Check(part, v=v).F
                if v: print "fin read part"
        elif cat == 'bulk' or cat == 'ads':
            if v: print "init read part", path
            tmp = Check(path, v=v)
            elm, num = next(tmp.elements.iteritems())
            ratio = ref.elements.get(elm) / float(num)
            res += tmp.F * ratio
            if v: print "fin read part"
    return res
