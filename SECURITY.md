# Security Policy

## Reporting

Report vulnerabilities to **cyriusmaccken@gmail.com**. Include reproduction
steps and the tyche version from `VERSION`. Expect an
initial response within one week. Coordinated disclosure is appreciated — do not
open a public GitHub issue with exploit details.

## tyche is NOT a CSPRNG

This is the security-critical fact about this library. **tyche is a
*statistical* PRNG, not a cryptographic one.** Its xorshift64 stream is
deterministic and trivially predictable: a single output reveals the entire past
and future stream, and the seed can be recovered. tyche exists for
reproducible-by-seed sampling — simulation, ML weight initialization, Monte
Carlo, dropout — where you *want* the same stream from the same seed.

**Do NOT use tyche for keys, nonces, IVs, session tokens, salts, password
material, or provable fairness.** Cryptographic randomness in this ecosystem is
the responsibility of **sigil**, the trust/crypto boundary — use it, never this
library. Treating tyche output as secret or unpredictable is a misuse, not a
vulnerability in tyche; reports of "the stream is predictable" will be closed as
working-as-designed.

## Threat model

tyche is a small, single-process, CPU-only library. It has **no networking**, no
file I/O, no `unsafe`/FFI surface, and no parsing of external formats. Its entire
public API is four functions over a process-global 64-bit state, plus that
state itself:

- `rng_seed(s)` — seed the stream (any `i64` accepted; finalized through
  splitmix64, with the all-zero fixed point bumped to 1).
- `rng_u64()` — next raw 64-bit value.
- `rng_uniform()` — `f64` in `[0,1)`.
- `rng_normal()` — `f64` from `N(0,1)`.
- `_rng_state` — the one internal consumers may read and write, to checkpoint
  and restore the stream (see [`docs/api.md`](docs/api.md)).

The untrusted inputs are the **seed value, any value written into
`_rng_state`, and the call pattern** a caller supplies. None of them hangs,
crashes or corrupts the library:

- The seed accepts any `i64`; the splitmix64 finalizer plus the zero-bump
  guarantees a non-degenerate stream for every seed (including 0).
- `_rng_state` accepts any `i64`. A 0, xorshift's fixed point, steps as state 1
  (since 1.2.2). Through 1.2.1, a zeroed state froze `rng_u64` and
  `rng_uniform` at 0 and made `rng_normal` loop forever. See
  [`docs/audit/2026-11-04-audit.md`](docs/audit/2026-11-04-audit.md).
- All state is fixed-size scalars; there is no allocation, no buffer, no index
  derived from external data, and no recursion. From every state, `rng_normal`'s
  rejection loop accepts a point with probability π/4 per try, and it cannot
  read or write out of bounds.
- f64 work uses only the IEEE-754 basic builtins (`f64_add`, `f64_sub`,
  `f64_mul`, `f64_div`, `f64_sqrt`) on bit patterns. The polar method's
  logarithm is tyche's own `_rng_ln`, which only ever receives `s` in
  `[2^-104, 1)` — strictly inside the unit circle and never 0 — so there is no
  division by zero, no domain error and no non-finite result. The fuzz harness
  (`tests/tyche.fcyr`) checks that every normal is finite and within ±12.01, the
  method's exact bound, across 100,006 seeds and from a zeroed state.

tyche does **not** defend against an attacker with arbitrary code execution in
the host process — they own the global state and the whole address space, which
is out of scope for any in-process library.

## Maturity

tyche is **1.x**, with its API frozen at 1.0.0. Two audit sweeps are recorded.
[`docs/audit/2026-09-25-audit.md`](docs/audit/2026-09-25-audit.md) (1.1.0) found
no security defect; its fixes were to correctness, cross-platform determinism,
tests and documentation.
[`docs/audit/2026-11-04-audit.md`](docs/audit/2026-11-04-audit.md) (1.2.2) found
one availability defect, the zeroed-state hang above. It also hardened the
release supply chain: actions are pinned by commit SHA, and the CI token is
read-only. The threat surface is small by construction (no I/O, no parsing, no
allocation). The not-a-CSPRNG boundary
above is the load-bearing security property and is enforced by documentation
and review, not by code — it cannot be, since predictability is inherent to the
algorithm.
