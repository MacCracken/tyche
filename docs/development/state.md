# tyche — Current State

> Refreshed every release. CLAUDE.md is preferences/process/procedures
> (durable); this file is **state** (volatile).

## Version

**1.0.0** — **stable, API frozen** (cut 2026-07-05). A clean freeze with no
behavior change from 0.1.1: what four shipping consumers (attn11, tarka, rosnet
`t_randn`, anukūlana via rosnet) had exercised unchanged since extraction — the
multi-consumer soak was the readiness evidence. Frozen 1.x surface in
[`docs/api.md`](../api.md): `rng_seed` / `rng_u64` / `rng_uniform` / `rng_normal`,
plus the documented `_rng_state` checkpoint-capture exception. One process-global
stream (per-stream handles are the flagged SMP-arc unwind point, additive when it
comes); bit-exact cross-platform determinism; **statistical, NOT cryptographic**
(crypto → sigil). Prior: **0.1.1** — scaffolded 2026-06-11 via `cyrius init`.

⚠ **No consumer has moved onto the 1.0.0 tag.** attn11, tentib, prajna, tarka,
rosnet and amuzesh all still declare `[deps.tyche] tag = "0.1.1"`. The freeze is
real; its propagation is not.

## Toolchain

- **Cyrius pin**: `6.5.27` (in `cyrius.cyml [package].cyrius`)

**Pin bumped to `6.5.27` 2026-08-17** (ecosystem-wide ML/AI-arc realign, ahead of the arc reopening). `cyrius lib sync --full` re-vendored the whole version-matched stdlib snapshot; suite re-verified green at the new pin.

## Source

- `src/rng.cyr` — the PRNG library surface (the `[lib]` bundle): `rng_seed`
  (splitmix64-finalized), `rng_u64` (xorshift64, 13/7/17), `rng_uniform`
  (top-53-bit → [0,1)), `rng_normal` (Marsaglia polar, N(0,1)).
- `src/main.cyr` — smoke demo (`[build].entry`); excluded from `dist/tyche.cyr`.
- `src/test.cyr` — `[build].test` entry (no-op gate; real tests in `tests/`).
- `dist/tyche.cyr` — consumable bundle, regenerated via `cyrius distlib`.

## Tests

- `tests/tyche.tcyr` — statistical suite: determinism, seed sensitivity,
  zero-fixed-point guard, uniform range/mean, normal mean/variance over 200k
  draws. **10 passed, 0 failed.**
- `tests/tyche.bcyr` — benchmark (no-op baseline)
- `tests/tyche.fcyr` — fuzz stub

## Dependencies

Direct (declared in `cyrius.cyml`):

- stdlib — string, fmt, alloc, io, vec, str, syscalls, assert, bench, math

## Consumers

_None yet._

## Next

See [`roadmap.md`](roadmap.md).
