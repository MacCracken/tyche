# Getting started with tyche

## Build and test

```sh
cyrius deps                              # resolve dependencies
cyrius build src/main.cyr build/tyche    # compile the smoke demo
cyrius tests                             # known-answer + statistical suite
cyrius tests --aarch64                   # the same suite under qemu-aarch64
CYRIUS_DCE=1 cyrius bench tests/tyche.bcyr
cyrius distlib                           # regenerate dist/tyche.cyr
```

`cyrius tests --aarch64` needs `qemu-aarch64` (Debian/Ubuntu: `qemu-user`). CI
runs both architectures; a change that passes only on x86_64 is not done.

## Layout

- `src/rng.cyr` — the library: `rng_seed` / `rng_u64` / `rng_uniform` /
  `rng_normal`, the `_rng_state` stream state, and the internal `_rng_ln`. This
  is the only file bundled into `dist/tyche.cyr`.
- `src/main.cyr` — smoke demo (`[build].entry`); not part of the bundle.
- `src/test.cyr` — the `[build].test` entry, a no-op; the suite is below.
- `tests/tyche.tcyr` — known-answer vectors plus statistical checks.
- `tests/tyche.bcyr` — benchmarks for every entry point ([`../benchmarks.md`](../benchmarks.md)).
- `tests/tyche.fcyr` — property fuzzing over 100k seeds.
- `scripts/kat_reference.py` — independent reference implementation; the
  source of the known-answer vectors.
- `dist/tyche.cyr` — what consumers include, as `lib/tyche.cyr`.

## Changing the library

1. Edit `src/rng.cyr`. Keep every f64 operation on a stream path to the
   correctly rounded basics (`f64_add` / `f64_sub` / `f64_mul` / `f64_div` /
   `f64_sqrt`): see *Numeric rules* in [`../../CONTRIBUTING.md`](../../CONTRIBUTING.md).
2. Run `cyrius tests` and `cyrius tests --aarch64`. If a known-answer vector
   fails, you changed the stream: that is a **Breaking** change, and the new
   vectors come from `scripts/kat_reference.py`, never from tyche's own output.
3. Benchmark, and update [`../benchmarks.md`](../benchmarks.md) if a number moved.
4. `cyrius distlib` (CI fails if `dist/tyche.cyr` lags `src/`).
5. Bump `VERSION` and add a CHANGELOG entry before tagging.

See [`../adr/template.md`](../adr/template.md) when a non-trivial design choice deserves an ADR.
