#!/usr/bin/env python3
"""Reference implementation of the tyche stream, and the source of the
known-answer vectors in tests/tyche.tcyr.

Written from the algorithms, not transcribed from src/rng.cyr's call graph:
  * rng_seed    splitmix64 finalizer (Steele, Lea & Flood 2014); state 0 -> 1
  * rng_u64     xorshift64, shift triple (13, 7, 17) (Marsaglia 2003)
  * rng_uniform (u64 >> 11) * 2^-53
  * rng_normal  Marsaglia polar (Marsaglia & Bray 1964) in IEEE-754 binary64,
                with tyche's logarithm _rng_ln: the double-double evaluation
                ported below operation for operation.

_rng_ln is correctly rounded except where ln(s) lies within about 2^-70 of a
rounding midpoint. The --hard-cases mode lists the draws where it differs from
a correctly rounded ln (Python's decimal at 50 digits); expect about one in two
million. Python floats are IEEE binary64 with round-to-nearest, and every step
below is one IEEE operation, so this reproduces tyche bit for bit. Standard
library only.

    python3 scripts/kat_reference.py                   # print the vectors
    python3 scripts/kat_reference.py --normals SEED N  # N normal bit patterns
    python3 scripts/kat_reference.py --hard-cases SEED N
"""
import math
import struct
import sys
from decimal import Decimal, getcontext
from fractions import Fraction

getcontext().prec = 50
M64 = (1 << 64) - 1
INITIAL_STATE = 88172645463325252          # tyche's documented unseeded state


def bits(d):
    return struct.unpack('<Q', struct.pack('<d', d))[0]


def from_bits(b):
    return struct.unpack('<d', struct.pack('<Q', b & M64))[0]


def ln_cr(x):
    """Correctly rounded natural log of a positive double (Decimal(x) is exact)."""
    return float(Decimal(x).ln())


# ---- _rng_ln, ported operation for operation ---------------------------------

def _dd(fr):
    hi = float(fr)
    return hi, float(fr - Fraction(hi))


_SPLIT = 134217729.0                                   # 2^27 + 1
_LN2_HI, _LN2_LO = 0.6931471805599453, 2.3190468138462996e-17
_C3 = _dd(Fraction(2, 3))
_C5 = _dd(Fraction(2, 5))
_TAIL = [float(Fraction(2, 2 * j + 7)) for j in range(11)]   # 2/7 ... 2/27


def _two_prod(a, b):
    p = a * b
    c = _SPLIT * a
    ah = c - (c - a)
    al = a - ah
    c = _SPLIT * b
    bh = c - (c - b)
    bl = b - bh
    return p, ((ah * bh - p) + ah * bl + al * bh) + al * bl


def _fast_two_sum(a, b):
    s = a + b
    return s, b - (s - a)


def _dd_mul(ah, al, bh, bl):
    p, e = _two_prod(ah, bh)
    return _fast_two_sum(p, e + (ah * bl + al * bh))


def _dd_add(ah, al, bh, bl):
    s = ah + bh
    bb = s - ah
    e = (ah - (s - bb)) + (bh - bb)
    return _fast_two_sum(s, e + (al + bl))


