from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.config import get_settings
from app.services.jwt_service import jwt_service
from app.services.otp_service import otp_service
from app.utils.whatsapp import send_whatsapp_message

router = APIRouter(prefix="/api/admin", tags=["admin"])
settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/token")


class OtpReq(BaseModel):
    phone_number: str

    @classmethod
    def __get_validators__(cls):
        yield from super().__get_validators__()
        yield cls.validate_phone_number

    @classmethod
    def validate_phone_number(cls, value):
        if not isinstance(value, str) or not value.isdigit() or len(value) != 10:
            raise ValueError("phone_number must be a 10-digit number")
        return value


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    name: str
    role: str


async def current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    data = jwt_service.verify_token(token=token)
    return User(**data)


@router.get("/status")
async def get_status():
    return {"status": "Admin API is running"}


@router.post("/otp", status_code=201)
async def post_otp(otp_req: OtpReq) -> str:
    otp = otp_service.generate_otp_and_save(otp_req.phone_number)
    message = f"Your OTP is {otp}"
    # Send the OTP via SMS or any other method
    s, err = send_whatsapp_message(f"1{otp_req.phone_number}", message, settings)
    if s is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    else:
        return ""


@router.post("/token")
async def post_generate_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    is_valid = otp_service.verify_otp(form_data.username, form_data.password)

    if is_valid:
        jwt_token = jwt_service.create_token({"name": "Super Admin", "role": "admin"})
        return Token(access_token=jwt_token, token_type="bearer")
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OTP or mobile number",
        )


@router.get("/me", response_model=User)
async def get_current_user(
    current_user: Annotated[User, Depends(current_user)],
) -> User:
    return current_user
