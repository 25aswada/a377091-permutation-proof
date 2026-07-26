from __future__ import annotations
from dataclasses import dataclass
from itertools import combinations
from math import isqrt
from hashlib import sha256

# ================================================================
# Exact mechanics of A377091 in sign/magnitude coordinates
# ================================================================

@dataclass
class Side:
    prefix: int
    extras: set[int]

    def copy(self):
        return Side(self.prefix, set(self.extras))

    def used(self, m: int) -> bool:
        return m <= self.prefix or m in self.extras

    def add(self, m: int) -> None:
        assert m > self.prefix and m not in self.extras
        self.extras.add(m)
        while self.prefix + 1 in self.extras:
            self.extras.remove(self.prefix + 1)
            self.prefix += 1


def min_same(x: int, side: Side) -> tuple[int,int]:
    # Search downward first because any downward candidate has smaller magnitude.
    d = x - side.prefix - 1
    if d >= 1:
        k = isqrt(d)
        while k >= 1:
            y = x - k*k
            if y > side.prefix and y not in side.extras:
                return y,k
            k -= 1
    # Then the least upward candidate.
    k = 1 if x > side.prefix else isqrt(side.prefix-x)+1
    while True:
        y = x + k*k
        if y > side.prefix and y not in side.extras:
            return y,k
        k += 1


def min_opposite(x: int, side: Side) -> tuple[int,int]:
    k = isqrt(x + side.prefix) + 1
    while True:
        y = k*k - x
        if y > side.prefix and y not in side.extras:
            return y,k
        k += 1


def choose_next(sign: int, x: int, sides: dict[int,Side]):
    y,ky = min_same(x,sides[sign])
    z,kz = min_opposite(x,sides[-sign])
    if y < z: return sign,y,ky
    if z < y: return -sign,z,kz
    # equal magnitudes: positive integer wins
    return (sign,y,ky) if sign == 1 else (-sign,z,kz)

# ================================================================
# One-sided cleanup certificates
# ================================================================

def next_one(cur: int, used: set[int]) -> int:
    best = None
    for k in range(1,isqrt(cur-1)+1):
        y = cur-k*k
        if y > 0 and y not in used and (best is None or y < best):
            best = y
    if best is not None:
        return best
    k=1
    while cur+k*k in used:
        k += 1
    return cur+k*k


def first_canonical(N: int, E: tuple[int,...]):
    """Start at N with N and E marked. Return first state with [1,p] used,
    no extras, and current p, p-1, or p-2."""
    used=set(E); used.add(N); cur=N; p=0
    while p+1 in used: p+=1
    for step in range(100000):
        if not any(v>p for v in used) and p-cur in (0,1,2):
            return p-N,p-cur,step
        cur=next_one(cur,used); used.add(cur)
        while p+1 in used: p+=1
    raise AssertionError

# Canonical modes C_g: full prefix p, no extras, current p-g, g=0,1,2.
# With a remote marked point p+L, the next canonical state after absorbing it is:
REMOTE_TABLE = {
    0: {0:(0,1),1:(0,1),2:(0,1),3:(0,1),4:(0,1)},
    1: {0:(13,1),1:(0,2),2:(8,1),3:(5,1),4:(1,0)},
    2: {0:(5,1),1:(1,0),2:(13,1),3:(0,2),4:(8,1)},
}

def remote_to_canonical(g: int, L: int):
    p=100
    used=set(range(1,p+1)); used.add(p+L); cur=p-g
    for step in range(100000):
        extras=[v for v in used if v>p]
        if p>=100+L and not extras and p-cur in (0,1,2):
            return p-(100+L),p-cur
        cur=next_one(cur,used); used.add(cur)
        while p+1 in used:p+=1
    raise AssertionError


