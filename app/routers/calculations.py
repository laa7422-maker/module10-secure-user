from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Calculation, User
from app.schemas import CalculationCreate, CalculationUpdate, CalculationRead
from app.calculation_factory import CalculationFactory
from app.dependencies import get_current_user

router = APIRouter(prefix="/calculations", tags=["calculations"])


@router.get("/", response_model=List[CalculationRead])
def browse_calculations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Calculation).filter(Calculation.user_id == current_user.id).all()


@router.get("/{calc_id}", response_model=CalculationRead)
def read_calculation(
    calc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    calc = db.query(Calculation).filter(
        Calculation.id == calc_id, Calculation.user_id == current_user.id
    ).first()
    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calc


@router.post("/", response_model=CalculationRead, status_code=status.HTTP_201_CREATED)
def add_calculation(
    calc_in: CalculationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = CalculationFactory.create(calc_in.type.value, calc_in.a, calc_in.b)

    calc = Calculation(
        a=calc_in.a,
        b=calc_in.b,
        type=calc_in.type.value,
        result=result,
        user_id=current_user.id,
    )
    db.add(calc)
    db.commit()
    db.refresh(calc)
    return calc


@router.put("/{calc_id}", response_model=CalculationRead)
def edit_calculation(
    calc_id: int,
    calc_in: CalculationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    calc = db.query(Calculation).filter(
        Calculation.id == calc_id, Calculation.user_id == current_user.id
    ).first()
    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")

    update_data = calc_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "type":
            value = value.value
        setattr(calc, field, value)

    try:
        calc.result = CalculationFactory.create(calc.type, calc.a, calc.b)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    db.commit()
    db.refresh(calc)
    return calc


@router.delete("/{calc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(
    calc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    calc = db.query(Calculation).filter(
        Calculation.id == calc_id, Calculation.user_id == current_user.id
    ).first()
    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")
    db.delete(calc)
    db.commit()
