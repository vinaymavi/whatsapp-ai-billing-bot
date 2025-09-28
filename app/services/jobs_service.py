from typing import Any, List

from app.services.db_service import db_service
from app.utils.constants import DB_COLLECTION

ORDER_BY = "started_at"


class JobsService:
    def __init__(self):
        pass

    def get_jobs(self, page_size: int) -> List[Any]:
        return db_service.read_list(DB_COLLECTION, page_size, ORDER_BY)


job_service = JobsService()
