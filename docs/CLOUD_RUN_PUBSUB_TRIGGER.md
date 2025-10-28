# Cloud Run Pub/Sub Trigger Setup

This document explains the Pub/Sub trigger configuration that enables event-driven processing of Celery tasks through Cloud Run.

## Overview

The WhatsApp AI Billing Bot uses Google Cloud Pub/Sub as the Celery message broker. This Terraform configuration creates an **Eventarc trigger** that listens to Pub/Sub messages from the Celery queue and automatically invokes a Cloud Run service endpoint to process those tasks.

## Architecture

```
Celery Task Created
      ↓
Pub/Sub Topic (celery)
      ↓
Eventarc Trigger
      ↓
Cloud Run Service Endpoint (/api/celery/process)
      ↓
Task Processing
```

## What Gets Provisioned

### 1. Pub/Sub Topic
- **Name**: `celery`
- **Purpose**: Message queue for Celery tasks
- **Retention**: 24 hours
- **Location**: Global (Pub/Sub topics are global resources)

### 2. Eventarc Trigger
- **Name**: `celery-pubsub-trigger`
- **Type**: Pub/Sub message published event
- **Source**: `projects/{PROJECT_ID}/topics/celery`
- **Destination**: Cloud Run service endpoint
- **Service**: `whatsapp-ai-agent` (main application)
- **Endpoint**: `/api/celery/process`

### 3. Service Account
- **Name**: `eventarc-trigger-sa`
- **Purpose**: Authenticate Eventarc when invoking Cloud Run
- **Permissions**:
  - `roles/run.invoker` - Invoke Cloud Run services
  - `roles/pubsub.subscriber` - Subscribe to Pub/Sub topics

### 4. APIs Enabled
- `eventarc.googleapis.com` - Eventarc service
- `pubsub.googleapis.com` - Pub/Sub messaging

## Prerequisites

Before deploying this trigger:

1. **Cloud Run service must be deployed**: The main application (`whatsapp-ai-agent`) must be running
2. **Endpoint must exist**: Your application must have the `/api/celery/process` endpoint implemented
3. **Celery must be configured**: Your Celery app should use Pub/Sub as the broker

## Deployment

### Using Terraform

1. Navigate to the infrastructure directory:
   ```bash
   cd infrastructure
   ```

2. Set up your environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   source ./init_env.sh
   ```

3. Apply the Terraform configuration:
   ```bash
   terraform init
   terraform plan -out=tfplan
   terraform apply tfplan
   ```

This will create:
- The Pub/Sub topic for Celery tasks
- Eventarc trigger configuration
- Service account with necessary permissions
- Enable required GCP APIs

## Implementation Requirements

### Cloud Run Service Endpoint

Your Cloud Run application needs to implement an endpoint to handle the Pub/Sub messages. Here's an example structure:

```python
from fastapi import APIRouter, Request
import base64
import json

router = APIRouter(prefix="/api/celery", tags=["celery"])

@router.post("/process")
async def process_celery_task(request: Request):
    """
    Endpoint triggered by Pub/Sub via Eventarc.
    
    Receives Celery task messages and processes them.
    """
    # Get the Pub/Sub message from the request
    envelope = await request.json()
    
    # Extract the Pub/Sub message
    if "message" not in envelope:
        return {"error": "Invalid Pub/Sub message format"}, 400
    
    pubsub_message = envelope["message"]
    
    # Decode the message data
    if "data" in pubsub_message:
        message_data = base64.b64decode(pubsub_message["data"]).decode("utf-8")
        task_data = json.loads(message_data)
        
        # Process the Celery task
        # Extract task_name, args, kwargs, etc. from task_data
        task_name = task_data.get("task")
        task_args = task_data.get("args", [])
        task_kwargs = task_data.get("kwargs", {})
        
        # Execute the appropriate task handler
        # ... your task processing logic ...
        
        return {"status": "success", "task": task_name}
    
    return {"error": "No data in message"}, 400
```

### Message Format

Pub/Sub messages from Celery typically include:
- `task`: Task name/identifier
- `id`: Task ID
- `args`: Positional arguments
- `kwargs`: Keyword arguments
- `retries`: Number of retries attempted
- `eta`: Execution time (if scheduled)

## Testing

### 1. Verify Trigger Creation

```bash
# List Eventarc triggers
gcloud eventarc triggers list --location=asia-south1

# Describe the specific trigger
gcloud eventarc triggers describe celery-pubsub-trigger \
    --location=asia-south1
