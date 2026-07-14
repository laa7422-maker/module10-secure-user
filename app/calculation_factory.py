from abc import ABC, abstractmethod


class CalculationStrategy(ABC):
    """Abstract base class defining the interface all calculation types must implement."""

    @abstractmethod
    def execute(self, a: float, b: float) -> float:
        ...


class AddCalculation(CalculationStrategy):
    def execute(self, a: float, b: float) -> float:
        return a + b


class SubCalculation(CalculationStrategy):
    def execute(self, a: float, b: float) -> float:
        return a - b


class MultiplyCalculation(CalculationStrategy):
    def execute(self, a: float, b: float) -> float:
        return a * b


class DivideCalculation(CalculationStrategy):
    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b


class CalculationFactory:
    """Factory that selects and runs the correct calculation strategy based on type."""

    _strategies = {
        "Add": AddCalculation,
        "Sub": SubCalculation,
        "Multiply": MultiplyCalculation,
        "Divide": DivideCalculation,
    }

    @classmethod
    def get_calculation(cls, calc_type: str) -> CalculationStrategy:
        strategy_class = cls._strategies.get(calc_type)
        if strategy_class is None:
            raise ValueError(f"Unsupported calculation type: {calc_type}")
        return strategy_class()

    @classmethod
    def create(cls, calc_type: str, a: float, b: float) -> float:
        strategy = cls.get_calculation(calc_type)
        return strategy.execute(a, b)
