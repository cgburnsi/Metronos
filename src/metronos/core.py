
class OffsetAlgebraError(ValueError): pass

class DimensionError(ValueError):
    def __init__(self, u_from, u_to, dim_from, dim_to):
        msg = ("Incompatible dimensions: '%s' %s -> '%s' %s. "
               "Units must have identical dimension vectors.") % (
                   u_from, dim_from, u_to, dim_to
               )
        ValueError.__init__(self, msg)
        self.u_from = u_from
        self.u_to = u_to
        self.dim_from = dim_from
        self.dim_to = dim_to

class UnknownUnitError(ValueError):
    def __init__(self, token):
        ValueError.__init__(self, "Unknown unit symbol: '%s'" % token)
        self.token = token


def _assert_linear(u):
    if getattr(u, 'offset', 0) not in (0, 0.0):
        raise OffsetAlgebraError(
            "Algebra with offset unit '%s' is not allowed. "
            "Normalize temperature to K or degR before multiplying/dividing/raising to a power." % u.symbol
        )


class PrefixDefinition:
    def __init__(self, symbol, name, factor):
        self.symbol = symbol
        self.name = name
        self.factor = factor

    def __repr__(self):
        return "Prefix(symbol='%s', name='%s', factor=%s)" % (self.symbol, self.name, self.factor)

    def __eq__(self, other):
        return isinstance(other, PrefixDefinition) and self.factor == other.factor

    def __mul__(self, unit):
        if isinstance(unit, UnitDefinition):
            return UnitDefinition(
                symbol=self.symbol + unit.symbol,
                name=self.name + unit.name,
                L=unit.L, M=unit.M, T=unit.T, I=unit.I, THETA=unit.THETA, N=unit.N, J=unit.J,
                coef=self.factor * unit.coef,
                offset=unit.offset
            )
        raise ValueError("Can only multiply PrefixDefinition with UnitDefinition.")


class UnitDefinition:
    def __init__(self, symbol, name, L=0, M=0, T=0, I=0, THETA=0, N=0, J=0, coef=1, offset=0):
        self.symbol = symbol
        self.name = name
        self.L = L
        self.M = M
        self.T = T
        self.I = I
        self.THETA = THETA
        self.N = N
        self.J = J
        self.coef = coef
        self.offset = offset

    def __repr__(self):
        return "Unit(symbol='%s', name='%s', coef=%s, offset=%s)" % (self.symbol, self.name, self.coef, self.offset)

    def __eq__(self, other):
        return (
            isinstance(other, UnitDefinition) and
            self.L == other.L and
            self.M == other.M and
            self.T == other.T and
            self.I == other.I and
            self.THETA == other.THETA and
            self.N == other.N and
            self.J == other.J and
            self.coef == other.coef and
            self.offset == other.offset
        )

    def __mul__(self, other):
        if isinstance(other, UnitDefinition):
            _assert_linear(self)
            _assert_linear(other)
            return UnitDefinition(
                symbol="%s*%s" % (self.symbol, other.symbol),
                name="%s*%s" % (self.name, other.name),
                L=self.L + other.L,
                M=self.M + other.M,
                T=self.T + other.T,
                I=self.I + other.I,
                THETA=self.THETA + other.THETA,
                N=self.N + other.N,
                J=self.J + other.J,
                coef=self.coef * other.coef,
                offset=0
            )
        raise ValueError("Can only multiply UnitDefinition with UnitDefinition.")

    def __pow__(self, power):
        _assert_linear(self)
        try:
            power = float(power)
        except (TypeError, ValueError):
            raise ValueError("Power must be a number.")
        return UnitDefinition(
            symbol="%s^%s" % (self.symbol, power),
            name="%s^%s" % (self.name, power),
            L=self.L * power,
            M=self.M * power,
            T=self.T * power,
            I=self.I * power,
            THETA=self.THETA * power,
            N=self.N * power,
            J=self.J * power,
            coef=self.coef ** power,
            offset=0
        )

    def __truediv__(self, other):
        if isinstance(other, UnitDefinition):
            _assert_linear(self)
            _assert_linear(other)
            return UnitDefinition(
                symbol="%s/%s" % (self.symbol, other.symbol),
                name="%s/%s" % (self.name, other.name),
                L=self.L - other.L,
                M=self.M - other.M,
                T=self.T - other.T,
                I=self.I - other.I,
                THETA=self.THETA - other.THETA,
                N=self.N - other.N,
                J=self.J - other.J,
                coef=self.coef / other.coef,
                offset=0
            )
        raise ValueError("Can only divide UnitDefinition by UnitDefinition.")

    def __rmul__(self, other):
        return self.__mul__(other)

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            _assert_linear(self)
            return UnitDefinition(
                symbol="%s/%s" % (other, self.symbol),
                name="%s/%s" % (other, self.name),
                L=-self.L,
                M=-self.M,
                T=-self.T,
                I=-self.I,
                THETA=-self.THETA,
                N=-self.N,
                J=-self.J,
                coef=other / self.coef,
                offset=0
            )
        raise ValueError("Can only right-divide UnitDefinition by a numeric value.")

    def is_same_dimension(self, other):
        return (
            self.L == other.L and
            self.M == other.M and
            self.T == other.T and
            self.I == other.I and
            self.THETA == other.THETA and
            self.N == other.N and
            self.J == other.J
        )


