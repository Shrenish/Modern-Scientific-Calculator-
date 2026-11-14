"""
Converters & Constants — Scientific Physical Constants & Unit Converter
========================================================================
Comprehensive physical constants database and accurate unit conversion engine.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class ConstantItem:
    symbol: str
    name: str
    value: float
    unit: str
    category: str
    description: str


# Standard CODATA recommended physical and mathematical constants
PHYSICAL_CONSTANTS: list[ConstantItem] = [
    # Universal
    ConstantItem("c", "Speed of Light in Vacuum", 299792458.0, "m/s", "Universal", "Exact speed of electromagnetic radiation in vacuum"),
    ConstantItem("G", "Newtonian Constant of Gravitation", 6.67430e-11, "m³/(kg·s²)", "Universal", "Gravitational coupling constant"),
    ConstantItem("h", "Planck Constant", 6.62607015e-34, "J·s", "Quantum", "Quantum of action"),
    ConstantItem("hbar", "Reduced Planck Constant", 1.054571817e-34, "J·s", "Quantum", "h / (2*pi)"),
    ConstantItem("e_charge", "Elementary Charge", 1.602176634e-19, "C", "Electromagnetic", "Electric charge carried by a single proton"),
    ConstantItem("eps0", "Vacuum Electric Permittivity", 8.8541878128e-12, "F/m", "Electromagnetic", "Permittivity of free space"),
    ConstantItem("mu0", "Vacuum Magnetic Permeability", 1.25663706212e-6, "N/A²", "Electromagnetic", "Permeability of free space"),
    
    # Atomic & Physicochemical
    ConstantItem("N_A", "Avogadro Constant", 6.02214076e23, "mol⁻¹", "Physicochemical", "Number of constituent particles in one mole"),
    ConstantItem("k_B", "Boltzmann Constant", 1.380649e-23, "J/K", "Thermodynamics", "Relates thermal energy to temperature"),
    ConstantItem("R", "Universal Molar Gas Constant", 8.314462618, "J/(mol·K)", "Thermodynamics", "N_A * k_B"),
    ConstantItem("sigma_SB", "Stefan-Boltzmann Constant", 5.670374419e-8, "W/(m²·K⁴)", "Thermodynamics", "Black-body radiation constant"),
    ConstantItem("m_e", "Electron Mass", 9.1093837015e-31, "kg", "Atomic", "Rest mass of an electron"),
    ConstantItem("m_p", "Proton Mass", 1.67262192369e-27, "kg", "Atomic", "Rest mass of a proton"),
    ConstantItem("m_n", "Neutron Mass", 1.67492749804e-27, "kg", "Atomic", "Rest mass of a neutron"),
    ConstantItem("u", "Atomic Mass Unit", 1.66053906660e-27, "kg", "Atomic", "Unified atomic mass unit (Dalton)"),
    ConstantItem("alpha", "Fine-Structure Constant", 7.2973525693e-3, "", "Quantum", "Coupling constant for electromagnetic interaction (1/137.036)"),
    ConstantItem("R_inf", "Rydberg Constant", 10973731.568160, "m⁻¹", "Atomic", "Limiting value of atomic spectra wavelengths"),
    
    # Planetary & Terrestrial
    ConstantItem("g0", "Standard Gravity", 9.80665, "m/s²", "Planetary", "Nominal Earth gravitational acceleration"),
    ConstantItem("M_earth", "Earth Mass", 5.9722e24, "kg", "Planetary", "Mass of planet Earth"),
    ConstantItem("R_earth", "Earth Mean Radius", 6.371e6, "m", "Planetary", "Mean volumetric radius of Earth"),
    ConstantItem("M_sun", "Solar Mass", 1.98847e30, "kg", "Planetary", "Mass of the Sun"),
    ConstantItem("AU", "Astronomical Unit", 1.495978707e11, "m", "Planetary", "Average Earth-Sun distance"),
    ConstantItem("ly", "Light-Year", 9.4607304725808e15, "m", "Planetary", "Distance light travels in vacuum in 1 Julian year"),
    ConstantItem("pc", "Parsec", 3.08567758149137e16, "m", "Planetary", "Parallax of one arcsecond"),
]


class UnitConverter:
    """Multi-category unit conversion system."""

    # Base factors relative to reference unit per category
    CATEGORIES: dict[str, dict[str, Any]] = {
        "Length": {
            "reference": "Meter (m)",
            "units": {
                "Meter (m)": 1.0,
                "Kilometer (km)": 1000.0,
                "Centimeter (cm)": 0.01,
                "Millimeter (mm)": 0.001,
                "Micrometer (µm)": 1e-6,
                "Nanometer (nm)": 1e-9,
                "Mile (mi)": 1609.344,
                "Yard (yd)": 0.9144,
                "Foot (ft)": 0.3048,
                "Inch (in)": 0.0254,
                "Nautical Mile (nmi)": 1852.0,
                "Light-Year (ly)": 9.4607304725808e15,
            }
        },
        "Mass": {
            "reference": "Kilogram (kg)",
            "units": {
                "Kilogram (kg)": 1.0,
                "Gram (g)": 0.001,
                "Milligram (mg)": 1e-6,
                "Metric Ton (t)": 1000.0,
                "Pound (lb)": 0.45359237,
                "Ounce (oz)": 0.028349523125,
                "Stone (st)": 6.35029318,
                "Short Ton (US)": 907.18474,
                "Atomic Mass Unit (u)": 1.6605390666e-27,
            }
        },
        "Temperature": {
            # Handled via custom functions
            "reference": "Celsius (°C)",
            "units": ["Celsius (°C)", "Fahrenheit (°F)", "Kelvin (K)", "Rankine (°R)"]
        },
        "Speed": {
            "reference": "Meter per second (m/s)",
            "units": {
                "Meter per second (m/s)": 1.0,
                "Kilometer per hour (km/h)": 1.0 / 3.6,
                "Miles per hour (mph)": 0.44704,
                "Knot (kn)": 0.514444444,
                "Foot per second (ft/s)": 0.3048,
                "Mach (at sea level)": 340.29,
                "Speed of Light (c)": 299792458.0,
            }
        },
        "Area": {
            "reference": "Square Meter (m²)",
            "units": {
                "Square Meter (m²)": 1.0,
                "Square Kilometer (km²)": 1e6,
                "Square Centimeter (cm²)": 1e-4,
                "Square Millimeter (mm²)": 1e-6,
                "Hectare (ha)": 10000.0,
                "Acre (ac)": 4046.8564224,
                "Square Mile (mi²)": 2589988.110336,
                "Square Foot (ft²)": 0.09290304,
                "Square Inch (in²)": 0.00064516,
            }
        },
        "Volume": {
            "reference": "Liter (L)",
            "units": {
                "Liter (L)": 1.0,
                "Milliliter (mL)": 0.001,
                "Cubic Meter (m³)": 1000.0,
                "Cubic Centimeter (cm³)": 0.001,
                "US Gallon (gal)": 3.785411784,
                "US Quart (qt)": 0.946352946,
                "US Pint (pt)": 0.473176473,
                "US Cup": 0.2365882365,
                "US Fluid Ounce (fl oz)": 0.0295735295625,
                "Imperial Gallon": 4.54609,
                "Cubic Foot (ft³)": 28.316846592,
                "Cubic Inch (in³)": 0.016387064,
            }
        },
        "Pressure": {
            "reference": "Pascal (Pa)",
            "units": {
                "Pascal (Pa)": 1.0,
                "Kilopascal (kPa)": 1000.0,
                "Megapascal (MPa)": 1e6,
                "Bar (bar)": 100000.0,
                "Millibar (mbar)": 100.0,
                "Atmosphere (atm)": 101325.0,
                "Torr / mmHg": 133.3223684,
                "Pounds per sq inch (psi)": 6894.757293,
            }
        },
        "Energy": {
            "reference": "Joule (J)",
            "units": {
                "Joule (J)": 1.0,
                "Kilojoule (kJ)": 1000.0,
                "Megajoule (MJ)": 1e6,
                "Calorie (cal)": 4.184,
                "Kilocalorie (kcal)": 4184.0,
                "Watt-hour (Wh)": 3600.0,
                "Kilowatt-hour (kWh)": 3.6e6,
                "Electronvolt (eV)": 1.602176634e-19,
                "British Thermal Unit (BTU)": 1055.06,
                "Foot-pound (ft·lb)": 1.3558179483314,
            }
        },
        "Power": {
            "reference": "Watt (W)",
            "units": {
                "Watt (W)": 1.0,
                "Kilowatt (kW)": 1000.0,
                "Megawatt (MW)": 1e6,
                "Horsepower (hp, mechanical)": 745.699872,
                "Horsepower (metric)": 735.49875,
                "BTU/hour": 0.293071,
                "Foot-pounds/sec": 1.355818,
            }
        },
        "Time": {
            "reference": "Second (s)",
            "units": {
                "Second (s)": 1.0,
                "Millisecond (ms)": 0.001,
                "Microsecond (µs)": 1e-6,
                "Nanosecond (ns)": 1e-9,
                "Minute (min)": 60.0,
                "Hour (hr)": 3600.0,
                "Day (d)": 86400.0,
                "Week (wk)": 604800.0,
                "Julian Year (yr)": 31557600.0,
            }
        },
        "Digital Data": {
            "reference": "Byte (B)",
            "units": {
                "Bit (b)": 0.125,
                "Byte (B)": 1.0,
                "Kilobyte (KB, 10³)": 1e3,
                "Megabyte (MB, 10⁶)": 1e6,
                "Gigabyte (GB, 10⁹)": 1e9,
                "Terabyte (TB, 10¹²)": 1e12,
                "Petabyte (PB, 10¹⁵)": 1e15,
                "Kibibyte (KiB, 2¹⁰)": 1024.0,
                "Mebibyte (MiB, 2²⁰)": 1048576.0,
                "Gibibyte (GiB, 2³⁰)": 1073741824.0,
                "Tebibyte (TiB, 2⁴⁰)": 1099511627776.0,
            }
        },
        "Angle": {
            "reference": "Degree (°)",
            "units": {
                "Degree (°)": 1.0,
                "Radian (rad)": 57.29577951308232,
                "Gradian (grad)": 0.9,
                "Arcminute (arcmin)": 1.0 / 60.0,
                "Arcsecond (arcsec)": 1.0 / 3600.0,
                "Revolution / Turn": 360.0,
            }
        }
    }

    @classmethod
    def get_categories(cls) -> list[str]:
        return list(cls.CATEGORIES.keys())

    @classmethod
    def get_units(cls, category: str) -> list[str]:
        cat = cls.CATEGORIES.get(category)
        if not cat:
            return []
        units = cat["units"]
        if isinstance(units, dict):
            return list(units.keys())
        return list(units)

    @classmethod
    def convert(cls, value: float, category: str, from_unit: str, to_unit: str) -> float:
        """Convert a numerical value between two units in a category."""
        if category == "Temperature":
            return cls._convert_temperature(value, from_unit, to_unit)

        cat = cls.CATEGORIES.get(category)
        if not cat:
            raise ValueError(f"Unknown category: {category}")

        units = cat["units"]
        if from_unit not in units or to_unit not in units:
            raise ValueError(f"Invalid units {from_unit} or {to_unit} in category {category}")

        # Convert to reference unit, then to target unit
        val_in_ref = value * units[from_unit]
        target_val = val_in_ref / units[to_unit]
        return target_val

    @staticmethod
    def _convert_temperature(val: float, from_unit: str, to_unit: str) -> float:
        """Accurate temperature conversions."""
        # Normalize to Celsius
        if "Celsius" in from_unit:
            c = val
        elif "Fahrenheit" in from_unit:
            c = (val - 32.0) * (5.0 / 9.0)
        elif "Kelvin" in from_unit:
            c = val - 273.15
        elif "Rankine" in from_unit:
            c = (val - 491.67) * (5.0 / 9.0)
        else:
            c = val

        # Convert from Celsius to target
        if "Celsius" in to_unit:
            return c
        elif "Fahrenheit" in to_unit:
            return c * (9.0 / 5.0) + 32.0
        elif "Kelvin" in to_unit:
            return c + 273.15
        elif "Rankine" in to_unit:
            return (c + 273.15) * (9.0 / 5.0)
        return c
