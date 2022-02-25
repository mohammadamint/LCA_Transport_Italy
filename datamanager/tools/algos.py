
import numpy as np

def dis_pow_weight(instance,weight,power,displacement):

    _weight = instance.segment_properties["weight"]
    _power = instance.segment_properties["power"]
    _displacement = instance.segment_properties["displacement"]
    segments = instance.segment_ids
    
    try:
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

        return {"segment":S}
    
    except IndexError:
        
        return {"segment":None}
    
def pow_weight(instance,weight,power):
    
    _weight = instance.segment_properties['weight']
    _power = instance.segment_properties['power']
    segments = instance.segment_ids
    
    try:
        w = abs(1 - _weight/weight)
        (w,) = np.where(w == min(w))
    
        w = segments[w[0]]

    
        p = abs(1 - _power/power)
        (p,) = np.where(p == min(p))
        if len(p)>1: 
            p=w
        else:
            p = segments[p[0]]
    
            
    
        S = round((p+w)/2)

        return {"segment":S}
    
    except IndexError:
        
        return {"segment":None}
    
    
    
