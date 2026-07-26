# A Computer-Assisted Proof That OEIS A377091 Is a Permutation of the Integers

> **Main result.** Every integer occurs in A377091; consequently, the sequence is a permutation of $\mathbb Z$.

## Contents

1. [Statement](#1-statement)
2. [Sign/magnitude representation](#2-signmagnitude-representation)
3. [Part I: One-sided cleanup](#part-i-one-sided-cleanup)
4. [Part II: Boundary states and the checkpoint bridge](#part-ii-boundary-states-and-the-checkpoint-bridge)
5. [Part III: Uniform decade conjugacy](#part-iii-uniform-decade-conjugacy)
6. [Part IV: Finite closure and conclusion](#part-iv-finite-closure-and-conclusion)
7. [Reproducibility](#18-reproducibility)
8. [Provenance and acknowledgments](#19-provenance-and-acknowledgments)

### 1. Statement

Let \(a(0)=0\). For \(n\ge 1\), let \(a(n)\) be the unused integer of least absolute value such that

$$
|a(n)-a(n-1)|
$$

is a positive perfect square. If the two candidates \(m\) and \(-m\) have the same absolute value, choose \(+m\).

> **Theorem.** Every integer occurs in this sequence. Therefore A377091 is a permutation of $\mathbb Z$.

The proof has two infinite ingredients, both elementary:

1. a strong-induction cleanup lemma for a one-sided square-jump walk;
2. a uniform decade-conjugacy lemma for two-sided phases.

Everything else is reduced to exact finite verification by the accompanying Python checker. The checker uses only integer arithmetic and exhaustive state enumeration.

---

### 2. Sign/magnitude representation

For each sign, represent the used positive magnitudes by

$$
\mathcal S=(p,E),
$$

where

- every magnitude \(1,\dots,p\) has been used;
- \(E\) is the finite set of used magnitudes greater than \(p\).

The number \(p\) is the **filled prefix**.

If the current sign is \(\sigma\in\{+1,-1\}\) and the current magnitude is \(x\), then:

- a same-sign move goes to an unused magnitude \(y\) with \(|x-y|=k^2\);
- an opposite-sign move goes to an unused magnitude \(z\) with \(x+z=k^2\).

The greedy rule compares the candidate magnitudes \(y\) and \(z\), choosing the smaller. In a tie, it chooses whichever candidate has positive sign.

The checker implements this rule exactly.

---

## Part I. One-Sided Cleanup

### 3. The one-sided walk

Consider the auxiliary walk on the positive integers. Begin at \(N\), with \(N\) and a set

$$
E\subseteq\{2,3,4\}
$$

marked used. Repeatedly choose the least unused positive integer at square distance from the current integer.

#### Canonical states

For \(g\in\{0,1,2\}\), let \(C_g(p)\) denote the state in which

- exactly \(1,\dots,p\) are used;
- there are no extras;
- the current value is \(p-g\).

Their continuations are explicit.

From \(C_0(p)\), the next value is \(p+1\), so

$$
C_0(p)\longrightarrow C_0(p+1).
$$

From \(C_1(p)\), the next three values are

$$
C_1(p):\qquad p+3 \longrightarrow p+2 \longrightarrow p+1.
$$

so

$$
C_1(p)\longrightarrow C_2(p+3).
$$

From \(C_2(p)\), the next two values are

$$
C_2(p):\qquad p+2 \longrightarrow p+1.
$$

so

$$
C_2(p)\longrightarrow C_1(p+2).
$$

Hence the \(C_1,C_2\) modes alternate in packets of lengths \(3,2,3,2,\dots\), and after five newly filled values the same mode returns translated by \(5\). Every canonical mode returns after ten newly filled values translated by \(10\).

---

### 4. One remote marked point

Start in \(C_g(p)\), and additionally mark \(p+L\) used, with \(L\ge 40\).

After the remote point is absorbed and the walk next reaches a canonical state, the result depends only on \(g\) and \(L\bmod 5\).

Write \((d,h)\) when the resulting state is

$$
C_h(p+L+d).
$$

The exact table is:

| Initial mode | \(L\equiv0\) | \(L\equiv1\) | \(L\equiv2\) | \(L\equiv3\) | \(L\equiv4\) |
|---|---:|---:|---:|---:|---:|
| \(C_0\) | \((0,1)\) | \((0,1)\) | \((0,1)\) | \((0,1)\) | \((0,1)\) |
| \(C_1\) | \((13,1)\) | \((0,2)\) | \((8,1)\) | \((5,1)\) | \((1,0)\) |
| \(C_2\) | \((5,1)\) | \((1,0)\) | \((13,1)\) | \((0,2)\) | \((8,1)\) |

The checker verifies one representative for every row and residue class.

Why does that finite check cover every \(L\ge40\)? Replacing \(L\) by \(L+5\) inserts one complete five-value canonical packet before the remote point can interfere. After that packet, the state is translated by \(5\), the canonical mode is unchanged, and the remaining distance to the remote point is again \(L\). Thus the result is exactly periodic in \(L\) modulo \(5\).

---

### 5. Cleanup lemma

> **Lemma 1 (One-sided cleanup).** For every $N\ge 1$ and every $E\subseteq\{2,3,4\}$, the one-sided walk reaches a canonical state $C_g(p)$ satisfying

$$
p\le N+23.
$$

**Proof.**


The checker exhaustively verifies all \(1\le N<100\) and all eight subsets of \(\{2,3,4\}\). The largest overshoot is exactly \(23\).

Now let \(N\ge100\), and assume the lemma for every smaller starting value. Put

$$
\begin{aligned}
q&=\left\lfloor\sqrt{N-1}\right\rfloor,\\
s&=N-q^2.
\end{aligned}
$$

Then \(1\le s\le2q\).

Any candidate \(k<s\) is at distance \(N-k\in(q^2,N-1]\subset(q^2,(q+1)^2)\) from \(N\), which contains no square; so no candidate below \(s\) is reachable.

If \(s\notin E\), the first move is therefore \(s\). If \(s\in E\), then \(s\in\{2,3,4\}\); moreover \(N=q^2+s\le q^2+4\), and since \(N\ge100\) this forces \(q\ge10\). Candidates strictly between \(s\) and \(s+2q-1\) are at distances strictly between \((q-1)^2\) and \(q^2\), again containing no square, while \(s+2q-1\) is at distance \((q-1)^2\). Since \(s+2q-1\ge21>4\), it is not in \(E\), so the first move is

$$
s+2q-1.
$$

Therefore the first move \(y\) always satisfies

$$
y\le2q+3.
$$

Ignore the remote marked point \(N\) temporarily. By strong induction, the walk starting at \(y\), with the same small set \(E\), reaches a canonical state \(C_g(p)\) with

$$
p\le y+23\le2q+26.
$$

For \(N\ge100\), this is strictly less than \(N\). Hence the unmarked comparison walk cannot have selected \(N\) before reaching that canonical state. Marking \(N\) therefore does not alter the path up to that point.

Moreover, the distance \(L=N-p\) is at least \(40\). Apply the remote-point table. The next canonical prefix is at most \(N+13\), hence certainly at most \(N+23\). This closes the induction. \(\square\)

---

## Part II. Boundary States and the Checkpoint Bridge

### 6. Phase boundaries

Let \(B_r\) be the instant immediately before the first sign crossing whose square root is \(r+1\).

At \(B_r\), call the current sign the **leading side**. Write

$$
\begin{aligned}
L&=\left\lceil\frac{r^2}{2}\right\rceil+r+f,\\
Q&=\left\lfloor\frac{r^2}{2}\right\rfloor+e.
\end{aligned}
$$

for the leading and other filled prefixes. Write the current leading magnitude as

$$
L+u.
$$

The normalized state associated with $B_r$ is recorded in labeled coordinates as

$$
B_r=
\left\{
\begin{aligned}
\rho   &= r \bmod 10,\\
\sigma &= \text{current sign},\\
f      &= \text{leading-prefix offset},\\
e      &= \text{other-prefix offset},\\
u      &= \text{current-magnitude offset},\\
E_A    &= \text{leading-side extras relative to }L,\\
E_B    &= \text{other-side extras relative to }Q.
\end{aligned}
\right.
$$

Equivalently, when compact notation is convenient, we write

$$
B_r=(\rho,\sigma,f,e,u,E_A,E_B),
\qquad \rho=r\bmod 10.
$$

The finite invariant found by closure has 412 states. Every one satisfies

$$
-2\le f\le1,
\qquad
-1\le e\le5,
$$

$$
(u,E_A)\in
\{(-2,\varnothing),(-1,\varnothing),(0,\varnothing),(2,\{2\}),(3,\{3\})\},
$$

and

$$
E_B\in
\{\varnothing,\{2\},\{3\},\{4\},\{2,3\}\}.
$$

---

### 7. The first crossing

Let \(\delta=r\bmod2\). At \(B_r\), the candidate using root \(r\) lands at or below the other filled prefix, since

$$
r^2-(L+u)-Q=-r-f-e-u<0.
$$

The root-\((r+1)\) landing is

$$
(r+1)^2-(L+u)=Q+D,
$$

where

$$
D=r+1-f-e-u.
$$

Since \(D\ge92\) from the invariant bounds, this landing is beyond every possible extra on the other side and is unused.

The least same-side candidate and the root-\((r+1)\) landing differ from \(L\) by constants depending only on

$$
(r\bmod2,\sigma,f,e,u,E_A).
$$

The checker exhausts all invariant states and verifies that the crossing candidate wins, including every tie-sign case. Replacing \(r\) by \(r+10\) translates both candidates by the same amount, so this check is uniform for every later root in the same residue class.

Thus the next move from every invariant \(B_r\) is the root-\((r+1)\) crossing.

---

### 8. Reduction to one-sided cleanup

After that crossing, translate the new side by subtracting its old prefix \(Q\). In these relative coordinates:

- the current point is \(D\);
- \(D\) is marked used;
- the only other initially marked positive coordinates are \(E_B\subseteq\{2,3,4\}\).

Therefore, as long as no sign crossing intervenes, the target-side evolution is exactly the one-sided walk of Lemma 1.

Let

$$
G=L-Q.
$$

A direct calculation gives

$$
D-G=1-(r\bmod2)-2f-u\le7.
$$

Hence

$$
G\ge D-7.
$$

---

### 9. Protected cleanup

Let

$$
q=\lfloor\sqrt{D-1}\rfloor.
$$

The first same-side descent from \(D\) is at most \(2q+3\). Apply Lemma 1 to that smaller starting point. The first resulting canonical prefix \(p\) satisfies

$$
p\le2q+26.
$$

For every \(D\ge92\),

$$
2q+26\le D-48.
$$

Thus the walk reaches a canonical state at least 48 places below the landing.

The remote point \(D\) cannot affect this initial cleanup, by the following general excursion bound: every value visited by the walk is used from then on, and at the first canonical state \(C_g(p)\) there are no used values above \(p\); hence the walk never visits any value above \(p\) before reaching that state. In particular, if the comparison walk without \(D\) had selected \(D\), its eventual canonical prefix would be at least \(D\), contradicting \(p\le D-48\). The same excursion bound shows that the entire cleanup stays at or below \(p\le D-48\).

Now continue from that canonical state using the explicit packet rules. Stop after the first complete canonical packet whose filled prefix is at least \(D-30\).

Before that stopping point, every chosen same-side coordinate is at most \(D-28\): the largest packet jump is from a prefix \(D-31\) to \(D-28\).

Therefore every target-side candidate considered before the checkpoint has absolute magnitude at most

$$
Q+D-28.
$$

But

$$
Q+D-28<L+1,
$$

because \(D-G\le7\). Every unused old-side magnitude is at least \(L+1\). Hence every target-side move before the checkpoint is strictly preferred to every sign-crossing candidate. The old side remains untouched.

This proves the required two-sided-to-one-sided reduction.

---

### 10. Exactly six checkpoint formats

Suppose the initial canonical state is \(C_g(p)\), with \(p<D-30\). Let

$$
n=D-30-p.
$$

For \(g=1,2\), only \(n\bmod5\) matters because the packet mode repeats after five filled values. The complete 15-case table is:

| Initial mode | \(n\equiv1\) | \(n\equiv2\) | \(n\equiv3\) | \(n\equiv4\) | \(n\equiv0\) |
|---|---:|---:|---:|---:|---:|
| \(C_0\) | \((30,0)\) | \((30,0)\) | \((30,0)\) | \((30,0)\) | \((30,0)\) |
| \(C_1\) | \((28,2)\) | \((29,2)\) | \((30,2)\) | \((29,1)\) | \((30,1)\) |
| \(C_2\) | \((29,1)\) | \((30,1)\) | \((28,2)\) | \((29,2)\) | \((30,2)\) |

Here \((h,g')\) means:

- the new filled prefix is \(D-h\);
- the current value is \(g'\) behind that prefix.

Thus the possible checkpoints are exactly

$$
\mathcal C=\bigl\{(28,2),(29,1),(29,2),(30,0),(30,1),(30,2)\bigr\}.
$$

At the checkpoint:

- the target side has filled every relative coordinate through \(D-h\);
- it has no local extras;
- the original landing \(D\) is its only extra;
- the old side is unchanged.

The bridge is proved by the analytic chain above: Lemma 1 (valid for every starting value), the excursion bound of Section 9, the protected-cleanup inequality, and the finite packet table. As corroboration, the checker additionally simulates the full two-sided walk from every formal invariant state — at the representative root and at two out-of-sample decades — through the crossing and the cleanup, and confirms in every run that the walk reaches one of precisely these six formats, with no interrupting crossing and the old side untouched.

This closes the first gap in the earlier proof attempt.

---

## Part III. Uniform Decade Conjugacy

### 11. Centered coordinates

Fix a normalized boundary state and one of the six checkpoint types. Let

$$
H_r=\left\lfloor\frac{r^2}{2}\right\rfloor+r.
$$

Subtract \(H_r\) from every magnitude at the checkpoint.

Let \(\delta=r\bmod2\). The old-side prefix becomes

$$
\delta+f.
$$

If the checkpoint type is \((h,g)\), the target-side prefix becomes

$$
1-f-u-h,
$$

its remote landing extra becomes

$$
1-f-u,
$$

and the current target coordinate becomes

$$
1-f-u-h-g.
$$

All of these are independent of \(r\) inside one residue class modulo \(10\).

A same-side square jump is translation-covariant, so its local behavior is independent of \(r\).

A crossing using root \(r+1\) sends local coordinate \(x\) to

$$
1+\delta-x,
$$

also independent of \(r\).

A crossing using root \(r+2\) sends \(x\) to

$$
T_r-x,
\qquad
T_r=2r+4+\delta.
$$

Replacing \(r\) by \(r+10\) changes only this threshold:

$$
T_{r+10}=T_r+20.
$$

This is the key structural fact.

---

### 12. Finite certificate conditions

For each of the 412 normalized states and six checkpoint types, choose the representative

$$
r_0=100+(r\bmod10).
$$

The checker simulates the exact phase at \(r_0\) until immediately before the first crossing using root \(r_0+2\). It certifies at every pre-exit state:

1. **Lower roots are unavailable.** The raw root-\(r_0\) landing lies at or below the opposite filled prefix. Hence every smaller root is unavailable as well.

2. **The old crossing is exact when available.** If the root-\((r_0+1)\) landing is unused, it is the least opposite-side candidate.

3. **The next-root landing is genuinely unused when the old crossing is unavailable.** The raw root-\((r_0+2)\) landing lies above every used point on the opposite side. Thus it is the actual next opposite candidate, not merely a lower bound for one.

4. **Before exit, the chosen move beats that raw next-root landing**, with the exact positive-sign tie rule.

The third item is essential. Without it, a raw landing that was used at one decade could become an unused, unexpectedly competitive landing after the threshold shifts by 20.

Across the complete finite closure, the minimum clearance of a raw next-root landing above every used point is 95.

---

### 13. The ten-move tail certificate

Let \(S_0\) be the pre-exit state of the representative phase \(r_0\).

At root \(r_0+10\), the phase follows the same local trace through \(S_0\), because the same-side and old-root candidates are unchanged while the next-root candidate is 20 larger.

At \(S_0\), the root-\((r_0+12)\) landing is therefore delayed. The checker verifies ten same-side moves with these stronger conditions at every step:

- the root-\((r_0+11)\) reflection lies inside the inactive filled prefix;
- the root-\((r_0+12)\) landing lies above every used inactive point;
- the same-side candidate wins, with the exact tie rule.

After the ten moves:

- the active side, including its prefix, extras, and current point, is translated by \(10\);
- the inactive side is unchanged;
- the old-root reflection is still used;
- the root-\((r_0+12)\) landing is unused;
- that landing wins the next comparison, with the exact tie rule.

The minimum old-root margin during these tails is 100, and the minimum next-root clearance is 107.

---

### 14. Uniform decade lemma

> **Lemma 2 (Uniform decade conjugacy).** For a fixed normalized boundary state and checkpoint type, the normalized phase output is the same for every

$$
r=r_0+10j,
\qquad j\ge0.
$$

**Proof.**


Let \(P_j\) be the phase with root parameter

$$
r_j=r_0+10j,
$$

written in \(H_{r_j}\)-centered coordinates.

The initial local state is identical for every \(j\).

We prove simultaneously by induction that:

1. \(P_{j+1}\) shadows all pre-exit moves of \(P_j\);
2. at the pre-exit state \(S_j\), the active side is the active side of \(S_0\) translated by \(10j\), while the inactive side is identical to that of \(S_0\);
3. the root-\((r_j+2)\) landing is unused and is the actual exit candidate.

The base case is certified exactly by the checker.

Assume the statements for \(j\). During the shadow segment, same-side candidates and root-\((r_j+1)\) reflections have identical local coordinates in \(P_j\) and \(P_{j+1}\). Lower roots remain unavailable because their local landing coordinates decrease when \(r\) increases. Whenever the old crossing is unavailable, the raw next-root landing in \(P_j\) is unused and above all used points; in \(P_{j+1}\) it is shifted upward by 20. Therefore it cannot create an earlier move. So \(P_{j+1}\) shadows \(P_j\) through \(S_j\).

At \(S_j\), the active side is translated by \(10j\) and the inactive side is fixed. During the ten certified tail moves:

- every same-side candidate is the corresponding base candidate translated by \(10j\);
- every root-\((r_{j+1}+2)\) candidate is also the corresponding base candidate translated by \(10j\);
- every root-\((r_{j+1}+1)\) reflection is the corresponding base reflection shifted downward by \(10j\).

Hence all ten comparisons have exactly the same outcome as in the finite certificate. The active side gains another translation by 10, the inactive side remains fixed, and the next move is the root-\((r_{j+1}+2)\) exit. This establishes the induction.

Finally, when \(r\) increases by 10, the normalization used at the next boundary increases by exactly the same amount as the two pre-exit sides:

- the active side gains the common checkpoint translation plus 10;
- the inactive side gains only the common checkpoint translation.

Therefore the normalized output state is identical. \(\square\)

This closes the second gap in the earlier proof attempt. The period certificate is now inductive and uniform, not observational.

---

## Part IV. Finite Closure and Conclusion

### 15. Exact base boundary

The checker generates the sequence exactly from \(a(0)=0\) until the first crossing whose root exceeds 100. It verifies that this is a root-101 crossing and that the preceding boundary is

$$
\boxed{
B_{100}:\quad
\begin{aligned}
\rho   &= 0,          & \sigma &= +,\\
f      &= 0,          & e      &= 0,\\
u      &= 2,          & E_A    &= \{2\},\\
&& E_B &= \varnothing.
\end{aligned}
}
$$

In compact coordinate notation, this is

$$
B_{100}=(0,+,0,0,2,\{2\},\varnothing).
$$

This occurs after 10,101 terms have been placed after the initial zero convention used by the checker.

---

### 16. Finite state closure

Starting from \(B_{100}\), the checker does the following:

1. for every discovered normalized state, allow all six checkpoint formats;
2. simulate the representative phase for each state/checkpoint pair;
3. verify the uniform decade certificate described above;
4. normalize the output boundary state;
5. add every output and repeat until no new state occurs.

The closure stabilizes after 13 rounds with

- 412 normalized states;
- 2472 state/checkpoint transitions.

Every output lies in the same 412-state set.

The aggregate uniform-certificate audit covers

- 335,888 representative pre-exit moves;
- 265,176 states where the old crossing was unavailable;
- phase lengths from 128 to 145 moves at the representative roots.

The exact state-transition digest is

```text
f90edef78a8f1ea482db3ed491a59b663718e1037626f274a1cbf78448e952ce
```

---

### 17. Completion

Assume the actual walk is at an invariant boundary \(B_r\), with \(r\ge100\).

- Section 7 proves that the next move is the root-\((r+1)\) crossing.
- Sections 8–10 prove that the actual walk reaches one of the six certified checkpoints, with the old side unchanged.
- Lemma 2 and the finite closure produce an invariant boundary \(B_{r+1}\).

By induction, an invariant boundary \(B_r\) exists for every \(r\ge100\).

At every invariant boundary,

$$
Q=\left\lfloor\frac{r^2}{2}\right\rfloor+e
$$

with \(e\ge-1\). Thus both signs have filled every magnitude through at least

$$
\left\lfloor\frac{r^2}{2}\right\rfloor-1.
$$

This tends to infinity. Therefore, for every positive integer \(m\), both \(+m\) and \(-m\) eventually occur.

Since the construction never repeats an integer,

$$
\boxed{\text{A377091 is a permutation of }\mathbb Z}
$$

---

### 18. Reproducibility

Run:

```bash
python3 A377091_proof_checker_v4.py
```

The checker verifies:

- the one-sided cleanup certificates;
- the exact boundary \(B_{100}\);
- the checkpoint bridge inequalities and packet table;
- 1,236 full two-sided bridge simulations at representative and out-of-sample roots;
- the 412-state closure;
- all 2472 uniform decade certificates;
- the aggregate safety margins listed above.

The `independent_verification/` directory contains separately written scripts that regenerate the sequence from the OEIS definition by brute force, extract all 607 boundary states of the first 500,000 terms, and confirm that every one lies in the 412-state closure and that all 606 consecutive phase transitions match the checker's representative-root predictions.

The proof remains a new, computer-assisted argument and should be independently reviewed before being treated as accepted literature.

---

### 19. Provenance and acknowledgments

This proof was developed with substantial AI assistance. The argument and checker were generated with OpenAI's ChatGPT under the direction of the author, who posed the problem and directed revisions. Independent adversarial auditing — including brute-force cross-validation against 500,000 exact terms of the sequence, identification of two gaps in an earlier version (an unverified boundary-to-checkpoint bridge, and a decade-conjugacy certificate that was observational rather than inductive), and verification of the revised argument — was carried out with Anthropic's Claude. The author takes responsibility for the correctness claims made here and welcomes scrutiny of both the mathematics and the code.
