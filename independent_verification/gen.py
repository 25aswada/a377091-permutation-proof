from math import isqrt

def issq(x):
    r = isqrt(x)
    return r*r == x

NMAX = 500_000
used_pos = set()
used_neg = set()
pref_pos = 0
pref_neg = 0
a_prev = 0
m = 1
seen_roots = set()
boundaries = {}
seq = [0]
crossing_roots = []  # roots in order of crossings

for n in range(1, NMAX+1):
    k = m
    while True:
        if k not in used_pos and issq(abs(a_prev - k)):
            cur = k; break
        if k not in used_neg and issq(abs(a_prev + k)):
            cur = -k; break
        k += 1
    if a_prev != 0 and (a_prev > 0) != (cur > 0):
        d = abs(cur - a_prev)
        R = isqrt(d)
        assert R*R == d, "crossing distance not a square?!"
        crossing_roots.append(R)
        if R not in seen_roots:
            seen_roots.add(R)
            r = R - 1
            if a_prev > 0:
                Lp, Ep, Qp, Eq, sigma = pref_pos, used_pos, pref_neg, used_neg, '+'
            else:
                Lp, Ep, Qp, Eq, sigma = pref_neg, used_neg, pref_pos, used_pos, '-'
            EA = tuple(sorted(x - Lp for x in Ep if x > Lp))
            EB = tuple(sorted(x - Qp for x in Eq if x > Qp))
            f = Lp - ((r*r + 1)//2 + r)
            e = Qp - (r*r // 2)
            u = abs(a_prev) - Lp
            boundaries[r] = dict(n_before=n-1, sigma=sigma, f=f, e=e, u=u, EA=EA, EB=EB)
    if cur > 0:
        used_pos.add(cur)
        while pref_pos + 1 in used_pos: pref_pos += 1
    else:
        used_neg.add(-cur)
        while pref_neg + 1 in used_neg: pref_neg += 1
    if len(seq) < 62:
        seq.append(cur)
    a_prev = cur
    while m in used_pos and m in used_neg:
        m += 1

# 1. check against OEIS first 62 terms
oeis = [0,1,2,-2,-1,3,4,5,-4,-3,6,7,8,-8,-7,-6,-5,-9,-10,-11,-12,13,9,10,11,12,-13,-14,-15,-16,-17,-18,18,14,15,16,17,-19,-20,-21,-22,-23,-24,25,21,20,19,23,22,26,27,28,24,-25,-26,-27,-28,-29,-30,-31,-32,32]
print("first-62 match vs OEIS:", seq == oeis)

# 2. crossing root structure
import collections
cnt = collections.Counter(crossing_roots)
bad = [r for r,c in cnt.items() if c != 2]
print("roots not appearing exactly twice:", sorted(bad)[:10], "...(showing up to 10)")
rs = sorted(seen_roots)
print("roots range:", rs[0], "to", rs[-1], "| consecutive w/o gaps:", rs == list(range(rs[0], rs[-1]+1)))

# 3. B_100 check
b = boundaries.get(100)
print("B_100:", b)

import pickle
with open('boundaries.pkl','wb') as fh:
    pickle.dump(boundaries, fh)
print("max r with boundary recorded:", max(boundaries))
