# Google Cloud Build Triggers Infrastructure

This document explains how to set up the infrastructure for Google Cloud Build triggers to automatically build and deploy the WhatsApp AI Billing Bot to Cloud Run.

## Overview

This repository includes Terraform configuration to provision the necessary infrastructure for Cloud Build triggers:

- **Cloud Build API**: Enabled for your GCP project
- **IAM Permissions**: Service account with necessary permissions to:
  - Access Secret Manager
  - Create and manage Cloud Build operations
  - Write logs
  - Deploy to Cloud Run
- **Example Trigger Configuration**: Commented example triggers in `infrastructure/main.tf` that you can customize

## What This Provides

This infrastructure setup gives you the foundation to create Cloud Build triggers. You will need to:

1. Create your own `cloudbuild.yaml` file(s) for your application
2. Uncomment and customize the example triggers in `infrastructure/main.tf`, or
3. Create triggers manually via the GCP Console

## Prerequisites

Before setting up Cloud Build triggers, ensure you have:

1. A Google Cloud Platform (GCP) account
2. A GitHub repository connected to Google Cloud Build
3. The following GCP APIs enabled (Terraform will enable these):
   - Cloud Build API
   - Cloud Run API
   - Artifact Registry API
   - Secret Manager API
   - Firestore API
   - Cloud Storage API

## Setting Up the Infrastructure

### Step 1: Apply Terraform Configuration

The Terraform configuration provisions the necessary infrastructure for Cloud Build.

1. Navigate to the infrastructure directory:
   ```bash
   cd infrastructure
   ```

2. Set up your environment variables (see `infrastructure/README.md` for details):
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   source ./init_env.sh
   ```

3. Initialize and apply Terraform:
   ```bash
   terraform init
   terraform plan -out=tfplan
   terraform apply tfplan
   ```

This will provision:
- Cloud Build API enablement
- Required IAM permissions for the service account (Secret Manager access, Cloud Build editor, logging)
- Example trigger configurations (commented out in `infrastructure/main.tf`)

### Step 2: Create Your Cloud Build Configuration File

Create a `cloudbuild.yaml` file in the root of your repository that defines your build and deployment process. Here's a basic example structure:

```yaml
steps:
  # Build your Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - '${_GCP_LOCATION}-docker.pkg.dev/${PROJECT_ID}/${_ARTIFACT_REGISTRY_REPO}/${_IMAGE_NAME}:${SHORT_SHA}'
      - '.'

  # Push to Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - '${_GCP_LOCATION}-docker.pkg.dev/${PROJECT_ID}/${_ARTIFACT_REGISTRY_REPO}/${_IMAGE_NAME}:${SHORT_SHA}'

  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - '${_SERVICE_NAME}'
      - '--image=${_GCP_LOCATION}-docker.pkg.dev/${PROJECT_ID}/${_ARTIFACT_REGISTRY_REPO}/${_IMAGE_NAME}:${SHORT_SHA}'
      - '--region=${_GCP_LOCATION}'
      - '--platform=managed'

substitutions:
  _GCP_LOCATION: 'asia-south1'
  _ARTIFACT_REGISTRY_REPO: 'whatsapp-chatbot-repo'
  _IMAGE_NAME: 'whatsapp-ai-agent'
  _SERVICE_NAME: 'whatsapp-ai-agent'

