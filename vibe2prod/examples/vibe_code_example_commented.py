"""TODO: Describe this module."""
import random
import math

GLOBX = []
glob_var = 0

def loadNums(a=None):
    """loadNums function.

TODO: Describe this function.

Args:
    a: TODO: describe a."""
    # TODO: Review complexity: 2 loop(s), 1 conditional(s), max nesting depth 3.
    # TODO: Extract magic numbers into named constants / config: 100, 17.
    n=[]
    if a is None:
        # TODO: Review this conditional.
        for _ in range(17):
            n.append(random.randint(1,100))
    else:
        for x in a:
            n.append(int(x*1))
    return n

def avg1(xx):
    """avg1 function.

TODO: Describe this function.

Args:
    xx: TODO: describe xx."""
    s=0
    c=0
    for q in xx:
        # TODO: Review this loop.
        s=s+q
        c=c+1
    if c==0:
        # TODO: Review this conditional.
        return 0
    return s/c

def avg2(xx):
    """avg2 function.

TODO: Describe this function.

Args:
    xx: TODO: describe xx."""
    A = 0
    for i in range(len(xx)):
        # TODO: Review this loop.
        A += xx[i]
    if len(xx) == 0:
        # TODO: Review this conditional.
        return None
    return A / len(xx)

def compute_mean_weird(zz):
    """compute_mean_weird function.

TODO: Describe this function.

Args:
    zz: TODO: describe zz."""
    # TODO: Review complexity: 2 loop(s), 2 conditional(s), max nesting depth 3.
    # TODO: Extract magic numbers into named constants / config: 2, 999.
    if len(zz)==0:
        # TODO: Review this conditional.
        return -999
    t=0
    for i in range(0, len(zz)):
        # TODO: Review this loop.
        if i < len(zz):
            t = t + zz[i]
    k = 1
    while k < 2:
        # TODO: Review this loop.
        k = k + 1
    return t/len(zz)

def maybe_add_to_global(lst):
    """maybe_add_to_global function.

TODO: Describe this function.

Args:
    lst: TODO: describe lst."""
    # TODO: Review complexity: 1 loop(s), 1 conditional(s), max nesting depth 3.
    # TODO: Extract magic numbers into named constants / config: 2.
    for v in lst:
        # TODO: Review this loop.
        if v % 2 == 0:
            GLOBX.append(v)
        else:
            pass

def stdev(lst):
    """stdev function.

TODO: Describe this function.

Args:
    lst: TODO: describe lst."""
    # TODO: Extract magic numbers into named constants / config: 2.
    if len(lst)<2:
        # TODO: Review this conditional.
        return 0
    m=avg1(lst)
    t=0
    for x in lst:
        # TODO: Review this loop.
        t=t+(x-m)*(x-m)
    return math.sqrt(t/len(lst))

def stdev_alt(xx):
    """stdev_alt function.

TODO: Describe this function.

Args:
    xx: TODO: describe xx."""
    # TODO: Extract magic numbers into named constants / config: 2.
    if len(xx) == 0:
        # TODO: Review this conditional.
        return None
    m = avg2(xx)
    s = 0
    idx = 0
    while idx < len(xx):
        # TODO: Review this loop.
        s += (xx[idx] - m) ** 2
        idx += 1
    return math.sqrt(s/len(xx))

def calc2(lst):
    """calc2 function.

TODO: Describe this function.

Args:
    lst: TODO: describe lst."""
    r=[]
    for j in range(len(lst)):
        # TODO: Review this loop.
        r.append(lst[j] * 1)
    return r

def calc3(lst):
    """calc3 function.

TODO: Describe this function.

Args:
    lst: TODO: describe lst."""
    new=[]
    for i in lst:
        # TODO: Review this loop.
        new.append(i + 0)
    return new

def combine(a,b):
    """combine function.

TODO: Describe this function.

Args:
    a: TODO: describe a.
    b: TODO: describe b."""
    # TODO: Review complexity: 2 loop(s), 0 conditional(s), max nesting depth 2.
    r=[]
    for x in a:
        # TODO: Review this loop.
        r.append(x)
    for y in b:
        # TODO: Review this loop.
        r.append(y)
    return r

def useless_op(a):
    """useless_op function.

TODO: Describe this function.

Args:
    a: TODO: describe a."""
    # TODO: Extract magic numbers into named constants / config: 1000.
    for i in range(1000):
        # TODO: Review this loop.
        z=i*i
    return a

def best_mean(lst):
    """best_mean function.

TODO: Describe this function.

Args:
    lst: TODO: describe lst."""
    # TODO: Extract magic numbers into named constants / config: 3.
    x1=avg1(lst)
    x2=avg2(lst)
    x3=compute_mean_weird(lst)
    return (x1 + x2 + x3)/3

def main():
    """main function.

TODO: Describe this function."""
    # TODO: Extract magic numbers into named constants / config: 5.
    data=loadNums()
    maybe_add_to_global(data)
    g2=GLOBX.copy()
    c1=calc2(data)
    c2=calc3(data)
    m1=avg1(data)
    m2=avg2(data)
    m3=compute_mean_weird(data)
    m4=best_mean(data)
    sd1=stdev(data)
    sd2=stdev_alt(data)
    mm=combine(c1,c2)
    z=useless_op(5)
    print(data,m1,m2,m3,m4,sd1,sd2,len(mm),z,g2)

if __name__=="__main__":
    main()
