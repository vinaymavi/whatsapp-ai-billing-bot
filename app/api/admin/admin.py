from fastapi import APIRouter
from pydantic import BaseModel

from app.config import get_settings
from app.services.otp_service import otp_service
from app.utils.whatsapp import send_whatsapp_message

router = APIRouter(prefix="/api/admin", tags=["admin"])
settings = get_settings()


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


class OtpVerifyReq(BaseModel):
    phone_number: str
    otp: str

    @classmethod
    def __get_validators__(cls):
        yield from super().__get_validators__()
        yield cls.validate_phone_number
        yield cls.validate_otp

    @classmethod
    def validate_otp(cls, value):
        if not isinstance(value, str) or not value.isdigit() or len(value) != 6:
            raise ValueError("otp must be a 6-digit number")
        return value

    @classmethod
    def validate_phone_number(cls, value):
        if not isinstance(value, str) or not value.isdigit() or len(value) != 10:
            raise ValueError("phone_number must be a 10-digit number")
        return value


@router.get("/status")
async def get_status():
    return {"status": "Admin API is running"}


@router.post("/otp", status_code=201)
async def post_otp(otp_req: OtpReq):
    otp = otp_service.generate_otp_and_save(otp_req.phone_number)
    message = f"Your OTP is {otp}"
    # Send the OTP via SMS or any other method
    send_whatsapp_message(f"1{otp_req.phone_number}", message, settings)

    return None


@router.post("/otp/verify")
async def post_otp_verify(otp_verify: OtpVerifyReq):
    is_valid = otp_service.verify_otp(otp_verify.phone_number, otp_verify.otp)

    if is_valid:
        return {
            "status": "OTP verified",
            "phone_number": otp_verify.phone_number,
            "otp": otp_verify.otp,
        }

    return {"status": "OTP verification failed"}
