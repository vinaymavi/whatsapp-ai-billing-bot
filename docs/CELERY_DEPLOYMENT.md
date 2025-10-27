# Celery Cloud Run Jobs Deployment

This workflow deploys the Celery worker application to Google Cloud Run Jobs for background task processing.

## Overview

- **File**: `.github/workflows/deploy-celery-to-cloud-run-jobs.yml`
- **Trigger**: Manual (`workflow_dispatch`)
- **Target**: Google Cloud Run Jobs
- **Docker Image**: Uses `Dockerfile.celery`

## What it does

1. **Builds** the Celery worker using `Dockerfile.celery`
2. **Pushes** the image to Google Container Registry
3. **Deploys** to Cloud Run Jobs with appropriate configuration
4. **Executes** a test run to verify the deployment

## Key Features

- **Resource Allocation**: 2 CPU cores, 2GB memory
- **Retry Policy**: Maximum 3 retries on failure
- **Execution Model**: Single task, single parallelism (can be adjusted)
- **Environment Variables**: All necessary environment variables for the application

## Manual Execution

To run this workflow manually:

1. Go to the **Actions** tab in your GitHub repository
2. Select **Deploy Celery to Cloud Run Jobs**
3. Click **Run workflow**
4. Choose the branch (usually `main`) and click **Run workflow**

## Cloud Run Jobs vs Cloud Run Services

**Cloud Run Jobs** are ideal for:
- Batch processing
- Background tasks
- One-time or scheduled executions
- Celery workers that process tasks from a queue

**Cloud Run Services** are ideal for:
- HTTP-based applications
- Always-on services
- Web APIs
- Applications that need to respond to requests

## Environment Variables Required

The workflow requires the same environment variables as the main application:

### Repository Variables (`vars`)
- `ENVIRONMENT`
- `GCP_DOCKER_REGISTRY_URI`
- `GCP_PROJECT_ID`
- `GCP_LOCATION`
- `GCP_STORAGE_BUCKET`
- `GCP_SA_EMAIL`
- `GCP_WLIP_GITHUB_PROVIDER`
- All other application-specific variables

### Repository Secrets (`secrets`)
- `WEBHOOK_TOKEN`
- `WHATSAPP_API_TOKEN`
- `OPENAI_API_KEY`
- `LANGCHAIN_API_KEY`
- `PINECONE_API_KEY`
- `JWT_SECRET_KEY`

## Monitoring and Logs

After deployment, you can monitor the Celery worker through:

1. **Google Cloud Console**:
   - Navigate to Cloud Run Jobs
   - View execution history and logs

2. **Command Line**:
   ```bash
   # List jobs
   gcloud run jobs list --region=us-central1

   # Describe the job
   gcloud run jobs describe whatsapp-ai-celery-worker --region=us-central1

   # Execute the job manually
   gcloud run jobs execute whatsapp-ai-celery-worker --region=us-central1

   # View execution logs
   gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=whatsapp-ai-celery-worker" --limit=50
   ```

## Customization

You can customize the deployment by modifying the workflow file:

- **CPU/Memory**: Adjust `--cpu` and `--memory` flags
- **Parallelism**: Change `--parallelism` for concurrent task processing
- **Max Retries**: Modify `--max-retries` for failure handling
- **Task Count**: Adjust `--task-count` for batch processing

## Celery Configuration

The Celery app configuration is in `app/celery/celery_app.py`:
- **Broker**: Google Cloud Pub/Sub
- **Backend**: Google Cloud Storage with Firestore
- **Task Discovery**: Auto-discovers tasks from `app.celery`

## Troubleshooting

1. **Job fails to start**: Check environment variables and GCP permissions
2. **Image build fails**: Verify `Dockerfile.celery` and dependencies
3. **Job execution timeout**: Increase timeout or optimize task processing
4. **Authentication issues**: Verify service account permissions for Pub/Sub, Storage, and Firestore
