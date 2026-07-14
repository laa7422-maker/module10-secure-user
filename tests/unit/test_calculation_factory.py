import pytest
from app.calculation_factory import CalculationFactory


def test_add():
    assert CalculationFactory.create("Add", 2, 3) == 5


def test_sub():
    assert CalculationFactory.create("Sub", 5, 3) == 2


def test_multiply():
    assert CalculationFactory.create("Multiply", 4, 3) == 12


def test_divide():
    assert CalculationFactory.create("Divide", 10, 2) == 5


def test_divide_by_zero_raises():
    with pytest.raises(ValueError):
        CalculationFactory.create("Divide", 10, 0)


def test_invalid_type_raises():
    with pytest.raises(ValueError):
        CalculationFactory.create("Modulo", 10, 2)


def test_get_calculation_returns_correct_strategy_instance():
    from app.calculation_factory import AddCalculation
    strategy = CalculationFactory.get_calculation("Add")
    assert isinstance(strategy, AddCalculation)
