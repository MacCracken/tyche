# Security Policy

## Reporting

Report vulnerabilities to **cyriusmaccken@gmail.com**. Include reproduction
steps and the tyche version from `VERSION` (currently **0.1.1**). Expect an
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
public API is four functions over a process-global 64-bit state:

- `rng_seed(s)` — seed the stream (any `i64` accepted; finalized through
  splitmix64, with the all-zero fixed point bumped to 1).
- `rng_u64()` — next raw 64-bit value.
- `rng_uniform()` — `f64` in `[0,1)`.
- `rng_normal()` — `f64` from `N(0,1)`.

The only untrusted input is the **seed value and the call pattern** a caller
supplies. There is no input that crashes or corrupts the library:

- The seed accepts any `i64`; the splitmix64 finalizer plus the zero-bump
  guarantees a non-degenerate stream for every seed (including 0).
- All state is fixed-size scalars; there is no allocation, no buffer, no index
  derived from external data, and no recursion (`rng_normal`'s rejection loop is
  bounded in expectation and cannot read or write out of bounds).
- f64 work is done with the compiler's `f64_*` builtins on IEEE-754 bit
  patterns; there is no division by zero or domain error in the mapping paths
  (the polar method only takes `ln(s)`/`sqrt` for `s` strictly inside the unit
  circle).

tyche does **not** defend against an attacker with arbitrary code execution in
the host process — they own the global state and the whole address space, which
is out of scope for any in-process library.

## Maturity

tyche is **pre-1.0 (0.1.1)** and has **not** had a formal security audit. The
threat surface above is small by construction (no I/O, no parsing, no
allocation), so the assessment is structural rather than the result of a
dedicated review. A formal audit (`docs/audit/YYYY-MM-DD-audit.md`) is a v1.0
gate per [`docs/development/roadmap.md`](docs/development/roadmap.md). The
not-a-CSPRNG boundary above is the load-bearing security property and is
enforced by documentation and review, not by code — it cannot be, since
predictability is inherent to the algorithm.
