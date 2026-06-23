# tyche — Current State

> Refreshed every release. CLAUDE.md is preferences/process/procedures
> (durable); this file is **state** (volatile).

## Version

**0.1.1** — scaffolded 2026-06-11 via `cyrius init`.

## Toolchain

- **Cyrius pin**: `6.2.11` (in `cyrius.cyml [package].cyrius`)

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
