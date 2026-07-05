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
| `rng_seed(s)` | seed the process-global stream; splitmix64-finalized so small/sequential seeds decorrelate; a seed finalizing to 0 bumps to 1 (xorshift's fixed point). Same seed → same stream, forever (the reproducibility contract). |
| `rng_u64()` | next 64-bit value (Marsaglia xorshift64, shift triple 13/7/17) |
| `rng_uniform()` | f64 in [0,1) — top 53 bits mapped via 2^53 |
| `rng_normal()` | standard normal f64 (Marsaglia polar; no sin/cos) |

## Contract notes (frozen semantics)

- **One process-global stream** (`_rng_state`) — the single-threaded sovereign
  execution model relies on this. Per-stream handles are the flagged unwind
  point for the SMP arc; they will land as an *additive* handle API, never a
  change to these four.
- **State capture exception**: checkpointing consumers read/write `_rng_state`
  directly (attn11's proven save/restore path). That one internal is
  load-bearing and freezes WITH the surface: it stays a single i64 cell.
- Determinism is bit-exact across platforms: integer ops wrap mod 2^64; f64
  mapping uses exact bit-pattern builtins.

## Algorithms / provenance

Marsaglia (2003) xorshift64 · Steele/Lea/Flood (2014) splitmix64 finalizer ·
Marsaglia & Bray (1964) polar normal. See `docs/development/sources.md`.
