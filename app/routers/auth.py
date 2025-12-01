# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import db_models
from app.database import get_db
from app.schemas import UserCreate, UserOut, Token
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)

router = APIRouter()

@router.post("/signup", response_model=UserOut)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    # check username/email uniqueness
    if db.query(db_models.User).filter(db_models.User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(db_models.User).filter(db_models.User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed = get_password_hash(user_in.password)
    user = db_models.User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed,
        is_admin=user_in.is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(form: UserCreate, db: Session = Depends(get_db)):
    # login accepts username & password from same schema for simplicity
    user = db.query(db_models.User).filter(db_models.User.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": user.username, "id": user.id})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def me(current_user: db_models.User = Depends(get_current_user)):
    return current_user
