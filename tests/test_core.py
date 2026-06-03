import pytest
import metronos as mt
from metronos.core import parse_unit, DimensionError, UnknownUnitError, OffsetAlgebraError


# --- Parsing ---

def test_parse_simple():
    u = parse_unit('m')
    assert u.L == 1 and u.coef == 1

def test_parse_prefix():
    u = parse_unit('km')
    assert u.L == 1 and u.coef == pytest.approx(1000)

def test_parse_compound_division():
    u = parse_unit('m/s')
    assert u.L == 1 and u.T == -1

def test_parse_power():
    u = parse_unit('m/s^2')
    assert u.L == 1 and u.T == -2

def test_parse_numerator_product():
    u = parse_unit('kg*m/s^2')
    assert u.M == 1 and u.L == 1 and u.T == -2

def test_parse_unknown_raises():
    with pytest.raises(UnknownUnitError):
        parse_unit('xyz')

def test_parse_offset_compound_raises():
    with pytest.raises(OffsetAlgebraError):
        parse_unit('degC*m')


# --- Construction ---

def test_si_unit():
    q = mt.Quantity(1.0, 'm')
    assert q._si_value == pytest.approx(1.0)

def test_prefix_unit():
    q = mt.Quantity(1.0, 'km')
    assert q._si_value == pytest.approx(1000.0)

def test_english_unit():
    q = mt.Quantity(1.0, 'ft')
    assert q._si_value == pytest.approx(0.3048)

def test_offset_celsius():
    q = mt.Quantity(0.0, 'degC')
    assert q._si_value == pytest.approx(273.15)

def test_offset_fahrenheit():
    q = mt.Quantity(32.0, 'degF')
    assert q._si_value == pytest.approx(273.15)

def test_dimensionless():
    q = mt.Quantity(5.0)
    assert q._si_value == pytest.approx(5.0)
    assert q._dims == (0, 0, 0, 0, 0, 0, 0)


# --- .value ---

def test_value_own_unit():
    assert mt.Quantity(3.5, 'ft').value == pytest.approx(3.5)

def test_value_celsius():
    assert mt.Quantity(100.0, 'degC').value == pytest.approx(100.0)

def test_value_after_to():
    assert mt.Quantity(1.0, 'km').to('m').value == pytest.approx(1000.0)


# --- Arithmetic ---

def test_add_same_unit():
    result = mt.Quantity(1.0, 'm') + mt.Quantity(2.0, 'm')
    assert result._si_value == pytest.approx(3.0)

def test_add_mixed_units():
    result = mt.Quantity(1.0, 'km') + mt.Quantity(1.0, 'm')
    assert result._si_value == pytest.approx(1001.0)

def test_add_dimension_mismatch():
    with pytest.raises(DimensionError):
        mt.Quantity(1.0, 'm') + mt.Quantity(1.0, 'kg')

def test_sub():
    result = mt.Quantity(3.0, 'm') - mt.Quantity(1.0, 'm')
    assert result._si_value == pytest.approx(2.0)

def test_sub_dimension_mismatch():
    with pytest.raises(DimensionError):
        mt.Quantity(1.0, 'm') - mt.Quantity(1.0, 's')

def test_mul_quantities():
    result = mt.Quantity(2.0, 'm') * mt.Quantity(3.0, 'm')
    assert result._si_value == pytest.approx(6.0)
    assert result._dims == (2, 0, 0, 0, 0, 0, 0)

def test_mul_scalar():
    assert (mt.Quantity(2.0, 'm') * 3)._si_value == pytest.approx(6.0)

def test_rmul_scalar():
    assert (3 * mt.Quantity(2.0, 'm'))._si_value == pytest.approx(6.0)

def test_div_quantities():
    result = mt.Quantity(6.0, 'm') / mt.Quantity(2.0, 's')
    assert result._si_value == pytest.approx(3.0)
    assert result._dims == (1, 0, -1, 0, 0, 0, 0)

def test_div_scalar():
    assert (mt.Quantity(6.0, 'm') / 2)._si_value == pytest.approx(3.0)

def test_pow():
    result = mt.Quantity(3.0, 'm') ** 2
    assert result._si_value == pytest.approx(9.0)
    assert result._dims == (2, 0, 0, 0, 0, 0, 0)


# --- to() ---

def test_to_length():
    assert mt.Quantity(1.0, 'm').to('ft').value == pytest.approx(1.0 / 0.3048)

def test_to_offset():
    assert mt.Quantity(100.0, 'degC').to('degF').value == pytest.approx(212.0)

def test_to_prefix():
    assert mt.Quantity(1000.0, 'm').to('km').value == pytest.approx(1.0)

def test_to_dimension_mismatch():
    with pytest.raises(DimensionError):
        mt.Quantity(1.0, 'm').to('kg')


# --- __neg__ ---

def test_neg_value():
    q = -mt.Quantity(3.0, 'm')
    assert q._si_value == pytest.approx(-3.0)

def test_neg_preserves_unit():
    q = -mt.Quantity(3.0, 'm')
    assert q.unit_str == 'm'


# --- __abs__ ---

def test_abs_positive():
    assert abs(mt.Quantity(3.0, 'm'))._si_value == pytest.approx(3.0)

def test_abs_negative():
    assert abs(mt.Quantity(-3.0, 'm'))._si_value == pytest.approx(3.0)

def test_abs_preserves_unit():
    assert abs(mt.Quantity(-3.0, 'ft')).unit_str == 'ft'


# --- __float__ ---

def test_float_dimensionless():
    assert float(mt.Quantity(5.0)) == pytest.approx(5.0)

def test_float_dimensioned_raises():
    with pytest.raises(TypeError):
        float(mt.Quantity(3.0, 'm'))


# --- Comparisons ---

def test_eq_same():
    assert mt.Quantity(1.0, 'm') == mt.Quantity(1.0, 'm')

def test_eq_equivalent_units():
    assert mt.Quantity(1.0, 'km') == mt.Quantity(1000.0, 'm')

def test_eq_different_dims_returns_false():
    assert not (mt.Quantity(1.0, 'm') == mt.Quantity(1.0, 'kg'))

def test_lt():
    assert mt.Quantity(1.0, 'm') < mt.Quantity(2.0, 'm')

def test_gt():
    assert mt.Quantity(2.0, 'm') > mt.Quantity(1.0, 'm')

def test_le_equal():
    assert mt.Quantity(1.0, 'm') <= mt.Quantity(1.0, 'm')

def test_ge_equal():
    assert mt.Quantity(2.0, 'm') >= mt.Quantity(1.0, 'm')

def test_ordering_dimension_mismatch():
    with pytest.raises(DimensionError):
        mt.Quantity(1.0, 'm') < mt.Quantity(1.0, 'kg')
