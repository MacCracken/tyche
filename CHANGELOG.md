# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

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

### Boundary
- **Not a CSPRNG.** Statistical/reproducible use only — keys, nonces, tokens,
  and provable fairness must use sigil. Documented in README and the module header.
