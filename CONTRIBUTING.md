# Contributing to tyche

## Development

1. Install the Cyrius toolchain at the version pinned in `cyrius.cyml`
   (`[package].cyrius`). The pin is the single source of truth — never hardcode
   a version elsewhere.
2. `cyrius deps` — resolve stdlib deps into `lib/`.
3. `cyrius build src/main.cyr build/tyche` — compile the smoke demo (seeds the
   stream, shows determinism, prints the not-a-CSPRNG reminder).
4. `cyrius test` — run the `[build].test` entry (`src/test.cyr`).
5. `cyrius build tests/tyche.tcyr build/tcyr && ./build/tcyr` — the statistical
   suite (the real correctness gate; see below).
6. `cyrius build tests/tyche.bcyr build/bench && ./build/bench` — benchmarks.
7. `cyrius build tests/tyche.fcyr build/fuzz && ./build/fuzz` — fuzz stub.
8. `cyrius distlib` — regenerate `dist/tyche.cyr` after touching `src/rng.cyr`
   (CI has a drift gate that fails if the bundle lags `src/`).

See [`CLAUDE.md`](CLAUDE.md) for the full development loop and
[`docs/development/sources.md`](docs/development/sources.md) for the algorithm
references (xorshift64, splitmix64, Marsaglia polar).

## Statistical tests are the contract

tyche is a PRNG: there is no reference oracle, so correctness is **statistical
and property-based**, verified in `tests/tyche.tcyr` before a change lands. A
new or modified generator path is incomplete until the suite covers it:

- **Determinism** — the same seed reproduces the exact `rng_u64` stream.
- **Seed sensitivity** — distinct seeds diverge on the first draw.
- **Zero-fixed-point guard** — seed 0 must not freeze the stream (xorshift's
  fixed point is 0; the splitmix64 finalizer + bump-to-1 prevents the all-zero
  stream).
- **Distribution shape** — `rng_uniform` draws all land in `[0,1)` with sample
  mean ≈ 0.5; `rng_normal` has sample mean ≈ 0 and variance ≈ 1 over 200k draws,
  within the documented tolerances.

If you change a shift triple, a finalizer constant, or the uniform/normal
mapping, you have changed the stream — update the suite and call it out as a
**Breaking** change (the stream is reproducible-by-seed, so callers depend on
the exact byte sequence).

## Numeric rules

- Cyrius has no float type — an `f64` is its IEEE-754 bit pattern carried in an
  `i64`. Use the `f64_*` builtins (`f64_add`, `f64_mul`, `f64_div`, `f64_sqrt`,
  `f64_ln`, `f64_lt`, …), never `+`/`*` on float values.
- Build precise constants from integers (`f64_from`, integer ratios); long-digit
  float literals mis-parse.
- Integer multiply wraps mod 2^64 — this is intentional in the splitmix64 seed
  finalizer. The xorshift shifts (`<<`, `>>`) are bitwise on the raw `i64`
  state; `rng_uniform` uses a logical right shift so the 53-bit value stays
  non-negative.

## Process

- One change at a time. Never bundle unrelated changes.
- Run the statistical suite after every change to a generator path; benchmark
  after every perf-touching change.
- Performance claims must include numbers — `before → after` with the bench
  name.
- Breaking changes (including any change to the seeded stream) get a `Breaking`
  section in [`CHANGELOG.md`](CHANGELOG.md) with a migration paragraph.
- Do not commit/push or use `gh` — the maintainer handles git operations.

## License

GPL-3.0-only.