def ln_tyche(x):
    """tyche's _rng_ln for a positive normal double."""
    b = bits(x)
    k = ((b >> 52) & 0x7FF) - 1023
    mb = (b & 0x000FFFFFFFFFFFFF) | 0x3FF0000000000000
    if mb > 0x3FF6A09E667F3BCD:
        mb -= 0x0010000000000000
        k += 1
    m = from_bits(mb)
    fm = m - 1.0
    d_hi = 1.0 + m
    d_lo = m - (d_hi - 1.0)
    t_hi = fm / d_hi
    p, q = _two_prod(t_hi, d_hi)
    t_lo = (((fm - p) - q) - t_hi * d_lo) / d_hi
    tt_hi, tt_lo = _dd_mul(t_hi, t_lo, t_hi, t_lo)
    q = _TAIL[10]
    for c in reversed(_TAIL[:10]):
        q = c + tt_hi * q
    a_hi, a_lo = _dd_mul(tt_hi, tt_lo, q, 0.0)
    a_hi, a_lo = _dd_add(_C5[0], _C5[1], a_hi, a_lo)
    a_hi, a_lo = _dd_mul(tt_hi, tt_lo, a_hi, a_lo)
    a_hi, a_lo = _dd_add(_C3[0], _C3[1], a_hi, a_lo)
    c_hi, c_lo = _dd_mul(t_hi, t_lo, tt_hi, tt_lo)
    c_hi, c_lo = _dd_mul(c_hi, c_lo, a_hi, a_lo)
    l_hi, l_lo = _dd_add(2.0 * t_hi, 2.0 * t_lo, c_hi, c_lo)
    kf = float(k)
    p, e = _two_prod(kf, _LN2_HI)
    s_hi, s_lo = _dd_add(p, e + kf * _LN2_LO, l_hi, l_lo)
    return s_hi + s_lo


# ---- the stream -----------------------------------------------------------

class Tyche:
    def __init__(self, ln=ln_tyche):
        self.state = INITIAL_STATE
        self.ln = ln

    def seed(self, s):
        s = (s + 0x9E3779B97F4A7C15) & M64
        z = s
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
        z ^= z >> 31
        self.state = z if z != 0 else 1

    def u64(self):
        x = self.state
        x ^= (x << 13) & M64
        x ^= x >> 7
        x ^= (x << 17) & M64
        self.state = x
        return x

    def uniform(self):
        return float(self.u64() >> 11) * 2.0 ** -53

    def polar(self):
        """One accepted polar point: (v1, s)."""
        while True:
            v1 = 2.0 * self.uniform() - 1.0
            v2 = 2.0 * self.uniform() - 1.0
            s = v1 * v1 + v2 * v2
            if s < 1.0 and s > 0.0:
                return v1, s

    def normal(self):
        v1, s = self.polar()
        return v1 * math.sqrt((-2.0 * self.ln(s)) / s)


def hx(u):
    return "0x%016X" % (u & M64)


def main():
    if len(sys.argv) == 4 and sys.argv[1] == "--normals":
        t = Tyche()
        t.seed(int(sys.argv[2]) & M64)
        for _ in range(int(sys.argv[3])):
            print("%016x" % bits(t.normal()))
        return
    if len(sys.argv) == 4 and sys.argv[1] == "--hard-cases":
        t = Tyche()
        t.seed(int(sys.argv[2]) & M64)
        for i in range(int(sys.argv[3])):
            v1, s = t.polar()
            a, c = ln_tyche(s), ln_cr(s)
            if a != c:
                print(f"draw {i}: s={s!r} _rng_ln={hx(bits(a))} correctly-rounded={hx(bits(c))}")
        return
    t = Tyche()
    print("unseeded u64:", [hx(t.u64()) for _ in range(3)])
    for sd in (0, 1, 42, -1, -(1 << 63), (1 << 63) - 1):
        t.seed(sd & M64)
        st = t.state
        print(f"seed {sd}: state={hx(st)} u64={[hx(t.u64()) for _ in range(3)]}")
    t.seed(12345)
    print("seed 12345 uniform:", [hx(bits(t.uniform())) for _ in range(3)])
    t.seed(777)
    print("seed 777 normal:", [hx(bits(t.normal())) for _ in range(4)])
    t.seed(1481)
    print("seed 1481 normal[2]:", hx(bits([t.normal() for _ in range(3)][2])))
    for x in (0.5, 0.25, 1.0, 2.0 ** -104, 0.1, 1 - 2.0 ** -53, 1 - 2.0 ** -52,
              1.4142135623730316, 0.7071610849050405):
        a = ln_tyche(x)
        flag = "" if a == ln_cr(x) else "   (differs from correctly rounded)"
        print(f"ln({x!r}) = {hx(bits(a))}{flag}")


if __name__ == "__main__":
    main()