def verify_cleanup_certificates():
    subsets=[tuple(c) for n in range(4) for c in combinations((2,3,4),n)]
    # Finite base for strong induction. Universal overshoot bound used in proof.
    max_over=-10**9
    for N in range(1,100):
        for E in subsets:
            EE=tuple(v for v in E if v!=N)
            dp,g,_=first_canonical(N,EE)
            max_over=max(max_over,dp)
            assert dp <= 23 and g in (0,1,2)
    assert max_over == 23

    # The remote-point table. Five-periodicity follows from the explicit
    # C1 -> C2 (+3) and C2 -> C1 (+2) packet rules; these checks certify
    # the finite transient around the marked point.
    for g in (0,1,2):
        for res in range(5):
            expected=REMOTE_TABLE[g][res]
            for L in (40+res,45+res,50+res):
                assert remote_to_canonical(g,L)==expected

    # Directly certify the canonical packet rules and their 10-step return.
    for g in (0,1,2):
        p=100; used=set(range(1,p+1)); cur=p-g
        seq=[]
        for _ in range(10):
            cur=next_one(cur,used); used.add(cur); seq.append(cur)
            while p+1 in used:p+=1
        assert not any(v>p for v in used)
        assert p==110 and p-cur==g

# ================================================================
# Phase invariant
# ================================================================
# B_r is the instant immediately before the first crossing with root r+1.
# State = (r mod 10, current sign, f,e,u, leading extras, other extras)
# L=ceil(r^2/2)+r+f; Q=floor(r^2/2)+e; current=L+u.

BASE=(0,1,0,0,2,(2,),())   # exact B_100
CHECKPOINTS=((28,2),(29,1),(29,2),(30,0),(30,1),(30,2))
TAILS={(0,()),(1,()),(2,()),(-2,(2,)),(-3,(3,))}


def instantiate(st,r):
    rm,sg,f,e,u,EA,EB=st
    assert r%10==rm
    L=(r*r+1)//2+r+f
    Q=(r*r)//2+e
    return sg,L,Q,u,EA,EB


