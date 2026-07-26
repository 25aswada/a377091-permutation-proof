import pickle
from math import isqrt
import importlib.util
import sys
spec = importlib.util.spec_from_file_location("chk", "A377091_proof_checker_v4.py")
chk = importlib.util.module_from_spec(spec)
sys.modules["chk"] = chk
spec.loader.exec_module(chk)

# --- 1. Mechanics cross-validation: checker's choose_next vs my independent generator, 100k steps
def issq(x):
    r = isqrt(x); return r*r == x

def my_gen(nmax):
    used_pos, used_neg = set(), set()
    a_prev, m = 0, 1
    out = []
    for n in range(nmax):
        k = m
        while True:
            if k not in used_pos and issq(abs(a_prev - k)): cur = k; break
            if k not in used_neg and issq(abs(a_prev + k)): cur = -k; break
            k += 1
        out.append(cur)
        (used_pos if cur > 0 else used_neg).add(abs(cur))
        a_prev = cur
        while m in used_pos and m in used_neg: m += 1
    return out

N = 100000
mine = my_gen(N)
sides = {1: chk.Side(0,set()), -1: chk.Side(0,set())}
sides[1].add(1); sg, x = 1, 1
theirs = [1]
for _ in range(N-1):
    sg, x, root = chk.choose_next(sg, x, sides)
    sides[sg].add(x)
    theirs.append(sg*x)
print("mechanics agree on first %d terms:" % N, mine == theirs)

# --- 2. Closure containment + transition agreement with the REAL sequence
states, rounds, ncache, digest = chk.build_invariant()
# rebuild the cache identically
cache = {}
for st in sorted(states):
    for idx in range(6):
        cache[(st, idx)] = chk.transition(st, idx)

# my empirical boundary states + checkpoint types (from checkpoint.py run) -- regenerate quickly
import subprocess
# reuse boundaries.pkl (states) but need checkpoint types too; rerun compact version
exec(open('checkpoint.py').read().split("print(")[0])  # runs the generation loop, defines boundaries, checkpoint_types
emp_states = {}
for r, tup in boundaries.items():
    if r < 100: continue
    rm, sigma, f, e, u, EA, EB = tup
    emp_states[r] = (rm, 1 if sigma == '+' else -1, f, e, u, EA, EB)

inset = sum(1 for s in emp_states.values() if s in states)
print("empirical boundary states inside 412-closure: %d / %d" % (inset, len(emp_states)))
missing = [ (r,s) for r,s in emp_states.items() if s not in states ]
print("outside closure:", missing[:5])

ckmap = {(28,2):0,(29,1):1,(29,2):2,(30,0):3,(30,1):4,(30,2):5}
agree = disagree = 0; bad = []
for r in sorted(emp_states):
    if r+1 not in emp_states or r not in checkpoint_types: continue
    idx = ckmap[checkpoint_types[r]]
    pred = cache.get((emp_states[r], idx))
    actual = emp_states[r+1]
    if pred == actual: agree += 1
    else:
        disagree += 1
        if len(bad) < 5: bad.append((r, checkpoint_types[r], pred, actual))
print("phase transitions: checker-predicted vs actual: %d agree, %d disagree" % (agree, disagree))
for b in bad: print("  MISMATCH:", b)
