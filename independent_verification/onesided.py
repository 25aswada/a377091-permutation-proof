from math import isqrt

def issq(x):
    r = isqrt(x); return r*r == x

def step(cur, used):
    k = 1
    while True:
        if k not in used and issq(abs(cur - k)):
            return k
        k += 1

def canonical(used, cur):
    # returns (True, p, g) if state is canonical C_g(p): used == {1..p}, cur = p-g, g in {0,1,2}
    p = 0
    while p+1 in used: p += 1
    if len(used) != p: return (False, None, None)
    g = p - cur
    if g in (0,1,2): return (True, p, g)
    return (False, None, None)

# --- Test 1: canonical transitions C_0, C_1, C_2
def run_until_canonical(cur, used, maxsteps=100000):
    for i in range(maxsteps):
        ok, p, g = canonical(used, cur)
        if ok: return p, g, i
        cur = step(cur, used)
        used.add(cur)
    raise RuntimeError("no canonical state reached")

p0 = 50
# C_1(p): expect visits p+3,p+2,p+1 then C_2(p+3)
used = set(range(1, p0+1)); cur = p0-1
seq = []
for _ in range(3):
    cur = step(cur, used); used.add(cur); seq.append(cur)
ok, p, g = canonical(used, cur)
print("C_1(50) ->", seq, "-> canonical:", ok, "C_%d(%d)" % (g,p), "| expected [53,52,51] -> C_2(53)")

used = set(range(1, p0+1)); cur = p0-2
seq = []
for _ in range(2):
    cur = step(cur, used); used.add(cur); seq.append(cur)
ok, p, g = canonical(used, cur)
print("C_2(50) ->", seq, "-> canonical:", ok, "C_%d(%d)" % (g,p), "| expected [52,51] -> C_1(52)")

# --- Test 2: cleanup lemma base: N in 1..99, all E subset of {2,3,4}, prefix at first canonical <= N+23
from itertools import combinations
maxover = -999; failures = []
for N in range(1, 100):
    for k in range(4):
        for E in combinations([2,3,4], k):
            E = set(E) - {N}
            used = {N} | E
            cur = N
            try:
                p, g, steps = run_until_canonical(cur, set(used))
            except RuntimeError:
                failures.append((N, E, "no canonical")); continue
            if p - N > maxover: maxover = p - N; argmax = (N, E, p, g)
            if p > N + 23: failures.append((N, E, p))
print("cleanup base failures:", failures[:5], "count:", len(failures))
print("max overshoot p-N:", maxover, "at", argmax, "| claimed: exactly 23")

# --- Test 3: remote point table, for L in 40..99 (covering all residues many times), g in {0,1,2}
table = {
 0: {0:(0,1),1:(0,1),2:(0,1),3:(0,1),4:(0,1)},
 1: {0:(13,1),1:(0,2),2:(8,1),3:(5,1),4:(1,0)},
 2: {0:(5,1),1:(1,0),2:(13,1),3:(0,2),4:(8,1)},
}
p0 = 200
bad = []
for g in (0,1,2):
    for L in range(40, 100):
        used = set(range(1, p0+1)) | {p0+L}
        cur = p0 - g
        # run until remote absorbed into prefix AND canonical
        for i in range(200000):
            pfx = 0
            # cheap: prefix from p0
            pfx = p0
            while pfx+1 in used: pfx += 1
            if pfx >= p0+L:
                ok, p, gg = canonical(used, cur)
                if ok:
                    d, h = p - (p0+L), gg
                    exp = table[g][L % 5]
                    if (d,h) != exp: bad.append((g, L, (d,h), exp))
                    break
            cur = step(cur, used); used.add(cur)
        else:
            bad.append((g, L, "never resolved", None))
print("remote-point table mismatches:", bad if bad else "NONE — table verified for all g, L in 40..99")
