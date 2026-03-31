from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.schemas.auth import AuthenticatedUser, LoginRequest, TokenResponse
from app.services.auth import AuthenticationError, authenticate_user, build_login_response, serialize_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = authenticate_user(db, payload.email, payload.password)
    except AuthenticationError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))
    return build_login_response(user)


@router.get("/me", response_model=AuthenticatedUser)
def me(current_user=Depends(get_current_user)):
    return serialize_user(current_user)