timeout: '1800s'
```

### Step 3: Create Cloud Build Triggers

You have two options to create the triggers:

#### Option A: Using Terraform (Uncomment Example Configuration)

1. Edit `infrastructure/main.tf` and uncomment the example trigger configurations
2. Customize the trigger settings (branch, filename, substitutions) as needed
3. Run `terraform apply` to create the triggers

#### Option B: Manual Setup via GCP Console

1. Go to the [Cloud Build Triggers page](https://console.cloud.google.com/cloud-build/triggers) in GCP Console

2. Click "Create Trigger"

3. Configure your trigger:
   - **Name**: Your choice (e.g., `whatsapp-ai-agent-deploy`)
   - **Description**: Description of what the trigger does
   - **Event**: Push to a branch
   - **Source**: Select your GitHub repository
   - **Branch**: `^main$` (regex pattern for main branch)
   - **Configuration**: Cloud Build configuration file
   - **Cloud Build configuration file location**: `cloudbuild.yaml`
   - **Service account**: Select the Cloud Run deployer service account

4. Add substitution variables as needed

5. Click "Create"

## Creating Cloud Build Configuration Files

Your `cloudbuild.yaml` file should define the complete build and deployment process. Key sections include:

### Steps
Define the build steps in sequence:
- **Build**: Build Docker images
- **Push**: Push images to Artifact Registry
- **Deploy**: Deploy to Cloud Run or Cloud Run Jobs

### Substitutions
Variables that can be customized per trigger (e.g., region, image name, service name)

### Timeout
Maximum time allowed for the build (default: 10 minutes, max: 24 hours)

### Example for Multi-Stage Build

If you have a multi-stage build (like frontend + backend), your cloudbuild.yaml might look like:

```yaml
steps:
  # Build the Docker image (includes frontend build stage)
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - '${_GCP_LOCATION}-docker.pkg.dev/${PROJECT_ID}/${_ARTIFACT_REGISTRY_REPO}/${_IMAGE_NAME}:${SHORT_SHA}'
      - '-t'
      - '${_GCP_LOCATION}-docker.pkg.dev/${PROJECT_ID}/${_ARTIFACT_REGISTRY_REPO}/${_IMAGE_NAME}:latest'
      - '.'

  # Push both tags
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', '--all-tags', '${_GCP_LOCATION}-docker.pkg.dev/${PROJECT_ID}/${_ARTIFACT_REGISTRY_REPO}/${_IMAGE_NAME}']

  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - '${_SERVICE_NAME}'
      - '--image=${_GCP_LOCATION}-docker.pkg.dev/${PROJECT_ID}/${_ARTIFACT_REGISTRY_REPO}/${_IMAGE_NAME}:${SHORT_SHA}'
      - '--region=${_GCP_LOCATION}'
      - '--platform=managed'
      - '--allow-unauthenticated'
      - '--memory=512Mi'
      - '--cpu=1'
      - '--update-secrets=WEBHOOK_TOKEN=WEBHOOK_TOKEN:latest,WHATSAPP_API_TOKEN=WHATSAPP_API_TOKEN:latest,OPENAI_API_KEY=OPENAI_API_KEY:latest'

images:
  - '${_GCP_LOCATION}-docker.pkg.dev/${PROJECT_ID}/${_ARTIFACT_REGISTRY_REPO}/${_IMAGE_NAME}:${SHORT_SHA}'
  - '${_GCP_LOCATION}-docker.pkg.dev/${PROJECT_ID}/${_ARTIFACT_REGISTRY_REPO}/${_IMAGE_NAME}:latest'
```

## Environment Variables and Secrets

The Cloud Build configuration uses two types of values:

### Environment Variables (Non-sensitive)
These are passed directly as environment variables:
- `ENVIRONMENT`
- `GCP_PROJECT_ID`
- `GCP_LOCATION`
- `GCP_STORAGE_BUCKET`
- `FIRESTORE_COLLECTION_CHAT_HISTORY`
- `FIRESTORE_COLLECTION_PROCESSED_MESSAGES`
- `WHATSAPP_PHONE_NUMBER_ID`
- `WHATSAPP_BUSINESS_ACCOUNT_ID`
- `OPENAI_MODEL`
- `LANGCHAIN_TRACING_V2`
- `PINECONE_INDEX_NAME`
- And more...

### Secrets (Sensitive)
These are stored in Google Secret Manager and accessed securely:
- `WEBHOOK_TOKEN`
- `WHATSAPP_API_TOKEN`
- `OPENAI_API_KEY`
- `LANGCHAIN_API_KEY`
- `PINECONE_API_KEY`
- `JWT_SECRET_KEY`

### Setting Up Secrets

Create secrets in Google Secret Manager:

```bash
# Create a secret
echo -n "your-secret-value" | gcloud secrets create SECRET_NAME --data-file=-

# Grant the service account access to the secret
gcloud secrets add-iam-policy-binding SECRET_NAME \
    --member="serviceAccount:YOUR_SERVICE_ACCOUNT@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

Required secrets:
- `WEBHOOK_TOKEN`
- `WHATSAPP_API_TOKEN`
- `OPENAI_API_KEY`
- `LANGCHAIN_API_KEY`
- `PINECONE_API_KEY`
- `JWT_SECRET_KEY`

