import pytest
from pydantic import ValidationError
from app.schemas import CalculationCreate


def test_valid_calculation_create():
    calc = CalculationCreate(a=10, b=2, type="Divide")
    assert calc.a == 10
    assert calc.b == 2
    assert calc.type == "Divide"


def test_divide_by_zero_rejected():
    with pytest.raises(ValidationError):
        CalculationCreate(a=10, b=0, type="Divide")


def test_invalid_type_rejected():
    with pytest.raises(ValidationError):
        CalculationCreate(a=10, b=2, type="Modulo")


def test_add_with_zero_operand_allowed():
    # Zero is only disallowed as a divisor, not generally
    calc = CalculationCreate(a=0, b=5, type="Add")
    assert calc.a == 0


def test_negative_operands_allowed():
    calc = CalculationCreate(a=-5, b=3, type="Sub")
    assert calc.a == -5
    assert calc.b == 3
