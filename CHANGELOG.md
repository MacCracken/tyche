# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [1.0.0] - 2026-07-05

**v1.0 — a clean freeze.** No behavior change from 0.1.1: this cut freezes
what four shipping consumers (attn11, tarka, rosnet `t_randn`, anukūlana via
rosnet) have exercised unchanged since extraction — the multi-consumer soak
is the readiness evidence. Surface: `rng_seed` / `rng_u64` / `rng_uniform` /
`rng_normal` (+ the documented `_rng_state` checkpoint-capture exception).

### Added
- **`docs/api.md`** — the frozen 1.x surface with contract notes: one
  process-global stream (per-stream handles = the flagged SMP-arc unwind
  point, additive when it comes), bit-exact cross-platform determinism, the
  STATISTICAL-not-cryptographic boundary (crypto → sigil), and the
  `_rng_state` exception (checkpointing consumers capture it directly —
  attn11's proven path — so it freezes as a single i64 cell).

## [0.1.1]

### Changed
- Bumped Cyrius toolchain pin to `6.2.11` (`cyrius.cyml [package].cyrius`).

## [0.1.0]

### Added
- Initial project scaffold.
- Deterministic statistical PRNG (`src/rng.cyr`), extracted from attn11's tensor
  layer at its v1 freeze: `rng_seed` (splitmix64-finalized), `rng_u64`
  (xorshift64, 13/7/17), `rng_uniform` (top-53-bit → [0,1)), `rng_normal`
  (Marsaglia polar, N(0,1)).
- Statistical test suite (`tests/tyche.tcyr`): seed determinism, seed
  sensitivity, zero-fixed-point guard, uniform range + mean≈0.5, normal
  mean≈0/variance≈1 over 200k draws. 10/10 passing.
- `dist/tyche.cyr` consumable bundle via `cyrius distlib`.
- CI/release workflows (`.github/workflows/`): toolchain installed via upstream
  `install.sh` (pin from `cyrius.cyml`, the form that passes `cyrius deps`
  pin-check), `workflow_call` CI gate, fmt/lint (120-char banner tolerated),
  build+ELF+smoke, statistical tests, bench, fuzz, **distlib drift gate** (fails
  if `dist/tyche.cyr` lags `src/`), and a tag-driven release that ships the
  source tarball + version-stamped `dist/tyche.cyr` + SHA256SUMS. Modeled on
  patra/sigil.

### Boundary
- **Not a CSPRNG.** Statistical/reproducible use only — keys, nonces, tokens,
  and provable fairness must use sigil. Documented in README and the module header.
