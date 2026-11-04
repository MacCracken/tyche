# tyche — Benchmarks

`tests/tyche.bcyr`, run with `CYRIUS_DCE=1 cyrius bench tests/tyche.bcyr`. Each
row is a batch of 1,000,000 calls; `lib/bench.cyr` measures its clock-read cost
and subtracts it. Numbers are the median of three runs.

**Host:** AMD Ryzen 7 5800H, Linux 7.2.6 (x86_64), cyrius 6.6.6.

| entry point | 1.0.3 | 1.1.0 | note |
|---|---:|---:|---|
| `rng_seed` | 6 ns | 6 ns | |
| `rng_u64` | 4 ns | 4 ns | |
| `rng_uniform` | 7 ns | 7 ns | now `m · 2^-53` instead of `m / 2^53`: identical bits, no measurable change |
| `rng_normal` | 92 ns | 347 ns | ×3.8, all of it `_rng_ln` |
| `_rng_ln` | — | 283 ns | internal; new in 1.1.0 |

**Re-measured at 1.1.1** (2026-11-03, same host on Linux 7.2.11): cyrius 6.6.6
and 6.6.20 give identical medians, 6 / 4 / 7 / 358 / 292 ns. The toolchain did
not move the numbers. `rng_normal` and `_rng_ln` now read about 3% above the
table on both toolchains, so the difference comes from the host.

**Re-measured at 1.2.0** (2026-11-04, same host): cyrius 6.6.20 gives 6 / 4 /
7 / 356 / 290 ns and 6.7.9 gives 6 / 4 / 7 / 357 / 291 ns, medians of three
runs each. That 1 ns is within run-to-run noise.

**Re-measured at 1.2.1** (2026-11-04, same host, a later session): cyrius 6.7.9
gives 6 / 4 / 7 / 345 / 281 ns and 6.7.18 gives 6 / 4 / 7 / 346 / 282 ns,
medians of three runs each. The toolchain again moves nothing. The whole
session ran about 10 ns faster than the 1.2.0 runs, which is host variance
between sessions: compare toolchains only within one session.

## 1.2.2 — the P(-1) sweep

Recorded with `./scripts/bench-history.sh` (rows in
[`../bench-history.csv`](../bench-history.csv)) before and after, in one
session on the same host and cyrius 6.7.18, median of three runs. The bits are
identical: same golden dump, and 200,000 normals checked against the reference.

| entry point | 1.2.1 | 1.2.2 | what moved it |
|---|---:|---:|---|
| `rng_seed` | 6 ns | 6 ns | |
| `rng_u64` | 4 ns | 4 ns | +0.3 ns at ps resolution (≈3.96 → 4.27): the state-0 guard. A branch-free `x \| (x == 0)` measured slower (4.49 ns). |
| `rng_uniform` | 7 ns | 5 ns | `#inline`: 5.74 → 4.74 ns measured with and without it on the same tree. The rest moved without any change to `rng_uniform`, which points to code layout. |
| `rng_normal` | 345 ns | 331 ns | −4.1%: each coordinate comes straight from `rng_u64()` as `m·2^-52 − 1`, saving a call level and a multiply. |
| `_rng_ln` | 281 ns | 282 ns | unchanged (noise) |

`_rng_ln` is now 85% of `rng_normal`. cyrius compiles each f64 builtin to
about 11 instructions of stack-machine code, so its ~220 operations cost
≈1.3 ns each. A rewrite of the same operations cannot move that much; see
[`audit/2026-11-04-audit.md`](audit/2026-11-04-audit.md).

## Why `rng_normal` got slower

Through 1.0.3 its logarithm was one x87 instruction on x86_64 (`f64_ln` →
`fyl2x`), which is also what made the stream differ on aarch64. 1.1.0 computes a
near-correctly-rounded `ln` from IEEE basic operations in double-double arithmetic:
about 220 f64 operations, at roughly 1.3 ns each under cyrius's code generation.
Inlining the double-double helpers (one call each, formerly) saved only 3%
(`_rng_ln` 293 → 283 ns), so the cost is the operation count, not call overhead.

Options measured or costed while choosing, for the next time speed matters:

- **A cheaper, < 1 ulp logarithm** (fdlibm's `e_log.c`, ~40 operations) would
  bring `rng_normal` close to its 1.0.3 cost. But a < 1 ulp result is not always
  the correctly rounded one: fdlibm's `log` differs from it on 7.3% of inputs
  from `rng_normal`'s range (14,628 of 200,000, measured). About half of `ln`
  differences reach the output, so roughly 3–4% of x86_64 draws would have moved
  instead of 0.011%. Rejected for 1.1.0 to keep the stream as stable as
  possible.
- **A 129-entry table reduction** (`r = m · (1/c_j) − 1`, exact via `two_prod`)
  would stay about as accurate with roughly a third of the operations, at the
  cost of ~400 lines of constants. As a different algorithm it would still
  disagree with `_rng_ln` on rare hard cases, so it too would be a stream
  change. Not done; see the roadmap.
- **A two-phase (Ziv) evaluation** does not pay here: a fast first pass accurate
  to ~0.2 ulp would fall through to the slow path on ~40% of calls.

## Consumers

Each consumer's own `cyrius tests`, with its pinned tyche (1.0.1) and then with
1.1.0, under its pinned cyrius (6.6.2). Same results either way; see
[`audit/2026-09-25-audit.md`](audit/2026-09-25-audit.md) for the table.
