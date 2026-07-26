# Independent verification scripts

These scripts were written separately from the proof and checker, as an
adversarial audit. They implement the sequence directly from the OEIS
definition by brute force and test the proof's claims against ground truth.

Run order (from this directory, with the checker copied in or adjacent):

1. `gen.py` — generates 500,000 exact terms (matches the 62 published OEIS
   terms), records all phase-boundary states, writes `boundaries.pkl`.
2. `onesided.py` — independently verifies the canonical packet dynamics, the
   cleanup lemma base case (max overshoot exactly 23), and the 15-entry
   remote-point table for every L in 40..99.
3. `checkpoint.py` — extracts the checkpoint type of every real phase;
   confirms zero interrupting crossings, exactly the six claimed formats,
   and that (state, residue, checkpoint) determines the next boundary with
   zero conflicts across 607 phases.
4. `crossval.py` — cross-validates the checker's mechanics against the
   brute-force generator over 100,000 terms; confirms all 607 empirical
   boundary states lie in the 412-state closure and that the checker's
   representative-root transition table predicts all 606 real transitions
   with zero disagreements.
5. `bridge_audit.py` — independently re-verifies the 15-case checkpoint
   packet table by direct simulation, and runs the full two-sided bridge
   from all 412 states at representative and out-of-sample roots.
