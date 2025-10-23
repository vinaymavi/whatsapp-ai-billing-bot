from datetime import timedelta
from typing import Annotated, Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.celery.celery_app import app
from app.celery.tasks import process_file
from app.config import get_settings
from app.services.gcp_storage import gcp_storage
from app.services.jobs_service import job_service
from app.services.jwt_service import jwt_service
from app.services.otp_service import otp_service
from app.utils.constants import CHUNK_SIZE
from app.utils.global_logging import get_logger
from app.utils.whatsapp import send_whatsapp_message

router = APIRouter(prefix="/api/admin", tags=["admin"])
settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/token")
logger = get_logger("Admin Router")


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
    s, err = send_whatsapp_message(f"{otp_req.phone_number}", message, settings)
    if s is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    else:
        return ""


@router.post(
    "/token",
)
async def post_generate_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    is_valid = otp_service.verify_otp(form_data.username, form_data.password)

    if is_valid:
        jwt_token = jwt_service.create_token(
            {"name": "Super Admin", "role": "admin"},
            timedelta(minutes=settings.jwt_expire_time),
        )
        return Token(access_token=jwt_token, token_type="bearer")
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OTP or mobile number",
        )


@router.get(
    "/me",
    response_model=User,
)
async def get_current_user(
    current_user: Annotated[User, Depends(current_user)],
) -> User:
    return current_user


@router.get(
    "/runs",
    response_model=List[Any],
    name="Batch jobs",
    dependencies=[Depends(current_user)],
)
async def get_runs(
    page_size: int = Query(1, ge=1, le=100),
):
    """_summary_

    Args:
        page_size (int, optional): size of the page. Defaults to Query(1, ge=1, le=100).

    Raises:
        HTTPException: Http server error

    Returns:
        List: of Firestore documents
    """
    try:
        return job_service.get_jobs(page_size)
    except Exception as e:
        logger.error(f"Exception occur {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/batch", name="Create Batch Job")
async def post_batch(file: UploadFile, user: User = Depends(current_user)):
    allowed_types = ["text/plain", "application/pdf", "image/jpeg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not supported ",
        )

    gcp_blob_name = gcp_storage.generate_unique_file_path(
        "batch-files", file.content_type
    )

    await gcp_storage.upload_stream(file, gcp_blob_name, CHUNK_SIZE)
    task = process_file.delay(
        gcp_blob_name, file.content_type, user.name, file.filename
    )
    logger.info(f"/batch processing {task}")

    return {"task": task.id, "status": "IN-PROGRESS"}


@router.get(
    "/batch/{task_id}",
    name="Get Batch Job Status",
    dependencies=[Depends(current_user)],
)
async def get_batch_status(task_id: str):
    """Get the status of a Celery batch processing task.

    Args:
        task_id (str): The ID of the task returned by the /batch endpoint

    Returns:
        dict: Task information including id, status, result, and traceback (if failed)

    Raises:
        HTTPException: If task is not found or an error occurs
    """

    task_result = app.AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": task_result.state,
    }

    if task_result.state == "PENDING":
        response["detail"] = "Task has not been executed yet"
    elif task_result.state == "SUCCESS":
        response["result"] = task_result.result
    elif task_result.state == "FAILURE":
        response["error"] = str(task_result.info)
        response["traceback"] = task_result.traceback
    elif task_result.state in ["RETRY", "IN-PROGRESS"]:
        response["detail"] = "Task is currently being processed"

    logger.info(f"Task status retrieved for {task_id}: {task_result.state}")
    return response
