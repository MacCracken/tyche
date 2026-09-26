# tyche — Roadmap

> Milestone plan. State lives in [`state.md`](state.md); this file is the
> sequencing — what shipped, what is next, and against what dependency gates.

## v1.0 criteria

Set at scaffold time. 1.0.0 (2026-07-05) was cut on the multi-consumer soak;
three criteria and the exact-stream tests were only met in the 1.1.0 audit.

- [x] Public API frozen — [`docs/api.md`](../api.md), at 1.0.0
- [x] Every exported symbol documented and tested — exact-bit vectors for each
  entry point and for `_rng_state`, at 1.1.0
- [x] Test coverage adequate for the surface area — 49 assertions (39 exact),
  property fuzzing, and a CI run on aarch64, at 1.1.0
- [x] Benchmarks captured in [`docs/benchmarks.md`](../benchmarks.md) — at 1.1.0
- [x] At least one downstream consumer green — eight consumers; seven suites
  re-run against 1.1.0 with results identical to 1.0.1 (six fully green;
  agnosai's one failure is pre-existing and unrelated)
- [x] CHANGELOG complete from v0.1.0 onward
- [x] Security audit pass — [`docs/audit/2026-09-25-audit.md`](../audit/2026-09-25-audit.md), at 1.1.0

## Shipped

- **0.1.0** (2026-06-11) — scaffold; the PRNG extracted from attn11's tensor layer.
- **0.1.1** — toolchain pin 6.2.11.
- **1.0.0** (2026-07-05) — API freeze, no behavior change.
- **1.0.1 – 1.0.3** (2026-08-17 → 2026-09-25) — toolchain pins 6.5.27, 6.6.2, 6.6.6.
- **1.1.0** (2026-09-25) — full audit. `rng_normal` made bit-identical across
  targets with tyche's own portable `ln`; exact-bit test vectors, an
  aarch64 CI leg, real benchmarks and fuzzing.

## Next (unscheduled)

- **Consumers onto 1.1.0.** All eight pin `tag = "1.0.1"`; see
  [`state.md`](state.md). Nothing in their suites changes (checked for seven).
- **Per-stream handles** — the SMP-arc unwind point flagged in `src/rng.cyr` and
  `docs/api.md`: a seeded state passed explicitly, so reproducibility survives
  threads. Additive; the four frozen functions stay as they are. Gate: the SMP
  arc itself.
- **A faster `_rng_ln`** — `rng_normal` costs 347 ns against 92 ns at 1.0.3.
  A table-driven reduction is costed in [`docs/benchmarks.md`](../benchmarks.md).
  ⚠ Any different algorithm will disagree with today's `_rng_ln` on some hard
  cases (today's misrounds about one draw in ten million), so it is a stream
  change: it needs the known-answer vectors to hold, a 10M-draw comparison with
  every differing draw accounted for, and a Breaking entry like 1.1.0's.

## Out of scope

- **Cryptographic randomness** — sigil's domain; tyche is statistical only.
- **A shared stream across threads** — the answer is per-stream handles, not
  locking the global stream.
