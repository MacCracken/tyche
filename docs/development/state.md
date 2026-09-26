# tyche — Current State

> Refreshed every release. CLAUDE.md is preferences/process/procedures
> (durable); this file is **state** (volatile).

## Version

**1.0.3** (2026-09-25) — toolchain maintenance; 1.0.1–1.0.3 carry no source
change, so the stream is still exactly the 1.0.0 one.

**1.0.0** — **stable, API frozen** (cut 2026-07-05). A clean freeze with no
behavior change from 0.1.1: what four shipping consumers (attn11, tarka, rosnet
`t_randn`, anukūlana via rosnet) had exercised unchanged since extraction — the
multi-consumer soak was the readiness evidence. Frozen 1.x surface in
[`docs/api.md`](../api.md): `rng_seed` / `rng_u64` / `rng_uniform` / `rng_normal`,
plus the documented `_rng_state` checkpoint-capture exception. One process-global
stream (per-stream handles are the flagged SMP-arc unwind point, additive when it
comes); bit-exact determinism (cross-platform for all but `rng_normal` — see
*Known gaps*); **statistical, NOT cryptographic** (crypto → sigil). Prior:
**0.1.1** — scaffolded 2026-06-11 via `cyrius init`.

## Toolchain

- **Cyrius pin**: `6.6.6` (in `cyrius.cyml [package].cyrius`)

**Pin bumped `6.6.2` → `6.6.6` 2026-09-25.** `lib/` byte-matches the 6.6.6
snapshot (111 files) and `cyrius.lock` covers all of them (`cyrius deps --verify`
clean). A pin bump here is three steps, not one: `cyrius lib sync --full`; delete
any `lib/` file the new snapshot no longer ships (`diff -rq lib
~/.cyrius/versions/<pin>/lib` — `lib sync` does not prune); then `cyrius deps
--lock`, because plain `cyrius deps` resolves no `[deps.NAME]` for tyche and so
never rewrites the lock. 1.0.1 and 1.0.2 each skipped part of this.

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

No `[deps.NAME]` git deps. `math` is load-bearing on aarch64 only: there,
`f64_ln` lowers to `_f64_ln_polyfill` from `lib/math.cyr`.

## Consumers

Eight, all on `[deps.tyche] tag = "1.0.1"` (surveyed 2026-09-25; none on 1.0.2
or later yet): agnosai, agnostic, amuzesh, attn11, prajna, rosnet, tarka, tentib.

## Known gaps

- **`rng_normal` is not bit-exact across x86_64 and aarch64.** `rng_seed`,
  `rng_u64` and `rng_uniform` are; `rng_normal` diverges in the low bits
  (a golden dump differs on 220 of 1,952 lines — identically at 6.6.2 and
  6.6.6, so it predates 1.0.3). Cause: cyrius's `f64_ln`. On x86_64 it is x87
  and effectively correctly rounded (19,981 / 20,000 inputs in (0,1) match
  glibc `log`, max 1 ULP); on aarch64 it is `_f64_ln_polyfill`, which matches
  on ~50% with a mean error of 7.2 ULP and a max of 211. `sqrt` / `div` /
  `mul` / `add` agree bit-for-bit. This contradicts `docs/api.md`'s
  "bit-exact across platforms" line. Not yet filed upstream.

## Next

See [`roadmap.md`](roadmap.md).
