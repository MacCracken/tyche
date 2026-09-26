# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [1.1.0] - 2026-09-25

The audit release: a full sweep of tyche, recorded in
[`docs/audit/2026-09-25-audit.md`](docs/audit/2026-09-25-audit.md). Its one
behavior change makes `rng_normal` keep the frozen API's cross-platform promise.

### Breaking

- **`rng_normal` gives the same bits on every target, which moves 0.011% of
  x86_64 draws by 1–3 ulp.** Through 1.0.3 it called the `f64_ln` builtin, which
  cyrius lowers to x87 `fyl2x` on x86_64 but to a software polyfill on aarch64
  that is up to 213 ulp off. About a third of aarch64 normal draws differed from
  x86_64 in their low bits, against `docs/api.md`'s "bit-exact across
  platforms". `rng_normal` now uses tyche's own logarithm, `_rng_ln` (internal),
  built from basic IEEE operations in double-double arithmetic. It was the
  correctly rounded value on 9,999,999 of 10,000,000 draws checked; the other is
  a hard case 2^-74 from a rounding midpoint. The stream is identical on x86_64
  and aarch64 across 10,000,000 consecutive draws, and
  `scripts/kat_reference.py` reproduces it with an operation-for-operation port.
  - **x86_64:** 1,081 of 10,000,000 draws change: 959 by 1 ulp, 121 by 2, one
    by 3. Each is a draw where x87 misrounded `ln(s)`, checked against a
    correctly rounded reference over all 10,000,000; the other 99.989% are
    bit-identical to 1.0.3.
  - **aarch64:** now produces the x86_64 stream.
  - **Unchanged, bit for bit:** `rng_seed`, `rng_u64`, `rng_uniform`, `_rng_state`.

  **Migration:** none, unless you compare against `rng_normal` output saved from
  1.0.3 or earlier. The consumers' suites do not: the seven that call tyche give
  identical results against 1.1.0 and 1.0.1 (agnostic makes no call). To
  bit-reproduce an old x86_64 run, pin `tag = "1.0.3"`.

### Changed

- **`rng_normal` costs 347 ns per draw, up from 92 ns** (x86_64; see
  [`docs/benchmarks.md`](docs/benchmarks.md)). The portable logarithm is about
  220 double-double operations. A cheaper < 1 ulp logarithm (fdlibm's,
  which misrounds 7.3% of these inputs) would have moved roughly 3–4% of x86_64
  draws instead of 0.011%, and stream stability won. `rng_seed` / `rng_u64` / `rng_uniform` are unchanged at 6 / 4 / 7 ns.
- `rng_uniform` multiplies by 2^-53 instead of dividing by 2^53: identical bits,
  since both steps are exact. The internal helper `_f64_2p53` is removed; no
  consumer referenced it.

### Added

- **Known-answer tests.** 39 exact-bit assertions: the unseeded stream, the seed
  finalizer at 0 / ±1 / the i64 extremes, `rng_u64` / `rng_uniform` /
  `rng_normal` / `_rng_ln` vectors, a guard vector (seed 1481, draw 2) that fails
  if `f64_ln` comes back, and the `_rng_state` checkpoint contract. The suite
  goes from 10 to **49 assertions**. The vectors come from
  `scripts/kat_reference.py`, an independent reference written from the
  algorithms. Mutation-checked: restoring `f64_ln`, perturbing the shift triple
  and perturbing a splitmix constant each fail it, on both targets.
- **aarch64 CI leg.** The suite and the fuzz harness run under qemu-user on
  every push, and the job fails rather than skips when the cross-compiler or
  qemu is missing.
- **Fuzz harness** (was a stub): properties over 100,005 seeds — the state is
  never 0, no `rng_u64` output is 0, uniforms lie in [0,1), normals are finite
  with |x| ≤ 12.01, re-seeding replays — plus `_rng_ln` monotonicity and
  powers of two.
- **Benchmarks** (measured a no-op): every entry point, with results in
  [`docs/benchmarks.md`](docs/benchmarks.md).
- [`docs/audit/2026-09-25-audit.md`](docs/audit/2026-09-25-audit.md),
  [`scripts/kat_reference.py`](scripts/kat_reference.py), and the first ADR,
  [`docs/adr/0001-rng-normal-uses-its-own-portable-ln.md`](docs/adr/0001-rng-normal-uses-its-own-portable-ln.md),
  which records the alternatives and their costs.

### Fixed

- **Docs that had gone stale or were never filled in:** the README dependency
  snippet (`tag = "0.1.0"`); `SECURITY.md`'s version and "pre-1.0, not audited";
  `CONTRIBUTING.md`, which said there was no reference oracle and listed
  `f64_ln` among the builtins to use; the getting-started guide and roadmap
  (both still scaffold text); `CLAUDE.md`'s identity and goal placeholders; and
  `docs/api.md`'s determinism note, which now says how it holds, and the
  unseeded state.

### Upstream

- Filed cyrius
  `docs/development/issues/2026-09-25-tyche-aarch64-f64-ln-polyfill-specials-and-accuracy.md`:
  on aarch64, `f64_ln` / `f64_log2` return finite values for 0, ±inf, NaN and
  subnormals, and the ln / exp polyfills miss their stated accuracy (up to
  213 / 2,313 ulp). tyche no longer depends on the fix.

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
