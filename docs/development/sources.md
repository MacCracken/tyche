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

## Uniform [0,1) — `rng_uniform`

Standard construction: take the high 53 bits of a u64 (the f64 significand width)
and divide by 2^53, giving a uniform draw on `[0, 1)` with full double precision
and no bias from low-bit weakness.

## Boundary note

None of these is cryptographically secure; all are designed for *statistical
quality and reproducibility*, not unpredictability. See README's "Not a CSPRNG"
section — crypto randomness is sigil's domain.