## Service Account Permissions

The Cloud Run deployer service account needs the following IAM roles:

- `roles/artifactregistry.admin` - Push Docker images to Artifact Registry
- `roles/run.developer` - Deploy to Cloud Run
- `roles/iam.serviceAccountUser` - Act as other service accounts
- `roles/secretmanager.secretAccessor` - Access secrets from Secret Manager
- `roles/cloudbuild.builds.editor` - Manage Cloud Build operations
- `roles/logging.logWriter` - Write build logs

These permissions are automatically granted when using the Terraform configuration.

## Triggering Builds

### Automatic Triggers

Once set up, Cloud Build triggers will automatically run when:
- Code is pushed to the `main` branch

### Manual Triggers

You can manually trigger a build:

1. Via GCP Console:
   - Go to Cloud Build > Triggers
   - Click "Run" on the desired trigger

2. Via gcloud CLI:
   ```bash
   gcloud builds triggers run whatsapp-ai-agent-deploy --branch=main
   gcloud builds triggers run whatsapp-ai-celery-worker-deploy --branch=main
   ```

## Viewing Build Logs

To view build logs:

1. Via GCP Console:
   - Go to Cloud Build > History
   - Click on a build to view details and logs

2. Via gcloud CLI:
   ```bash
   gcloud builds list
   gcloud builds log BUILD_ID
   ```

## Customizing the Build

### Modifying Substitution Variables

Edit the `substitutions` section in `cloudbuild.yaml` or `cloudbuild-celery.yaml` to change:
- Region/location
- Image names
- Service/job names
- Environment variables
- Resource limits (memory, CPU)

### Changing Build Configuration

Modify the `steps` section in the Cloud Build files to:
- Add pre-build or post-build steps
- Run tests before deployment
- Add notification steps
- Customize the deployment process

## Comparison with GitHub Actions

The repository supports both GitHub Actions and Cloud Build triggers:

| Feature | GitHub Actions | Cloud Build Triggers |
|---------|---------------|---------------------|
| Trigger | Manual (workflow_dispatch) | Automatic (on push to main) |
| Configuration | `.github/workflows/` | `cloudbuild.yaml` |
| Authentication | Workload Identity | Service Account |
| Secrets | GitHub Secrets | GCP Secret Manager |
| Cost | GitHub minutes | GCP build minutes |
| Best for | Manual deployments | Automatic CI/CD |

You can use both in parallel:
- **Cloud Build Triggers**: For automatic deployments on every push to main
- **GitHub Actions**: For manual, controlled production deployments

## Disabling Automatic Deployments

If you want to disable automatic deployments:

1. Via GCP Console:
   - Go to Cloud Build > Triggers
   - Select the trigger
   - Click "Disable"

2. Via Terraform:
   - Set `disabled = true` in the trigger resource
   - Run `terraform apply`

## Troubleshooting

### Build Fails with "Permission Denied"

Ensure the service account has all required IAM roles:
```bash
gcloud projects get-iam-policy PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:YOUR_SA@PROJECT_ID.iam.gserviceaccount.com"
```

### Cannot Access Secrets

Verify the service account has access to Secret Manager:
```bash
gcloud secrets get-iam-policy SECRET_NAME
```

### Deployment Fails

Check Cloud Run logs for deployment errors:
```bash
gcloud run services describe whatsapp-ai-agent --region=REGION
```

### Build Timeout

Increase the timeout in the Cloud Build configuration:
```yaml
timeout: '3600s'  # Increase from default 1800s
```

## Cost Optimization

Cloud Build provides a free tier:
- First 120 build-minutes per day are free
- After that, you pay per build-minute

To optimize costs:
1. Use smaller machine types when possible
2. Optimize Docker layer caching
3. Disable automatic triggers for non-production branches
4. Set up build retention policies

## Security Best Practices

1. **Never commit secrets**: Always use Secret Manager for sensitive values
2. **Restrict service account permissions**: Use the principle of least privilege
3. **Use private Artifact Registry**: Keep your Docker images private
4. **Enable VPC Service Controls**: For additional security (optional)
5. **Audit build logs**: Regularly review Cloud Build history for unauthorized builds

## Additional Resources

- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Secret Manager Documentation](https://cloud.google.com/secret-manager/docs)
- [Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)
