# A computer-assisted proof that OEIS A377091 is a permutation of the integers

**Author:** Akshaj Satyawada (University of Pennsylvania)
**Status:** New and unreviewed. Independent expert review is invited before
this should be treated as an accepted result.

## Claim

Conjecture 1 on the OEIS entry for A377091 (Sloane, Dec 2024): every integer,
positive and negative, appears in the sequence. This package contains a
computer-assisted proof of that conjecture. It does not address Conjectures
2-4, although the invariant here gives quantitative filling bounds related in
spirit to Conjecture 4.

## Contents

- `A377091_proof_revised_3.md` — the proof document.
- `A377091_proof_checker_v4.py` — the exact-arithmetic checker. Verifies the
  one-sided cleanup certificates, the base boundary B_100, the checkpoint
  bridge inequalities and packet table, 1,236 full two-sided bridge
  simulations (representative and out-of-sample roots), the 412-state
  closure, and all 2,472 uniform decade certificates. Pure Python 3, no
  dependencies, no floating point.
- `independent_verification/` — separately written scripts that regenerate
  the sequence by brute force directly from the OEIS definition, extract all
  607 phase-boundary states in the first 500,000 terms, and confirm that
  every one lies in the closure and that all 606 consecutive phase
  transitions match the checker's predictions. See the README inside.

## Reproduction

```bash
python3 A377091_proof_checker_v4.py
```

Expected final line: `Conclusion: every positive and negative integer occurs
in A377091.` The state-transition digest is
`f90edef78a8f1ea482db3ed491a59b663718e1037626f274a1cbf78448e952ce`.

## Provenance

This proof was developed with substantial AI assistance, disclosed in full in
Section 19 of the proof document. The mathematical argument and checker were
generated with OpenAI's ChatGPT under the author's direction. Independent
adversarial auditing — including the brute-force cross-validation in
`independent_verification/`, the identification of two genuine gaps in an
earlier version, and the verification of the revised argument — was carried
out with Anthropic's Claude. The author takes responsibility for the
correctness claims and welcomes scrutiny of both the mathematics and the
code.