PREFIXES = {
    'y':  PrefixDefinition('y',  'yocto', 1E-24),
    'z':  PrefixDefinition('z',  'zepto', 1E-21),
    'a':  PrefixDefinition('a',  'atto',  1E-18),
    'f':  PrefixDefinition('f',  'femto', 1E-15),
    'p':  PrefixDefinition('p',  'pico',  1E-12),
    'n':  PrefixDefinition('n',  'nano',  1E-09),
    'µ':  PrefixDefinition('µ',  'micro', 1E-06),
    'u':  PrefixDefinition('u',  'micro', 1E-06),
    'm':  PrefixDefinition('m',  'milli', 1E-03),
    'c':  PrefixDefinition('c',  'centi', 1E-02),
    'd':  PrefixDefinition('d',  'deci',  1E-01),
    '':   PrefixDefinition('',   '',      1E0),
    'da': PrefixDefinition('da', 'deca',  1E+01),
    'h':  PrefixDefinition('h',  'hecto', 1E+02),
    'k':  PrefixDefinition('k',  'kilo',  1E+03),
    'M':  PrefixDefinition('M',  'mega',  1E+06),
    'G':  PrefixDefinition('G',  'giga',  1E+09),
    'T':  PrefixDefinition('T',  'tera',  1E+12),
    'P':  PrefixDefinition('P',  'peta',  1E+15),
    'E':  PrefixDefinition('E',  'exa',   1E+18),
    'Z':  PrefixDefinition('Z',  'zetta', 1E+21),
    'Y':  PrefixDefinition('Y',  'yotta', 1E+24),
}

