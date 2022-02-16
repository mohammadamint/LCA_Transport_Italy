
import numpy as np

def dis_pow_weight(instance,weight,power,displacement):

    _weight = instance.segment_properties["weight"]
    _power = instance.segment_properties["power"]
    _displacement = instance.segment_properties["displacement"]
    segments = instance.segment_ids

    w = abs(1 - _weight/weight)
    (w,) = np.where(w == min(w))
    w = segments[w[0]]

    c = abs(1-_displacement/displacement)
    (c,) = np.where(c == min(c))
    if len(c)>1: 
        c=w
    else: 
        c=segments[c[0]]

    p = abs(1 - _power/power)
    (p,) = np.where(p == min(p))
    if len(p)>1: 
        p=w
    else:
        p = segments[p[0]]

    if (c == p): 
        w = c
    if (c == w): 
        p = c
    if (w == p): 
        c = w
        

    S = round((c+p+w)/3)

    # Cc = ((displacement- _displacement[S-1])/_displacement[S-1])
    # Cw = ((weight - _weight[S-1])/_weight[S-1])
    # Cp = ((power - _power[S-1])/_power[S-1])

    # goodMPE = (Cc+Cw+Cp)/3

    return {"segment":S}