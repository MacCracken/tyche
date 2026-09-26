# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [1.0.3] - 2026-09-25

### Changed

- **Toolchain `6.6.2` → `6.6.6`** (through 6.6.3–6.6.5). No source change, and
  the output did not move: a golden dump of raw `rng_u64` / `rng_uniform` /
  `rng_normal` bit patterns (10 edge seeds including 0, -1 and the i64
  extremes, plus three 1M-round digests) is bit-identical between 1.0.2 @ 6.6.2
  and 1.0.3 @ 6.6.6, on x86_64 and separately on aarch64 (qemu). **10
  assertions** pass. None of the upstream upgrade notes reach tyche: the 6.6.5
  aarch64 `SYS_UNLINKAT` renumber and the 6.6.6 Windows `O_APPEND` / `O_TRUNC`
  fix (tyche never opens or unlinks a file), or 6.6.6's new global-redeclaration
  and top-level-block-scope rules (tyche has neither shape). The shipped DCE
  smoke binary grows 15,712 → 20,456 B, all of it the stdlib's.
- **Vendored `lib/` re-synced** (`cyrius lib sync --full`) and now byte-matches
  the 6.6.6 snapshot, 111 files: adds `alloc_cx.cyr`, `boxed.cyr` and
  `hashseed.cyr`, and removes `lib/agnosys.cyr` — retired from the stdlib at
  v6.2.37, never included by tyche, and left behind because `lib sync` does not
  prune. This also completes the re-sync 1.0.2 left partial: its twelve folded
  stdlibs (sigil, patra, mabda, …) had stayed behind the 6.6.2 pin, which is
  what the `./lib/ shadows version-pinned` build warning was reporting.
- **`cyrius.lock` regenerated** (`cyrius deps --lock`): 111 files, and
  `cyrius deps --verify` is clean. It had gone stale — by 1.0.2, 35 of its 100
  hashes no longer matched `lib/` — because plain `cyrius deps` only rewrites
  the lock when it resolves a `[deps.NAME]` entry, and tyche has none.
- **CI: `actions/checkout` `v4` → `v7`, `softprops/action-gh-release` `v2` →
  `v3`.** Both are runtime moves (Node 20 → Node 24) with no input changes:
  gh-release v3 still takes `name` / `body_path` / `prerelease` / `files`, and
  checkout v7's new fork-checkout refusal applies only to `pull_request_target`
  / `workflow_run`, which tyche does not use.

## [1.0.2] - 2026-09-11

### Changed

- **Toolchain `6.5.27` → `6.6.2`.** No source change — the largest pin jump in
  this sweep so far, and it needed nothing. tyche has no `Result` / `Option` /
  `Either` surface at all, so the 6.6.0 value form cannot reach it: zero compiler
  rejections, zero fail-open sites, zero collisions. **10 assertions** pass.

  Its six `callptr` sites were each traced to their target sets; none reaches a
  pair-returning function.

## [1.0.1] - 2026-08-17

### Changed

- **Cyrius pin `6.5.10` -> `6.5.27`** (2026-08-17, ecosystem-wide ML/AI-arc realign ahead of
  the arc reopening). `cyrius lib sync --full` re-vendored the whole version-matched stdlib
  snapshot, clearing the toolchain-drift and `./lib/ shadows version-pinned` warnings.
  Suite unchanged and green at the new pin: **10/10 assertions**, identical to the pre-bump baseline.

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
