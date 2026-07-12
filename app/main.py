from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db, Base, engine
from app import models, schemas
from app.security import hash_password

# Create tables on startup (fine for dev/testing; migrations replace this in production)
Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/users", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create a new user with a securely hashed password."""

    # 1. Hash the incoming plain-text password
    hashed = hash_password(user.password)

    # 2. Build the database model instance
    new_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed,
    )

    # 3. Save it, handling duplicate username/email gracefully
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists.",
        )

    db.refresh(new_user)
    return new_user
