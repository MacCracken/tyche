# tyche — Current State

> Refreshed every release. CLAUDE.md is preferences/process/procedures
> (durable); this file is **state** (volatile).

## Version

**1.1.0** (2026-09-25) — the audit release. `rng_normal` is now bit-identical on
every target: it uses tyche's own logarithm (`_rng_ln`, correctly rounded on
9,999,999 of 10,000,000 draws checked) instead of the `f64_ln` builtin, which is
x87 on x86_64 and a looser polyfill on aarch64. On x86_64, 1,081 of 10,000,000
draws moved by 1–3 ulp, every one a draw x87 had misrounded; everything else in
the stream is unchanged since 0.1.0. See
[`../audit/2026-09-25-audit.md`](../audit/2026-09-25-audit.md) and
[ADR 0001](../adr/0001-rng-normal-uses-its-own-portable-ln.md).

**1.0.0** — **stable, API frozen** (cut 2026-07-05). A clean freeze with no
behavior change from 0.1.1: what four shipping consumers (attn11, tarka, rosnet
`t_randn`, anukūlana via rosnet) had exercised unchanged since extraction — the
multi-consumer soak was the readiness evidence. Frozen 1.x surface in
[`docs/api.md`](../api.md): `rng_seed` / `rng_u64` / `rng_uniform` / `rng_normal`,
plus the documented `_rng_state` checkpoint-capture exception. One process-global
stream (per-stream handles are the flagged SMP-arc unwind point, additive when it
comes); bit-exact determinism across targets; **statistical, NOT cryptographic**
(crypto → sigil). Prior: **0.1.1** — scaffolded 2026-06-11 via `cyrius init`.

## Toolchain

- **Cyrius pin**: `6.6.6` (in `cyrius.cyml [package].cyrius`)

**Pin bumped `6.6.2` → `6.6.6` 2026-09-25 (1.0.3).** `lib/` byte-matches the 6.6.6
snapshot (111 files) and `cyrius.lock` covers all of them (`cyrius deps --verify`
clean). A pin bump here is three steps, not one: `cyrius lib sync --full`; delete
any `lib/` file the new snapshot no longer ships (`diff -rq lib
~/.cyrius/versions/<pin>/lib` — `lib sync` does not prune); then `cyrius deps
--lock`, because plain `cyrius deps` resolves no `[deps.NAME]` for tyche and so
never rewrites the lock. 1.0.1 and 1.0.2 each skipped part of this.

## Source

- `src/rng.cyr` — the library (the `[lib]` bundle): `rng_seed` (splitmix64-
  finalized), `rng_u64` (xorshift64, 13/7/17), `rng_uniform` (top 53 bits ×
  2^-53), `rng_normal` (Marsaglia polar, N(0,1)), and the internal `_rng_ln`
  (double-double; correctly rounded but for rare hard cases, about 1 in 10^7
  draws). Uses only compiler builtins — no stdlib
  module — and among the f64 builtins only the correctly rounded basics.
- `src/main.cyr` — smoke demo (`[build].entry`); excluded from `dist/tyche.cyr`.
- `src/test.cyr` — `[build].test` entry (no-op gate; real tests in `tests/`).
- `dist/tyche.cyr` — consumable bundle, regenerated via `cyrius distlib`.
- `scripts/kat_reference.py` — independent reference implementation; source of
  the known-answer vectors.

## Tests

- `tests/tyche.tcyr` — **49 passed, 0 failed**, on x86_64 and on aarch64
  (qemu, in CI). 39 exact-bit assertions (unseeded stream, seed finalizer at
  edge seeds, u64 / uniform / normal / `_rng_ln` vectors, the seed-1481 guard
  against `f64_ln` returning, the `_rng_state` checkpoint) and 10 statistical.
- `tests/tyche.fcyr` — properties over 100,005 seeds, `_rng_ln` monotonicity
  and powers of two; x86_64 and aarch64.
- `tests/tyche.bcyr` — every entry point; numbers in
  [`../benchmarks.md`](../benchmarks.md).

## Dependencies

Direct (declared in `cyrius.cyml`):

- stdlib — string, fmt, alloc, io, vec, str, syscalls, assert, bench, math

No `[deps.NAME]` git deps. Since 1.1.0 the library itself needs none of the
declared stdlib: the list serves the tests, benchmarks and smoke demo, and
`dist/tyche.deps` passes it on to consumers unchanged.

## Consumers

Eight, all on `[deps.tyche] tag = "1.0.1"` (surveyed 2026-09-25; none on 1.0.2
or later yet): agnosai, agnostic, amuzesh, attn11, prajna, rosnet, tarka, tentib.
Seven of them have suites that call tyche, and each gives the same result with
1.1.0 as with 1.0.1 under its pinned cyrius 6.6.2. agnosai's one failing
assertion (`sandbox_spawn.tcyr`, unrelated) fails identically with both.
agnostic makes no `rng_*` call.

## Known trade-offs

- **`rng_normal` is 3.8× slower** than at 1.0.3 (347 ns against 92 ns), the price
  of a near-correctly-rounded logarithm from basic ops. Options are costed in
  [`../benchmarks.md`](../benchmarks.md); a faster `_rng_ln` must keep identical
  bits.

## Upstream

- cyrius `docs/development/issues/2026-09-25-tyche-aarch64-f64-ln-polyfill-specials-and-accuracy.md`
  — aarch64 `f64_ln` / `f64_log2` / `f64_exp`: wrong IEEE special values, and up
  to 213 / 92 / 2,313 ulp of error. tyche no longer depends on the fix.

## Next

See [`roadmap.md`](roadmap.md).