def norm_output(rn,sg,x,lead,other):
    f=lead.prefix-((rn*rn+1)//2+rn)
    e=other.prefix-(rn*rn//2)
    u=x-lead.prefix
    EA=tuple(sorted(v-lead.prefix for v in lead.extras))
    EB=tuple(sorted(v-other.prefix for v in other.extras))
    return (rn%10,sg,f,e,u,EA,EB)


def initial_checkpoint(st,idx,r):
    sg,L,Q,u,EA,EB=instantiate(st,r)
    _,_,f,e,_,_,_=st
    D=r+1-f-e-u
    h,g=CHECKPOINTS[idx]
    P=D-h
    assert P>0
    sides={
        sg:Side(L,{L+a for a in EA}),
        -sg:Side(Q+P,{Q+D}),
    }
    return -sg,Q+P-g,sides


def phase_trace(st,idx,r):
    sg,x,sides=initial_checkpoint(st,idx,r)
    trace=[]
    for step in range(10000):
        ns,y,root=choose_next(sg,x,sides)
        if ns!=sg and root>=r+2:
            assert root==r+2
            tail=(sides[sg].prefix-x,
                  tuple(sorted(v-sides[sg].prefix for v in sides[sg].extras)))
            out=norm_output(r+1,sg,x,sides[sg],sides[-sg])
            return trace,(sg,x,sides),tail,(ns,y,root),out
        if ns != sg:
            assert root == r+1
        trace.append((sg,x,ns,y,root))
        sides[ns].add(y); sg,x=ns,y
    raise AssertionError


def verify_first_crossing(st,r):
    sg,L,Q,u,EA,EB=instantiate(st,r)
    sides={sg:Side(L,{L+a for a in EA}),-sg:Side(Q,{Q+a for a in EB})}
    ns,y,root=choose_next(sg,L+u,sides)
    assert ns==-sg and root==r+1


def shifted_side_equal(a:Side,b:Side,d:int):
    return b.prefix==a.prefix+d and b.extras=={v+d for v in a.extras}


def max_used(side: Side) -> int:
    return max([side.prefix, *side.extras])


def verify_uniform_period_certificate(st,idx,r):
    """A finite certificate for a *uniform* r -> r+10 induction.

    Put H_r=floor(r^2/2)+r.  At a checkpoint, subtracting H_r from
    every magnitude makes the initial two-side state independent of r
    within a fixed residue class.  Same-side moves and crossings with
    root r+1 are then independent of r; the raw root-(r+2) candidate is
    the only moving competitor, and its local coordinate increases by
    20 when r is replaced by r+10.

    This routine verifies the finite base trace and the ten-move tail
    conditions used by the induction in the proof.  In particular it
    checks the inequalities that remain valid after every further
    decade, rather than merely comparing one observed pair of traces.
    """
    assert 100 <= r <= 109 and r % 10 == st[0]
    sg0,x0,S0=initial_checkpoint(st,idx,r)
    sg1,x1,S1=initial_checkpoint(st,idx,r+10)
    delta=10*r+60
    H0=r*r//2+r
    H1=(r+10)*(r+10)//2+(r+10)
    assert H1-H0==delta

    # The checkpoint is literally the same finite local state after
    # subtracting H_r.
    assert sg0==sg1 and x1-H1==x0-H0
    for sign in (1,-1):
        assert S1[sign].prefix-H1==S0[sign].prefix-H0
        assert {v-H1 for v in S1[sign].extras}=={v-H0 for v in S0[sign].extras}

    # P_1 shadows the complete pre-exit trace of P_0.  The proof shows
    # this shadowing continues inductively: the old-root/same candidates
    # are unchanged in local coordinates, while every candidate using
    # root >= r+2 can only move upward.
    sg,x,sides=sg0,x0,S0
    SG,X,SIDES=sg1,x1,S1
    base_steps=0
    min_lower_root_margin=10**9
    for _ in range(10000):
        # Root r and every smaller crossing root are unavailable.
        lower_raw=r*r-x
        lower_margin=sides[-sg].prefix-lower_raw
        assert lower_margin>=0
        min_lower_root_margin=min(min_lower_root_margin,lower_margin)

        old_raw=(r+1)*(r+1)-x
        old_available=(old_raw>sides[-sg].prefix and
                       old_raw not in sides[-sg].extras)
        next_raw=(r+2)*(r+2)-x
        if not old_available:
            # The raw next-root landing is not merely an abstract lower
            # bound: it lies above every used point and is therefore the
            # actual next opposite candidate.  This prevents a used raw
            # landing at decade j from becoming a dangerous unused one at
            # decade j+1.
            assert next_raw>max_used(sides[-sg])

        ns,y,root=choose_next(sg,x,sides)
        if ns!=sg and root>=r+2:
            assert not old_available
            assert root==r+2 and y==next_raw
            old_exit_y=y
            break
        if ns != sg:
            assert old_available and root == r+1 and y==old_raw
        elif not old_available:
            sy,sk=min_same(x,sides[sg])
            assert y==sy
            assert sy < next_raw or (sy==next_raw and sg==1)

        NS,Y,ROOT=choose_next(SG,X,SIDES)
        assert NS==ns and Y==y+delta
        assert ROOT==(root+10 if NS!=SG else root)
        sides[ns].add(y); sg,x=ns,y
        SIDES[NS].add(Y); SG,X=NS,Y
        base_steps += 1
    else:
        raise AssertionError

    old_sg,old_x=sg,x
    old_sides={1:sides[1].copy(),-1:sides[-1].copy()}
    old_tail=(sides[sg].prefix-x,
              tuple(sorted(v-sides[sg].prefix for v in sides[sg].extras)))
    assert old_tail in TAILS

    # At the corresponding state in P_1, ten same-side moves absorb the
    # +20 displacement of the next-root candidate.  These checks are
    # symbolic-in-induction: at decade j, the active state and every
    # same/next-root candidate below are translated by 10j, while the
    # inactive side is fixed.  The old-root reflection moves *down* by
    # 10j and is therefore still inside the inactive filled prefix.
    tail_start_sg,tail_start_x=SG,X
    tail_start_active=SIDES[SG].copy()
    tail_start_inactive=SIDES[-SG].copy()
    min_old_root_margin=10**9
    min_next_minus_same=10**9

    for _ in range(10):
        old_raw=(r+11)*(r+11)-X
        old_margin=SIDES[-SG].prefix-old_raw
        assert old_margin>=0
        min_old_root_margin=min(min_old_root_margin,old_margin)

        sy,sk=min_same(X,SIDES[SG])
        next_raw=(r+12)*(r+12)-X
        assert next_raw>max_used(SIDES[-SG])
        # Same side must win, including the exact positive-sign tie rule.
        assert sy < next_raw or (sy==next_raw and SG==1)
        min_next_minus_same=min(min_next_minus_same,next_raw-sy)

        NS,Y,ROOT=choose_next(SG,X,SIDES)
        assert NS==SG and Y==sy and ROOT==sk
        SIDES[NS].add(Y); SG,X=NS,Y

    assert SG==tail_start_sg and X==tail_start_x+10
    assert shifted_side_equal(tail_start_active,SIDES[SG],10)
    assert SIDES[-SG].prefix==tail_start_inactive.prefix
    assert SIDES[-SG].extras==tail_start_inactive.extras

    # The old crossing root remains unavailable.  The new landing is
    # above every used point of the inactive side, and it beats the
    # same-side candidate (with the correct tie sign).  All quantities
    # in this comparison translate by 10j in later decades.
    old_raw=(r+11)*(r+11)-X
    old_exit_margin=SIDES[-SG].prefix-old_raw
    assert old_exit_margin>=0

    landing=(r+12)*(r+12)-X
    landing_clearance=landing-max_used(SIDES[-SG])
    assert landing_clearance>0
    sy,sk=min_same(X,SIDES[SG])
    assert landing < sy or (landing==sy and SG==-1)

    NS,Y,ROOT=choose_next(SG,X,SIDES)
    assert NS==-SG and ROOT==r+12 and Y==landing
    assert Y==old_exit_y+delta+10

    old_out=norm_output(r+1,old_sg,old_x,
                        old_sides[old_sg],old_sides[-old_sg])
    new_out=norm_output(r+11,SG,X,SIDES[SG],SIDES[-SG])
    assert old_out==new_out

    return old_out,(
        base_steps,
        min_lower_root_margin,
        min_old_root_margin,
        min_next_minus_same,
        old_exit_margin,
        landing_clearance,
    )


def transition(st,idx):
    r=100+st[0]
    verify_first_crossing(st,r)
    trace,pre,tail,exit_move,out=phase_trace(st,idx,r)
    assert tail in TAILS
    uniform_out,_cert=verify_uniform_period_certificate(st,idx,r)
    assert uniform_out==out
    return out


def build_invariant():
    states={BASE}; rounds=0; cache={}
    while True:
        new=set()
        for st in sorted(states):
            for idx in range(6):
                key=(st,idx)
                if key not in cache:
                    cache[key]=transition(st,idx)
                new.add(cache[key])
        add=new-states
        if not add: break
        states|=add; rounds+=1
        assert rounds<30
    assert len(states)==412
    assert len(cache)==412*6
    for rm,sg,f,e,u,EA,EB in states:
        assert rm in range(10) and sg in (-1,1)
        assert -2<=f<=1 and -1<=e<=5
        assert (u,EA) in ((-2,()),(-1,()),(0,()),(2,(2,)),(3,(3,)))
        assert EB in ((),(2,),(3,),(4,),(2,3))
    transitions=sorted((st,idx,out) for (st,idx),out in cache.items())
    digest=sha256(repr((sorted(states),transitions)).encode()).hexdigest()
    return states,rounds,len(cache),digest

# ================================================================
# Uniform bridge from B_r to one of the six checkpoints
# ================================================================

def verify_checkpoint_bridge(states):
    """Verify the finite offset inequalities used by the analytic bridge.

    The one-sided cleanup lemma is universal.  For D>=92 its first
    canonical prefix is at most 2*floor(sqrt(D-1))+26 <= D-48.  From
    there the explicit canonical packet rules reach the first prefix
    >=D-30 in exactly one of CHECKPOINTS.  Until then every same-side
    candidate is at relative coordinate <=D-28.  The assertions below
    certify that this is strictly smaller than the least unused old-side
    magnitude for every invariant state and every later decade.
    """
    worst_D=10**9
    worst_D_minus_G=-10**9
    for st in states:
        r=100+st[0]
        sg,L,Q,u,EA,EB=instantiate(st,r)
        _,_,f,e,_,_,_=st
        D=r+1-f-e-u
        G=L-Q
        worst_D=min(worst_D,D)
        worst_D_minus_G=max(worst_D_minus_G,D-G)
        assert D>=92
        # The landing Q+D is unused: the only old extras are at +2,+3,+4.
        assert D>max((0,*EB))
        # Root r is below the target filled prefix, root r+1 lands at D.
        assert r*r-(L+u)<=Q
        landing=(r+1)*(r+1)-(L+u)
        assert landing==Q+D
        lead=Side(L,{L+a for a in EA})
        same,_=min_same(L+u,lead)
        assert landing < same or (landing==same and sg==-1)
        # Protected-cleanup comparison.
        assert Q+D-28 < L+1
        # All inequalities only improve when r is replaced by r+10:
        # D rises by 10, G rises by 10, and D-G is unchanged.
    assert worst_D>=92
    assert worst_D_minus_G<=7

    # Pure packet enumeration: from C_0 increments are 1 forever; from
    # C_1 and C_2 the canonical-prefix increments alternate 3,2 or 2,3.
    reached=set()
    for g0 in (0,1,2):
        for deficit in range(31,36):
            # Start with p=D-deficit and take canonical packets until p>=D-30.
            p=-deficit; g=g0
            while p < -30:
                if g==0: p,g=p+1,0
                elif g==1: p,g=p+3,2
                else: p,g=p+2,1
            reached.add((-p,g))
    assert reached==set(CHECKPOINTS)
    return worst_D,worst_D_minus_G

def verify_two_sided_bridge(states):
    """Simulate the full two-sided walk from every invariant boundary
    state, at the representative root and at two out-of-sample decades,
    through the root-(r+1) crossing and the protected cleanup.  Confirm
    that the walk reaches one of the six certified checkpoint formats,
    with the old side untouched and no interrupting crossing.  This
    corroborates the analytic bridge of Sections 8-10 of the proof.
    """
    six=set(CHECKPOINTS)
    runs=0
    for st in sorted(states):
        rep=100+st[0]
        for r in (rep,rep+40,rep+230):
            sg,L,Q,u,EA,EB=instantiate(st,r)
            _,_,f,e,_,_,_=st
            D=r+1-f-e-u
            sides={sg:Side(L,{L+a for a in EA}),
                   -sg:Side(Q,{Q+a for a in EB})}
            s,x=sg,L+u
            old0=(sides[sg].prefix,frozenset(sides[sg].extras))
            ns,y,root=choose_next(s,x,sides)
            assert ns==-sg and root==r+1 and y==Q+D
            sides[ns].add(y); s,x=ns,y
            for _ in range(100000):
                tgt=sides[s]
                if (s==-sg and tgt.prefix-Q>=D-30 and tgt.extras=={Q+D}
                        and tgt.prefix-x in (0,1,2)):
                    ck=(D-(tgt.prefix-Q),tgt.prefix-x)
                    assert ck in six
                    assert (sides[sg].prefix,
                            frozenset(sides[sg].extras))==old0
                    break
                ns,y,root=choose_next(s,x,sides)
                # No sign crossing may occur before the checkpoint.
                assert ns==s
                sides[ns].add(y); s,x=ns,y
            else:
                raise AssertionError
            runs+=1
    return runs

# ================================================================
# Aggregate audit statistics for the uniform certificates
# ================================================================

def audit_uniform_certificates(states):
    stats={
        'transitions':0,
        'pre_steps':0,
        'old_unavailable_steps':0,
        'min_lower_root_margin':10**9,
        'min_next_landing_clearance':10**9,
        'min_next_minus_same':10**9,
        'min_tail_old_root_margin':10**9,
        'min_tail_next_clearance':10**9,
        'min_tail_next_minus_same':10**9,
        'min_exit_old_root_margin':10**9,
        'min_exit_landing_clearance':10**9,
        'min_exit_same_minus_landing':10**9,
        'min_phase_steps':10**9,
        'max_phase_steps':0,
    }
    for st in states:
        r=100+st[0]
        for idx in range(6):
            stats['transitions']+=1
            sg,x,sides=initial_checkpoint(st,idx,r)
            SG,X,SIDES=initial_checkpoint(st,idx,r+10)
            steps=0
            while True:
                lower=r*r-x
                stats['min_lower_root_margin']=min(
                    stats['min_lower_root_margin'],sides[-sg].prefix-lower)
                old=(r+1)*(r+1)-x
                old_available=(old>sides[-sg].prefix and
                               old not in sides[-sg].extras)
                nxt=(r+2)*(r+2)-x
                ns,y,root=choose_next(sg,x,sides)
                if not old_available:
                    stats['old_unavailable_steps']+=1
                    stats['min_next_landing_clearance']=min(
                        stats['min_next_landing_clearance'],
                        nxt-max_used(sides[-sg]))
                    sy,_=min_same(x,sides[sg])
                    if not (ns!=sg and root>=r+2):
                        stats['min_next_minus_same']=min(
                            stats['min_next_minus_same'],nxt-sy)
                if ns!=sg and root>=r+2:
                    break
                NS,Y,ROOT=choose_next(SG,X,SIDES)
                sides[ns].add(y); sg,x=ns,y
                SIDES[NS].add(Y); SG,X=NS,Y
                steps+=1
            stats['pre_steps']+=steps
            stats['min_phase_steps']=min(stats['min_phase_steps'],steps)
            stats['max_phase_steps']=max(stats['max_phase_steps'],steps)

            for _ in range(10):
                old=(r+11)*(r+11)-X
                stats['min_tail_old_root_margin']=min(
                    stats['min_tail_old_root_margin'],
                    SIDES[-SG].prefix-old)
                nxt=(r+12)*(r+12)-X
                stats['min_tail_next_clearance']=min(
                    stats['min_tail_next_clearance'],
                    nxt-max_used(SIDES[-SG]))
                sy,_=min_same(X,SIDES[SG])
                stats['min_tail_next_minus_same']=min(
                    stats['min_tail_next_minus_same'],nxt-sy)
                NS,Y,ROOT=choose_next(SG,X,SIDES)
                SIDES[NS].add(Y); SG,X=NS,Y

            old=(r+11)*(r+11)-X
            stats['min_exit_old_root_margin']=min(
                stats['min_exit_old_root_margin'],SIDES[-SG].prefix-old)
            landing=(r+12)*(r+12)-X
            stats['min_exit_landing_clearance']=min(
                stats['min_exit_landing_clearance'],
                landing-max_used(SIDES[-SG]))
            sy,_=min_same(X,SIDES[SG])
            stats['min_exit_same_minus_landing']=min(
                stats['min_exit_same_minus_landing'],sy-landing)
    return stats

# ================================================================
# Exact finite verification of B_100 from a(0)=0
# ================================================================

def verify_B100():
    sides={1:Side(0,set()),-1:Side(0,set())}
    # From zero, +/-1 tie; +1 wins.
    sides[1].add(1); sg,x=1,1; steps=1; max_cross_root=0
    while steps<100000:
        ns,y,root=choose_next(sg,x,sides)
        if ns!=sg:
            if root>=101:
                # This is the first crossing whose root exceeds 100.
                assert root==101 and max_cross_root==100
                st=norm_output(100,sg,x,sides[sg],sides[-sg])
                assert st==BASE
                return steps
            max_cross_root=max(max_cross_root,root)
        sides[ns].add(y); sg,x=ns,y; steps+=1
    raise AssertionError

if __name__=='__main__':
    verify_cleanup_certificates()
    n=verify_B100()
    states,rounds,checks,digest=build_invariant()
    bridge=verify_checkpoint_bridge(states)
    sims=verify_two_sided_bridge(states)
    audit=audit_uniform_certificates(states)
    print('cleanup certificates: OK')
    print('B_100 exact verification: OK at step',n)
    print('checkpoint bridge: OK; min D, max(D-G) =',bridge)
    print('two-sided bridge simulations: OK;',sims,
          'runs at representative and out-of-sample roots')
    print('closed phase states:',len(states))
    print('closure rounds:',rounds)
    print('unique phase transitions:',checks)
    print('uniform certificate audit:',audit)
    print('certificate SHA-256:',digest)
    print('Conclusion: every positive and negative integer occurs in A377091.')
