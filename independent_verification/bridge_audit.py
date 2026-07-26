import sys, importlib.util
from math import isqrt
spec = importlib.util.spec_from_file_location("chk3", "A377091_proof_checker_v3.py")
chk = importlib.util.module_from_spec(spec); sys.modules["chk3"] = chk
spec.loader.exec_module(chk)

# ---- Test A: independently verify the 15-case checkpoint table (doc section 10)
# via REAL one-sided simulation with the remote D marked, across many deficits.
DOC_TABLE = {  # (g, n mod 5) -> (h, g') with n = D-30-p
 (0,1):(30,0),(0,2):(30,0),(0,3):(30,0),(0,4):(30,0),(0,0):(30,0),
 (1,1):(28,2),(1,2):(29,2),(1,3):(30,2),(1,4):(29,1),(1,0):(30,1),
 (2,1):(29,1),(2,2):(30,1),(2,3):(28,2),(2,4):(29,2),(2,0):(30,2),
}
def issq(v): rt=isqrt(v); return rt*rt==v
bad = []
D = 137  # arbitrary D >= 92
for g in (0,1,2):
    for deficit in range(31, 49):
        p = D - deficit
        used = set(range(1, p+1)) | {D}
        cur = p - g
        # simulate one-sided until first canonical-with-single-extra-at-D with prefix >= D-30
        pf = p
        for _ in range(100000):
            extras = [v for v in used if v > pf]
            if pf >= D-30 and extras == [D] and pf-cur in (0,1,2):
                h, gp = D - pf, pf - cur
                n = deficit - 30
                exp = DOC_TABLE[(g, n % 5)]
                if (h, gp) != exp: bad.append((g, deficit, (h,gp), exp))
                break
            cur = chk.next_one(cur, used); used.add(cur)
            while pf+1 in used: pf += 1
        else:
            bad.append((g, deficit, "unresolved", None))
print("15-case table vs real simulation:", "ALL MATCH" if not bad else bad[:8])

# ---- Test B: the missing corroboration -- full TWO-SIDED bridge simulation
# from every closure state at representative AND out-of-sample roots.
states, rounds, ncache, digest = chk.build_invariant()
SIX = set(chk.CHECKPOINTS)
def bridge_sim(st, r):
    sg, L, Q, u, EA, EB = chk.instantiate(st, r)
    _,_,f,e,_,_,_ = st
    D = r+1-f-e-u
    sides = {sg: chk.Side(L, {L+a for a in EA}), -sg: chk.Side(Q, {Q+a for a in EB})}
    x, s = L+u, sg
    old_snapshot = (sides[sg].prefix, frozenset(sides[sg].extras))
    # first move must be the root-(r+1) crossing
    ns, y, root = chk.choose_next(s, x, sides)
    assert ns == -sg and root == r+1 and y == Q + D, "first crossing failed"
    sides[ns].add(y); s, x = ns, y
    for _ in range(100000):
        tgt = sides[s]
        if s == -sg and tgt.prefix - Q >= D - 30 and tgt.extras == {Q + D} and tgt.prefix - x in (0,1,2):
            h, g = D - (tgt.prefix - Q), tgt.prefix - x
            oldside = sides[sg]
            untouched = (oldside.prefix, frozenset(oldside.extras)) == old_snapshot
            return (h, g), untouched
        ns, y, root = chk.choose_next(s, x, sides)
        if ns != s:
            return ("CROSSING-INTERRUPT", root), False
        sides[ns].add(y); s, x = ns, y
    return ("UNRESOLVED", None), False

fails = 0; total = 0; seen = set()
for st in sorted(states):
    rep = 100 + st[0]
    for r in (rep, rep+40, rep+230):   # representative + two out-of-sample decades
        total += 1
        (ck, ok) = bridge_sim(st, r)
        if not (ck in SIX and ok):
            fails += 1
            if fails <= 5: print("BRIDGE FAIL:", st, "r=%d" % r, ck, "old-side-untouched:", ok)
        else:
            seen.add(ck)
print("two-sided bridge simulations: %d run, %d failures; checkpoint formats seen: %s" % (total, fails, sorted(seen)))
