# 0001 — rng_normal uses its own portable ln

**Status**: Accepted
**Date**: 2026-09-25

## Context

tyche's frozen contract (`docs/api.md`) is that the same seed gives the same bits
on every target. `rng_normal` (Marsaglia polar) needs `ln(s)`, and through 1.0.3
it called the `f64_ln` builtin. cyrius lowers that builtin differently per
target: x87 `fyl2x` on x86_64, which is correctly rounded on 99.98% of inputs,
and a Taylor-series polyfill on aarch64, which is correctly rounded on about 50%
of (0,1) and up to 213 ulp off. About a third of aarch64 normal draws differed
from x86_64 in their low bits.

The two halves of the contract pull against each other here. Keeping the x86_64
stream exactly would need an aarch64 `ln` that reproduces x87 bit for bit, which
cannot be guaranteed: x87 is not always correctly rounded, and its results are
not specified across CPU vendors. So any fix changes some x86_64 draws, and the
real choice is how many, and at what cost.

## Decision

`rng_normal` computes `ln(s)` itself, with `_rng_ln`: a table-free double-double
evaluation (Dekker products, no FMA) built only from `f64_add` / `f64_sub` /
`f64_mul` / `f64_div`, which are correctly rounded on every IEEE-754 target.
It carries ~2^-70 of accuracy into the final rounding, so it is correctly
rounded except for hard cases: 9,999,999 of 10,000,000 draws checked, and the
miss lies 2^-74.2 from a rounding midpoint. The stream is therefore defined by
`_rng_ln`'s exact operations. `scripts/kat_reference.py` ports them and
reproduces the stream bit for bit; its `--hard-cases` mode lists the draws
where a correctly rounded `ln` would differ.

Scope: `rng_normal` only. `rng_seed` / `rng_u64` / `rng_uniform` never touched a
transcendental builtin and are unchanged. `_rng_ln` is internal, not API.

## Consequences

- **Positive** — The stream is the same on x86_64 and aarch64 (10,000,000 draws
  compared), and no longer depends on x87 microcode or on a cyrius polyfill.
  Because `_rng_ln` agrees with x87 wherever x87 was correctly rounded, only
  0.011% of x86_64 draws moved (1,081 of 10,000,000, each by 1–3 ulp, every one
  an x87 misround). The stream now has a definition that can be checked
  independently, and CI checks it on both targets.
- **Negative** — `rng_normal` is 3.8× slower (92 → 347 ns on x86_64): about 220
  f64 operations against one x87 instruction. tyche now owns a numerical routine
  and its accuracy argument, and "correctly rounded" is only nearly true: about
  one draw in ten million is a hard case it rounds the other way, so the stream
  is pinned to `_rng_ln`'s exact operations. The 0.011% of x86_64 draws that
  moved is a Breaking change under CONTRIBUTING.md, shipped as 1.1.0.
- **Neutral** — A faster `_rng_ln` is possible (see Alternatives), with a fixed
  acceptance bar: identical bits. The upstream defect is filed in cyrius and no
  longer blocks tyche.

## Alternatives considered

- **Wait for cyrius to fix its aarch64 polyfill.** Even a perfect fix would only
  make aarch64 correct, not identical to x87, and tyche would stay hostage to
  per-target lowering. Filed upstream anyway.
- **Use x87 on x86_64 and tyche's `ln` only on aarch64.** Matches x86_64 on
  ~99.98% of draws, not all of them, and still ties x86_64 to x87 microcode.
  Rejected: not bit-exact.
- **A cheaper, < 1 ulp logarithm (fdlibm's `e_log.c`, ~40 operations).**
  Nearly restores the 1.0.3 speed, but it differs from the correctly rounded
  value on 7.3% of `rng_normal`'s inputs (measured), so roughly 3–4% of x86_64
  draws would move instead of 0.011%. Rejected for stream stability.
- **A 129-entry table reduction.** About as accurate with a third of the
  operations, but adds ~400 lines of constants to a ~250-line library, and as a
  different algorithm it would disagree on rare hard cases. Deferred; see the
  roadmap.
- **Two-phase (Ziv) evaluation.** A cheap first pass is only accurate to
  ~0.2 ulp, so ~40% of calls would fall through to the slow path. No gain.
- **A normal method without ln** (CLT sum of uniforms). Not a true normal.
  Ziggurat still needs exp / ln in its tail and would change the whole stream.
  Rejected.
