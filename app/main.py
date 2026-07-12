from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app import models, schemas
from app.database import engine, get_db, Base
from app.security import hash_password, verify_password, create_access_token, decode_access_token, oauth2_scheme
#                                                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#                                                          ⬆️ ADD these two new imports to the existing line

Base.metadata.create_all(bind=engine)

app = FastAPI()


# ⬇️ ⬇️ ⬇️  ADD THIS NEW FUNCTION HERE — after `app = FastAPI()`, before any routes  ⬇️ ⬇️ ⬇️
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    """Decode the JWT, find the matching user, or reject the request."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username = payload.get("sub")
    if username is None:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception

    return user
# ⬆️ ⬆️ ⬆️  END of new function  ⬆️ ⬆️ ⬆️


# --- your existing /users route stays exactly as-is ---
@app.post("/users", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_pw = hash_password(user.password)
    new_user = models.User(username=user.username, email=user.email, password_hash=hashed_pw)
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username or email already exists.")
    db.refresh(new_user)
    return new_user


# --- your existing /login route stays exactly as-is ---
@app.post("/login", response_model=schemas.Token)
def login(credentials: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


# ⬇️ ⬇️ ⬇️  ADD THIS NEW ROUTE HERE — anywhere after get_current_user is defined  ⬇️ ⬇️ ⬇️
@app.get("/me", response_model=schemas.UserRead)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user

