import secrets
from datetime import datetime

from pytz import UTC

from app.services.db_service import db_service
from app.utils.global_logging import get_logger

OTP_COLLECTION = "otp_codes"
OTP_TIMEOUT_SECONDS = 300  # 5 minutes

logger = get_logger(__name__)


class OTPService:
    def __init__(self, length=6):
        self.length = length

    def generate_otp(self):
        return "".join(secrets.choice("0123456789") for _ in range(self.length))

    def save_otp(self, phone_number: str, otp: str):
        db_service.write_with_ttl(
            OTP_COLLECTION, phone_number, {"phone_number": phone_number, "otp": otp}
        )
        return True

    def generate_otp_and_save(self, phone_number: str) -> str:
        otp = self.generate_otp()
        self.save_otp(phone_number, otp)
        return otp

    def verify_otp(self, phone_number: str, otp: str) -> bool:
        record = db_service.read(OTP_COLLECTION, phone_number)

        if record is None:
            return False
        expire_at = record.get("expires_at")
        if record and record.get("otp") == otp and expire_at > datetime.now(UTC):
            db_service.delete(OTP_COLLECTION, phone_number)
            return True

        if record is not None:
            db_service.delete(OTP_COLLECTION, phone_number)

        return False


otp_service = OTPService()
