from celery import Celery

from app.config import get_settings

settings = get_settings()
PROJECT_ID = settings.gcp_project_id
RESULTS_BUCKET = "chat-gpt-videos-chabot-celery-files"
FIRESTORE_PROJECT = PROJECT_ID

app = Celery(
    "celery",
    broker=f"gcpubsub://projects/{PROJECT_ID}",
    backend=f"gs://{RESULTS_BUCKET}/tasks?gcs_project={PROJECT_ID}&gcs_ttl=86400&gcs_threadpool_maxsize=20&firestore_project={FIRESTORE_PROJECT}",
)
app.autodiscover_tasks(["app.celery"])