UNITS = {
    # Base SI units
    'm':   UnitDefinition('m',   'meter',   L=1),
    'g':   UnitDefinition('g',   'gram',    M=1, coef=1E-3),
    's':   UnitDefinition('s',   'second',  T=1),
    'A':   UnitDefinition('A',   'ampere',  I=1),
    'K':   UnitDefinition('K',   'kelvin',  THETA=1),
    'mol': UnitDefinition('mol', 'mole',    N=1),
    'cd':  UnitDefinition('cd',  'candela', J=1),

    # Derived SI units
    'Hz':  UnitDefinition('Hz',  'hertz', T=-1),
    'N':   UnitDefinition('N',   'newton', M=1, L=1, T=-2),
    'Pa':  UnitDefinition('Pa',  'pascal', M=1, L=-1, T=-2),
    'J':   UnitDefinition('J',   'joule', M=1, L=2, T=-2),
    'W':   UnitDefinition('W',   'watt', M=1, L=2, T=-3),
    'C':   UnitDefinition('C',   'coulomb', T=1, I=1),
    'V':   UnitDefinition('V',   'volt', M=1, L=2, T=-3, I=-1),
    'Ω':   UnitDefinition('Ω',   'ohm', M=1, L=2, T=-3, I=-2),
    'S':   UnitDefinition('S',   'siemens', M=-1, L=-2, T=3, I=2),
    'F':   UnitDefinition('F',   'farad', M=-1, L=-2, T=4, I=2),
    'T':   UnitDefinition('T',   'tesla', M=1, T=-2, I=-1),
    'Wb':  UnitDefinition('Wb',  'weber', M=1, L=2, T=-2, I=-1),
    'H':   UnitDefinition('H',   'henry', M=1, L=2, T=-2, I=-2),
    '°C':  UnitDefinition('°C',  'celsius', THETA=1, offset=273.15),
    'degC':  UnitDefinition('°C',  'celsius', THETA=1, offset=273.15),
    'rad': UnitDefinition('rad', 'radian'),
    'sr':  UnitDefinition('sr',  'steradian'),
    'lm':  UnitDefinition('lm',  'lumen', J=1),
    'lx':  UnitDefinition('lx',  'lux', L=-2, J=1),
    'Bq':  UnitDefinition('Bq',  'becquerel', T=-1),
    'Gy':  UnitDefinition('Gy',  'gray', L=2, T=-2),
    'Sv':  UnitDefinition('Sv',  'sievert', L=2, T=-2),
    'kat': UnitDefinition('kat', 'katal', T=-1, N=1),
    'L':   UnitDefinition('L',   'liter', L=3, coef=1e-3),
    'P':   UnitDefinition('P',   'poise', M=1, L=-1, T=-1, coef=1e-1),

    # Customary US units
    '°F':   UnitDefinition('°F',  'fahrenheit', THETA=1, offset=459.67, coef=5/9),
    '°R':   UnitDefinition('°R',  'rankine',    THETA=1, coef=5/9),
    'degF': UnitDefinition('°F',  'fahrenheit', THETA=1, offset=459.67, coef=5/9),
    'degR': UnitDefinition('°R',  'rankine',    THETA=1, coef=5/9),
    'gal':  UnitDefinition('gal', 'gallon',  L=3, coef=0.00378541),
    'psi':  UnitDefinition('psi', 'psi',     M=1, L=-1, T=-2, coef=6894.76),
    'psia': UnitDefinition('psi', 'psi',     M=1, L=-1, T=-2, coef=6894.76),
    'lb':   UnitDefinition('lb',  'pound',   M=1, coef=0.453592),
    'lbf':  UnitDefinition('lbf', 'lbf',     M=1, L=1, T=-2, coef=4.44822),
    'thou': UnitDefinition('th',  'thou',    L=1, coef=2.54E-5),
    'inch': UnitDefinition('in',  'inch',    L=1, coef=2.54E-2),
    'in':   UnitDefinition('in',  'inch',    L=1, coef=2.54E-2),
    'ft':   UnitDefinition('ft',  'foot',    L=1, coef=3.048E-1),
    'yard': UnitDefinition('yd',  'yard',    L=1, coef=9.144E-1),
    'chain':   UnitDefinition('ch',  'chain',   L=1, coef=20.1168),
    'furlong': UnitDefinition('fur', 'furlong', L=1, coef=201.168),
    'mile':    UnitDefinition('ml',  'mile',    L=1, coef=1609.344),
    'league':  UnitDefinition('lea', 'league',  L=1, coef=4828.032),
    'BTU':     UnitDefinition('BTU', 'btu',     M=1, L=2, T=-2, coef=1055.06),

    # Miscellaneous
    'Torr': UnitDefinition('Torr', 'torr',   M=1, L=-1, T=-2, coef=133.322),
    'bar':  UnitDefinition('bar',  'bar',    M=1, L=-1, T=-2, coef=1E5),
    'min':  UnitDefinition('min',  'minute', T=1, coef=60),
    'h':    UnitDefinition('h',    'hour',   T=1, coef=3600),
}


_SI_BASE = ['m', 'kg', 's', 'A', 'K', 'mol', 'cd']

def _dims_to_si_str(dims):
    pos = []
    neg = []
    for i, exp in enumerate(dims):
        if exp == 0:
            continue
        sym = _SI_BASE[i]
        label = sym if abs(exp) == 1 else '%s^%g' % (sym, abs(exp))
        (pos if exp > 0 else neg).append(label)
    if not pos and not neg:
        return 'dimensionless'
    result = '*'.join(pos) if pos else '1'
    if neg:
        result += '/' + '*'.join(neg)
    return result


def parse_unit(unit_str):
    parts = [p.strip() for p in unit_str.split('/')]
    numerator, denominators = parts[0], parts[1:]
    parsed = _parse_unit_group(numerator)
    for denom in denominators:
        for u in _parse_unit_group(denom):
            parsed.append(u ** -1)
    result = parsed[0]
    for u in parsed[1:]:
        result = result * u
    return result

def _parse_unit_group(units_str):
    return [_parse_unit_token(u) for u in units_str.split('*') if u.strip()]

def _parse_unit_token(unit):
    unit = unit.strip()
    if '^' in unit:
        base, power = unit.split('^')
        return _resolve_unit(base.strip()) ** float(power)
    return _resolve_unit(unit)

def _resolve_unit(unit_s):
    if unit_s in UNITS:
        return UNITS[unit_s]
    for prefix in sorted(PREFIXES, key=len, reverse=True):
        if prefix and unit_s.startswith(prefix):
            base = unit_s[len(prefix):]
            if base in UNITS:
                return PREFIXES[prefix] * UNITS[base]
    raise UnknownUnitError(unit_s)


