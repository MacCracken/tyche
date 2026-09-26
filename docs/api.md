# tyche — Public API (1.x FROZEN)

> **Frozen at v1.0.0 (2026-07-05).** A clean freeze — no behavior change from
> 0.1.1; this documents what four shipping consumers (attn11, tarka, rosnet's
> `t_randn`, anukūlana via rosnet) have exercised unchanged since extraction.
> Additions land as 1.x minors. `_`-prefixed symbols are internal (one
> documented exception below).

**⚠ STATISTICAL, NOT CRYPTOGRAPHIC** — xorshift64 is trivially predictable.
Keys/nonces/tokens/salts → sigil's CSPRNG. tyche is for reproducible-by-seed
sampling: ML init, dropout, Monte Carlo, rollout draws.

## The surface

| fn | contract |
|----|----------|
| `rng_seed(s)` | seed the process-global stream; splitmix64-finalized so small/sequential seeds decorrelate; a seed finalizing to 0 bumps to 1 (xorshift's fixed point). Same seed → same stream (the reproducibility contract; see *Stream stability* for the one correction since 1.0.0). |
| `rng_u64()` | next 64-bit value (Marsaglia xorshift64, shift triple 13/7/17) |
| `rng_uniform()` | f64 in [0,1): the top 53 bits of `rng_u64()` times 2^-53 (exact) |
| `rng_normal()` | standard normal f64 (Marsaglia polar; no sin/cos). Defined bit for bit as `v1 · sqrt((−2 · ln s) / s)` in IEEE-754 binary64, with `ln` computed by tyche's own `_rng_ln` from basic operations — the correctly rounded value on all but one of 10,000,000 draws checked (a hard case 2^-74 from a rounding midpoint) |

## Contract notes (frozen semantics)

- **One process-global stream** (`_rng_state`) — the single-threaded sovereign
  execution model relies on this. Per-stream handles are the flagged unwind
  point for the SMP arc; they will land as an *additive* handle API, never a
  change to these four.
- **State capture exception**: checkpointing consumers read/write `_rng_state`
  directly (attn11's proven save/restore path). That one internal is
  load-bearing and freezes WITH the surface: it stays a single i64 cell, and it
  is the *whole* stream state — `rng_normal` keeps no cached second variate.
  Unseeded, it starts at `88172645463325252`, so the unseeded stream is
  deterministic too.
- **Determinism is bit-exact across platforms.** Integer ops wrap mod 2^64, and
  every f64 operation in the stream is a single correctly rounded IEEE-754 op
  (add, sub, mul, div, sqrt — SSE2 on x86_64, scalar FP on aarch64, never fused).
  tyche uses **no transcendental builtin**: cyrius lowers `f64_ln`, `f64_exp` and
  friends to x87 on x86_64 but to looser software polyfills on aarch64, so their
  bits differ by target. `rng_normal`'s logarithm is tyche's own `_rng_ln`
  (internal, not API), built from the basic ops. CI runs the known-answer suite
  on x86_64 and on aarch64 under qemu; `scripts/kat_reference.py` reproduces
  every stream from the algorithms and an operation-for-operation port of
  `_rng_ln`.

## Stream stability

`rng_seed`, `rng_u64`, `rng_uniform` and `_rng_state` produce the same bits as
at 0.1.0. `rng_normal` changed once, in **1.1.0**, to honour the cross-platform
contract above: through 1.0.3 it called `f64_ln`, so ~34% of aarch64 draws
differed from x86_64 in the low bits, and on x86_64 the x87 logarithm misrounded
about 1 draw in 9,250. From 1.1.0 every target produces one stream. On x86_64,
99.989% of draws are unchanged from 1.0.3, and each of the others (1–3 ulp) is a
draw where x87 had misrounded `ln(s)` — checked over 10,000,000 draws. Pin
`tag = "1.0.3"` only if an old x86_64 run must be bit-reproduced.

## Algorithms / provenance

Marsaglia (2003) xorshift64 · Steele/Lea/Flood (2014) splitmix64 finalizer ·
Marsaglia & Bray (1964) polar normal · Dekker (1971) double-double arithmetic
for `_rng_ln`. See `docs/development/sources.md`.
