# tyche

**τύχη** — the Greek deity of fortune and chance, fronting a stream that is, in
truth, perfectly reproducible. A sovereign **deterministic statistical PRNG** for
[AGNOS](https://github.com/MacCracken/agnosticos), written in
[Cyrius](https://github.com/MacCracken/cyrius). Zero external dependencies; f64
work rides on compiler builtins (IEEE-754 bit patterns in `i64`).

> ## ⚠ Not a CSPRNG
>
> tyche is for **reproducible-by-seed sampling** — simulation, ML weight
> initialization, Monte Carlo, dropout — anywhere you want the *same* stream
> from the *same* seed. It is **not cryptographically secure**: xorshift64 is
> trivially predictable (one output reveals the entire past and future stream).
>
> **Do NOT use tyche for keys, nonces, session tokens, salts, password
> material, or provable fairness.** Those need a CSPRNG — use **sigil**, the
> ecosystem's trust/crypto boundary, never this library.

## API

| Function | Returns | Notes |
|----------|---------|-------|
| `rng_seed(s)` | — | Seed the stream. Scrambled through a splitmix64 finalizer; a seed finalizing to 0 is bumped to 1 (xorshift's fixed point). |
| `rng_u64()` | `i64` | Next raw 64-bit value from the xorshift64 stream. |
| `rng_uniform()` | f64 in [0,1) | Top 53 bits / 2^53. |
| `rng_normal()` | f64 ~ N(0,1) | Standard normal via the Marsaglia polar method. |

The stream is a single process-global state. The single-threaded sovereign
execution model relies on this; the coming multi-threading / SMP arc will
introduce per-stream handles so reproducibility survives across threads.

## Use as a dependency

```toml
[deps.tyche]
git = "https://github.com/MacCracken/tyche"
tag = "0.1.0"
modules = ["dist/tyche.cyr"]
```

Then `cyrius deps` and `include "lib/tyche.cyr"`. The consumer's `[deps] stdlib`
list supplies the builtins the bundle leaves unresolved.

## Build

```sh
cyrius deps                              # resolve stdlib deps
cyrius build src/main.cyr build/tyche    # compile the smoke demo
cyrius tests                             # statistical test suite (tests/*.tcyr)
cyrius distlib                           # regenerate dist/tyche.cyr
```

## Algorithms

- **xorshift64** — Marsaglia, G. (2003), "Xorshift RNGs", *J. Stat. Soft.* 8(14); the (13, 7, 17) shift triple.
- **splitmix64** seed finalizer — Steele, Lea & Flood (2014), "Fast Splittable PRNGs", *OOPSLA 2014*.
- **Marsaglia polar** normal — Marsaglia & Bray (1964), *SIAM Review* 6(3); chosen over Box-Muller (no sin/cos).

Extracted from [attn11](https://github.com/MacCracken/attn11)'s tensor layer at
its v1 freeze, where the same stream seeds reproducible training runs.

## License

GPL-3.0-only
