# Metronos

**Metronos** (from the Ancient Greek *μέτρον* /metron/, meaning "measure" or "that by which anything is measured.")

A lightweight Python library for physical quantities with units. No heavy dependencies, no mandatory annotations, no user-facing registries — just quantities that know what they are and refuse to let you mix them up.

---

## Installation

```bash
pip install git+https://github.com/cgburnsi/Metronos.git
```

Or clone and install locally:

```bash
git clone https://github.com/cgburnsi/Metronos.git
cd Metronos
pip install -e .
```

---

## Quick start

```python
import metronos as mt

d = mt.Quantity(6.2, 'ft')
v = mt.Quantity(60, 'mile/s')
a = mt.Quantity(9.81, 'm/s^2')
```

---

## Features

### Unit conversion

```python
mt.Quantity(6.2, 'ft').to('m')          # Quantity(1.88976 [m])
mt.Quantity(60, 'mile/s').to('km/s')    # Quantity(96.56064 [km/s])
mt.Quantity(9.81, 'm/s^2').to('ft/s^2') # Quantity(32.185 [ft/s^2])
```

### Arithmetic

Units combine automatically. Mixed-unit arithmetic works as long as the dimensions are compatible.

```python
mt.Quantity(100, 'm') + mt.Quantity(0.5, 'km')   # Quantity(600.0 [m])

mass = mt.Quantity(70, 'kg')
accel = mt.Quantity(9.81, 'm/s^2')
force = mass * accel                              # Quantity(686.7 [m*kg/s^2])

KE = 0.5 * mass * mt.Quantity(10, 'm/s') ** 2   # Quantity(3500.0 [m^2*kg/s^2])
```

### Temperature

Offset units (°C, °F, °R) are fully supported.

```python
mt.Quantity(100, 'degC').to('degF')   # Quantity(212.0 [degF])
mt.Quantity(32, 'degF').to('K')       # Quantity(273.15 [K])
```

### Extracting values

```python
speed = mt.Quantity(25, 'm/s')
speed.to('km/s').value    # 0.025  (float, in the requested unit)

ratio = mt.Quantity(3.0) / mt.Quantity(1.5)
float(ratio)              # 2.0  (dimensionless quantities only)
```

### Dimension safety

Metronos raises a `DimensionError` if you try to add or compare incompatible quantities.

```python
mt.Quantity(1, 'm') + mt.Quantity(1, 'kg')   # DimensionError
mt.Quantity(1, 'm').to('s')                  # DimensionError
mt.Quantity(1, 'm') < mt.Quantity(1, 'kg')   # DimensionError
```

### Comparisons

```python
mt.Quantity(100, 'm') == mt.Quantity(0.1, 'km')   # True
mt.Quantity(100, 'm') < mt.Quantity(1, 'mile')    # True
```

---

## Supported units

### SI base units

| Symbol | Quantity |
|--------|----------|
| `m` | length |
| `g` | mass (base unit is kg internally) |
| `s` | time |
| `A` | electric current |
| `K` | temperature |
| `mol` | amount of substance |
| `cd` | luminous intensity |

All SI base and derived units support the full prefix set (`n`, `µ`, `m`, `k`, `M`, `G`, etc.).

### Derived SI units

`Hz`, `N`, `Pa`, `J`, `W`, `C`, `V`, `Ω`, `S`, `F`, `T`, `Wb`, `H`, `lm`, `lx`, `Bq`, `Gy`, `Sv`, `kat`, `L`

### Customary US units

`ft`, `in`, `inch`, `mile`, `yard`, `lb`, `lbf`, `psi`, `psia`, `gal`, `BTU`, `degF`, `degR`

### Other

`bar`, `Torr`, `min`, `h`, `degC`

---

## Philosophy

- **Lean:** No dependencies beyond the Python standard library.
- **Pythonic:** Clean, simple API with no mandatory annotations or boilerplate.
- **Intuitive:** It handles the dimensional math so you can focus on the physics.
