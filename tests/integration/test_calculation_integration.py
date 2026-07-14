from app.models import Calculation
from app.calculation_factory import CalculationFactory


def test_create_calculation_record(db_session):
    result = CalculationFactory.create("Add", 3, 4)
    calc = Calculation(a=3, b=4, type="Add", result=result)

    db_session.add(calc)
    db_session.commit()

    saved = db_session.query(Calculation).filter_by(id=calc.id).first()
    assert saved is not None
    assert saved.a == 3
    assert saved.b == 4
    assert saved.result == 7
    assert saved.type == "Add"


def test_divide_record_stores_correct_result(db_session):
    result = CalculationFactory.create("Divide", 10, 2)
    calc = Calculation(a=10, b=2, type="Divide", result=result)

    db_session.add(calc)
    db_session.commit()

    saved = db_session.query(Calculation).filter_by(id=calc.id).first()
    assert saved.result == 5


def test_multiple_calculations_persist_independently(db_session):
    calc1 = Calculation(a=1, b=1, type="Add", result=CalculationFactory.create("Add", 1, 1))
    calc2 = Calculation(a=9, b=3, type="Sub", result=CalculationFactory.create("Sub", 9, 3))

    db_session.add_all([calc1, calc2])
    db_session.commit()

    all_records = db_session.query(Calculation).all()
    assert len(all_records) == 2
