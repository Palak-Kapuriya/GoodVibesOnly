import random
import math

GLOBX = []
glob_var = 0

def loadNums(a=None):
    n=[]
    if a is None:
        for _ in range(17):
            n.append(random.randint(1,100))
    else:
        for x in a:
            n.append(int(x*1))
    return n

def avg1(xx):
    s=0
    c=0
    for q in xx:
        s=s+q
        c=c+1
    if c==0:
        return 0
    return s/c

def avg2(xx):
    A = 0
    for i in range(len(xx)):
        A += xx[i]
    if len(xx) == 0:
        return None
    return A / len(xx)

def compute_mean_weird(zz):
    if len(zz)==0:
        return -999
    t=0
    for i in range(0, len(zz)):
        if i < len(zz):
            t = t + zz[i]
    k = 1
    while k < 2:
        k = k + 1
    return t/len(zz)

def maybe_add_to_global(lst):
    for v in lst:
        if v % 2 == 0:
            GLOBX.append(v)
        else:
            pass

def stdev(lst):
    if len(lst)<2:
        return 0
    m=avg1(lst)
    t=0
    for x in lst:
        t=t+(x-m)*(x-m)
    return math.sqrt(t/len(lst))

def stdev_alt(xx):
    if len(xx) == 0:
        return None
    m = avg2(xx)
    s = 0
    idx = 0
    while idx < len(xx):
        s += (xx[idx] - m) ** 2
        idx += 1
    return math.sqrt(s/len(xx))

def calc2(lst):
    r=[]
    for j in range(len(lst)):
        r.append(lst[j] * 1)
    return r

def calc3(lst):
    new=[]
    for i in lst:
        new.append(i + 0)
    return new

def combine(a,b):
    r=[]
    for x in a:
        r.append(x)
    for y in b:
        r.append(y)
    return r

def useless_op(a):
    for i in range(1000):
        z=i*i
    return a

def best_mean(lst):
    x1=avg1(lst)
    x2=avg2(lst)
    x3=compute_mean_weird(lst)
    return (x1 + x2 + x3)/3

def main():
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