```

### 2. Test Pub/Sub Message

Send a test message to the Celery topic:

```bash
gcloud pubsub topics publish celery \
    --message='{"task": "test_task", "args": [], "kwargs": {}}' \
    --project=YOUR_PROJECT_ID
```

### 3. Check Cloud Run Logs

```bash
# View logs for the Cloud Run service
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=whatsapp-ai-agent" \
    --limit=50 \
    --format=json
```

## Monitoring

### Eventarc Metrics

Monitor trigger activity in Cloud Console:
1. Go to **Eventarc** in GCP Console
2. Click on the trigger name
3. View metrics:
   - Event count
   - Success/failure rates
   - Latency

### Cloud Logging

View trigger execution logs:
```bash
# Filter logs by Eventarc trigger
gcloud logging read \
    'resource.type="eventarc.googleapis.com/Trigger"
     resource.labels.trigger_id="celery-pubsub-trigger"' \
    --limit=50
```

## Celery Integration

### Broker Configuration

Ensure your Celery app is configured to use Pub/Sub:

```python
from celery import Celery

PROJECT_ID = "your-project-id"

app = Celery(
    "celery",
    broker=f"gcpubsub://projects/{PROJECT_ID}",
    backend=f"gs://your-bucket/results"
)
```

### Topic Naming

The Celery Pub/Sub broker creates topics with the pattern:
- Default topic: `celery` (for regular tasks)
- You can configure custom queues which will create separate topics

## Troubleshooting

### Trigger Not Firing

1. **Check Pub/Sub subscription**:
   ```bash
   gcloud pubsub subscriptions list
   ```
   Eventarc automatically creates a subscription for the trigger.

2. **Verify service account permissions**:
   ```bash
   gcloud projects get-iam-policy YOUR_PROJECT_ID \
       --flatten="bindings[].members" \
       --filter="bindings.members:eventarc-trigger-sa@"
   ```

3. **Check Cloud Run service is running**:
   ```bash
   gcloud run services describe whatsapp-ai-agent \
       --region=asia-south1
   ```

### Messages Not Reaching Endpoint

1. **Verify endpoint exists**: Make sure `/api/celery/process` is implemented
2. **Check authentication**: Eventarc service account needs `run.invoker` permission
3. **Review Cloud Run logs**: Look for incoming requests and errors

### Permission Errors

If you see permission errors:

```bash
# Grant Eventarc service agent permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:service-PROJECT_NUMBER@gcp-sa-eventarc.iam.gserviceaccount.com" \
    --role="roles/eventarc.serviceAgent"
```

## Customization

### Different Endpoint

To use a different endpoint, modify `infrastructure/main.tf`:

```hcl
destination {
  cloud_run_service {
    service = "whatsapp-ai-agent"
    region  = var.gcp_zone_india
    path    = "/your/custom/endpoint"  # Change this
  }
}
```

### Multiple Topics

To listen to multiple Pub/Sub topics, create additional triggers:

```hcl
resource "google_eventarc_trigger" "celery_priority_trigger" {
  name     = "celery-priority-trigger"
  location = var.gcp_zone_india
  
  matching_criteria {
    attribute = "type"
    value     = "google.cloud.pubsub.topic.v1.messagePublished"
  }
  
  transport {
    pubsub {
      topic = "projects/${var.gcp_project_id}/topics/celery-priority"
    }
  }
  
  destination {
    cloud_run_service {
      service = "whatsapp-ai-agent"
      region  = var.gcp_zone_india
      path    = "/api/celery/process-priority"
    }
  }
  
  service_account = google_service_account.eventarc_trigger.email
}
```

## Cost Considerations

- **Eventarc**: Free tier available (10,000 events/month), then $0.40 per 10,000 events
- **Pub/Sub**: Free tier (10 GB/month), then pricing based on message volume
- **Cloud Run**: Pay per request and compute time

## Security Best Practices

1. **Least Privilege**: Service account has only necessary permissions
2. **Private Endpoints**: Consider making Cloud Run service private (only invokable by service account)
3. **Message Validation**: Always validate incoming Pub/Sub messages in your endpoint
4. **Authentication**: Eventarc uses service account authentication to invoke Cloud Run

## Additional Resources

- [Eventarc Documentation](https://cloud.google.com/eventarc/docs)
- [Pub/Sub with Cloud Run](https://cloud.google.com/run/docs/tutorials/pubsub)
- [Celery with GCP Pub/Sub](https://docs.celeryproject.org/en/stable/userguide/configuration.html#broker-url)
- [Eventarc Triggers Reference](https://cloud.google.com/eventarc/docs/creating-triggers)
