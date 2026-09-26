# tyche — algorithm sources

Multi-source prior art for the PRNG primitives. tyche ports the converged,
well-characterized forms; none of these is novel, which is the point — a
statistical PRNG should be boring and exactly reproducible.

## xorshift64 stream — `rng_u64`

Marsaglia, G. (2003). "Xorshift RNGs." *Journal of Statistical Software*, 8(14).
The `(13, 7, 17)` left/right/left shift triple is one of Marsaglia's published
full-period choices for 64-bit state. Period 2^64 − 1; the all-zero state is the
single fixed point and is excluded by the seeder.

## splitmix64 seed finalizer — `rng_seed`

Steele, G., Lea, D., & Flood, C. (2014). "Fast Splittable Pseudorandom Number
Generators." *OOPSLA 2014*. The finalizer constants
(`0x9E3779B97F4A7C15`, `0xBF58476D1CE4E5B9`, `0x94D049BB133111EB`) decorrelate
small/sequential seeds so the first xorshift outputs aren't near-zero or
near-identical across adjacent seeds.

## Standard normal — `rng_normal`

Marsaglia, G., & Bray, T. A. (1964). "A Convenient Method for Generating Normal
Variables." *SIAM Review*, 6(3). The polar (rejection) method: draw points in
the square `[-1,1)^2`, keep those strictly inside the unit circle, scale by
`sqrt(-2 ln(s) / s)`. Chosen over Box-Muller because it needs no `sin`/`cos`.

### Its logarithm — `_rng_ln` (since 1.1.0)

The polar method needs `ln(s)`. tyche computes it itself instead of calling the
`f64_ln` builtin, because cyrius lowers that builtin differently per target:
x87 `fyl2x` on x86_64, and a Taylor-series polyfill (`lib/math.cyr`) on aarch64
that is up to 213 ulp off. Through 1.0.3 that made `rng_normal` differ across
targets; it was filed upstream as cyrius
`docs/development/issues/2026-09-25-tyche-aarch64-f64-ln-polyfill-specials-and-accuracy.md`.

- **Reduction:** `x = 2^k · m`, `m ∈ [√½, √2]`, so `ln x = k ln 2 + 2 atanh(t)`
  with `t = (m − 1)/(m + 1)`, `|t| ≤ 3 − 2√2`. The atanh series is the classical
  one used by fdlibm's `e_log.c` (Sun Microsystems, 1993).
- **Precision:** double-double arithmetic after Dekker, T. J. (1971). "A
  floating-point technique for extending the available precision." *Numerische
  Mathematik*, 18(3), 224–242: Veltkamp splitting, the exact product
  (`two_prod`) and exact sums (`two_sum`, Knuth's TAOCP vol. 2 §4.2.2). No FMA
  is needed or used.
- **Accuracy:** the value before the last rounding is within ~2^-70 of `ln x`,
  so the result is the correctly rounded `ln x` except when `ln x` lies within
  ~2^-70 of a rounding midpoint. Against Python's `decimal` at 50 digits it was
  correctly rounded on all 1,294,808 test inputs and on 9,999,999 of the
  10,000,000 values of `s` behind a 10M-draw `rng_normal` run. The miss lies
  2^-74.2 from a midpoint, and x87 rounded it the same way.

So `rng_normal` is defined by `_rng_ln`'s exact operations, not by "a correctly
rounded ln". `scripts/kat_reference.py` ports them one for one and reproduces
the stream bit for bit; its `--hard-cases` mode lists the rare draws where a
correctly rounded `ln` would differ.

## Uniform [0,1) — `rng_uniform`

Standard construction: take the high 53 bits of a u64 (the f64 significand width)
and scale by 2^-53, giving a uniform draw on `[0, 1)` with full double precision
and no bias from low-bit weakness. Both steps are exact.

## Boundary note

None of these is cryptographically secure; all are designed for *statistical
quality and reproducibility*, not unpredictability. See README's "Not a CSPRNG"
section — crypto randomness is sigil's domain.
