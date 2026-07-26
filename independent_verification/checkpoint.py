from math import isqrt

def issq(x):
    r = isqrt(x); return r*r == x

NMAX = 500_000
used_pos, used_neg = set(), set()
pref_pos = pref_neg = 0
a_prev = 0
m = 1
seen_roots = set()
boundaries = {}
pending = None  # tracking cleanup after a first-crossing
checkpoint_types = {}
interrupts = []
six = {(28,2),(29,1),(29,2),(30,0),(30,1),(30,2)}

for n in range(1, NMAX+1):
    k = m
    while True:
        if k not in used_pos and issq(abs(a_prev - k)):
            cur = k; break
        if k not in used_neg and issq(abs(a_prev + k)):
            cur = -k; break
        k += 1
    crossing = a_prev != 0 and (a_prev > 0) != (cur > 0)
    if crossing:
        d = abs(cur - a_prev); R = isqrt(d)
        if pending is not None:
            interrupts.append((pending['r'], n))  # crossing before checkpoint found!
            pending = None
        if R not in seen_roots:
            seen_roots.add(R)
            r = R - 1
            if a_prev > 0:
                Lp, Ep, Qp, Eq, sigma = pref_pos, used_pos, pref_neg, used_neg, '+'
            else:
                Lp, Ep, Qp, Eq, sigma = pref_neg, used_neg, pref_pos, used_pos, '-'
            EA = tuple(sorted(x - Lp for x in Ep if x > Lp))
            EB = tuple(sorted(x - Qp for x in Eq if x > Qp))
            f = Lp - ((r*r+1)//2 + r); e = Qp - (r*r//2); u = abs(a_prev) - Lp
            boundaries[r] = (r % 10, sigma, f, e, u, EA, EB)
            if r >= 100:
                D = abs(cur) - Qp
                pending = dict(r=r, Q=Qp, D=D, target='+' if cur > 0 else '-')
    # add cur
    if cur > 0:
        used_pos.add(cur)
        while pref_pos+1 in used_pos: pref_pos += 1
    else:
        used_neg.add(-cur)
        while pref_neg+1 in used_neg: pref_neg += 1
    a_prev = cur
    while m in used_pos and m in used_neg: m += 1
    # checkpoint detection (after updating with cur)
    if pending is not None:
        tgt = pending['target']
        up, pf = (used_pos, pref_pos) if tgt == '+' else (used_neg, pref_neg)
        Q, D = pending['Q'], pending['D']
        on_target = (cur > 0) == (tgt == '+')
        if on_target and pf - Q >= D - 30 and len(up) - pf == 1:
            g = pf - abs(cur)
            if g in (0,1,2):
                h = D - (pf - Q)
                checkpoint_types[pending['r']] = (h, g)
                pending = None

print("crossings interrupting cleanup before checkpoint:", len(interrupts), interrupts[:5])
ck = checkpoint_types
outside = {r:v for r,v in ck.items() if v not in six}
print("checkpoints found for %d boundaries (r>=100); outside six-type set: %d" % (len(ck), len(outside)))
if outside:
    for r in sorted(outside)[:10]: print("  r=%d type=%s" % (r, outside[r]))
import collections
print("checkpoint type distribution:", dict(collections.Counter(ck.values())))

# transition determinism WITH checkpoint type
transmap = {}; conflicts = []
rs = sorted(boundaries)
for r in rs:
    if r < 100 or r+1 not in boundaries or r not in ck: continue
    key = (boundaries[r], ck[r])
    out = boundaries[r+1][1:]
    if key in transmap and transmap[key] != out:
        conflicts.append((r, key, transmap[key], out))
    transmap[key] = out
print("conflicts WITH checkpoint type included:", len(conflicts))
for c in conflicts[:10]:
    print("  r=%d key=%s : %s vs %s" % (c[0], c[1], c[2], c[3]))
print("distinct (state, checkpoint) -> next transitions observed:", len(transmap))