class Quantity:
    def __init__(self, value, unit=''):
        self.unit_str = unit
        if unit:
            u = parse_unit(unit)
            self._unit_def = u
            self._si_value = (value + u.offset) * u.coef
            self._dims = (u.L, u.M, u.T, u.I, u.THETA, u.N, u.J)
        else:
            self._unit_def = None
            self._si_value = float(value)
            self._dims = (0, 0, 0, 0, 0, 0, 0)

    @classmethod
    def _from_si(cls, si_value, dims, unit_str='', unit_def=None):
        q = cls.__new__(cls)
        q._si_value = si_value
        q._dims = dims
        q.unit_str = unit_str
        q._unit_def = unit_def
        return q

    def __repr__(self):
        if self.unit_str and self._unit_def:
            display = self._si_value / self._unit_def.coef - self._unit_def.offset
            return 'Quantity(%s [%s])' % (display, self.unit_str)
        return 'Quantity(%s [%s])' % (self._si_value, _dims_to_si_str(self._dims))

    def __add__(self, other):
        if self._dims != other._dims:
            raise DimensionError(self.unit_str, other.unit_str, self._dims, other._dims)
        unit_str, unit_def = (self.unit_str, self._unit_def) if self.unit_str == other.unit_str else ('', None)
        return Quantity._from_si(self._si_value + other._si_value, self._dims, unit_str, unit_def)

    def __sub__(self, other):
        if self._dims != other._dims:
            raise DimensionError(self.unit_str, other.unit_str, self._dims, other._dims)
        unit_str, unit_def = (self.unit_str, self._unit_def) if self.unit_str == other.unit_str else ('', None)
        return Quantity._from_si(self._si_value - other._si_value, self._dims, unit_str, unit_def)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Quantity._from_si(self._si_value * other, self._dims)
        dims = tuple(a + b for a, b in zip(self._dims, other._dims))
        return Quantity._from_si(self._si_value * other._si_value, dims)

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return Quantity._from_si(self._si_value * other, self._dims)
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Quantity._from_si(self._si_value / other, self._dims)
        dims = tuple(a - b for a, b in zip(self._dims, other._dims))
        return Quantity._from_si(self._si_value / other._si_value, dims)

    def __rtruediv__(self, other):
        if isinstance(other, (int, float)):
            dims = tuple(-d for d in self._dims)
            return Quantity._from_si(other / self._si_value, dims)
        return NotImplemented

    def __pow__(self, power):
        dims = tuple(d * power for d in self._dims)
        return Quantity._from_si(self._si_value ** power, dims)

    def __neg__(self):
        return Quantity._from_si(-self._si_value, self._dims, self.unit_str, self._unit_def)

    def __abs__(self):
        return Quantity._from_si(abs(self._si_value), self._dims, self.unit_str, self._unit_def)

    def __float__(self):
        if any(self._dims):
            raise TypeError("Cannot convert a dimensioned Quantity to float; use .value or .to() first.")
        return float(self._si_value)

    def __eq__(self, other):
        if not isinstance(other, Quantity):
            return NotImplemented
        if self._dims != other._dims:
            return False
        return self._si_value == other._si_value

    def __hash__(self):
        return hash((self._si_value, self._dims))

    def __lt__(self, other):
        if self._dims != other._dims:
            raise DimensionError(self.unit_str, other.unit_str, self._dims, other._dims)
        return self._si_value < other._si_value

    def __le__(self, other):
        if self._dims != other._dims:
            raise DimensionError(self.unit_str, other.unit_str, self._dims, other._dims)
        return self._si_value <= other._si_value

    def __gt__(self, other):
        if self._dims != other._dims:
            raise DimensionError(self.unit_str, other.unit_str, self._dims, other._dims)
        return self._si_value > other._si_value

    def __ge__(self, other):
        if self._dims != other._dims:
            raise DimensionError(self.unit_str, other.unit_str, self._dims, other._dims)
        return self._si_value >= other._si_value

    @property
    def value(self):
        if self._unit_def:
            return self._si_value / self._unit_def.coef - self._unit_def.offset
        return self._si_value

    def to(self, unit_str):
        u = parse_unit(unit_str)
        target_dims = (u.L, u.M, u.T, u.I, u.THETA, u.N, u.J)
        if self._dims != target_dims:
            raise DimensionError(self.unit_str, unit_str, self._dims, target_dims)
        return Quantity._from_si(self._si_value, self._dims, unit_str, u)
