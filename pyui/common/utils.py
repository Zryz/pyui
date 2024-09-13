from random import randint
from .defs import EXCLUDED_CHARS
from typing import List

def gen_random_char()->chr:
    val = randint(32, 115)
    while val > 126 and val < 160:
        val = randint(32, 300)
    if val % 5 == 0 or val % 2 == 0 or chr(val) in EXCLUDED_CHARS: 
        char = ' '
    else:
        char = chr(val)
    return char

"""Divide a span by a set of floats given as a list that sum to 1.0 - e.g .5, .5 for a span of 8 returns a list of [4,4] i.e 50%"""

def divide_span(divisions:List[float], span)-> List[int]:
    z = q = []
    #Divmod and generate [size, remainder] pairs
    for scale in divisions:
        if not scale:
            diff = 1.0 - sum([x for x in divisions if isinstance(x, float)])
            size, remainder = divmod(span*diff, 1.0)
            z.append([[int(size), None], 0])
        else:
            size, remainder = divmod(span*scale, 1.0)
            z.append([int(size),remainder])

    #Sum the total of the remainders (will always reach a whole number) and apply to the centre sector len // 2
    if len(divisions) == 2:
        r = 0
    else:
        r = len(divisions)//2

    z[r][0] += int(sum([val[1] for val in z]))  
    
    #Return the line breakdown of window heights summing to y result of self.getmaxyx()
    return [val[0] for val in z]