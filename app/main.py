from app.security import verify_password, create_access_token
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

@app.post("/login", response_model=schemas.Token)
def login(credentials: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Authenticate a user and issue a JWT access token."""

    user = db.query(models.User).filter(models.User.username == credentials.username).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
