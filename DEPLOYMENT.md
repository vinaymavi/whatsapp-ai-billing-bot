# Deployment to Google Cloud Run

This guide explains how to set up the necessary components to deploy the WhatsApp AI Billing Bot to Google Cloud Run using GitHub Actions.

## Prerequisites

1. A Google Cloud Platform (GCP) account
2. A GitHub repository for your code
3. Google Cloud CLI (gcloud) installed (for local testing)

## Initial Setup

### Set up Google Cloud Project

1. Create a new Google Cloud Project or use an existing one
2. Enable the following APIs:
   - Cloud Run API
   - Container Registry API
   - Secret Manager API
   - Firestore API
   - Cloud Storage API

### Create a Service Account for GitHub Actions

1. In the Google Cloud Console, go to IAM & Admin > Service Accounts
2. Create a new service account (e.g., `github-deploy`)
3. Add the following roles to this service account:
   - Cloud Run Admin
   - Storage Admin
   - Service Account User
   - Secret Manager Admin
   - Artifact Registry Admin

4. Create and download a JSON key for this service account

### Set up Secrets in GitHub

Add the following secrets to your GitHub repository (Settings > Secrets > Actions):

1. `GCP_PROJECT_ID` - Your Google Cloud Project ID
2. `GCP_SA_KEY` - The content of the service account JSON key file

### Set up Secrets in Google Cloud Secret Manager

Create the following secrets in Google Cloud Secret Manager:

```bash
# For each required secret:
echo -n "your-secret-value" | gcloud secrets create SECRET_NAME --data-file=-

# Required secrets:
# WHATSAPP_API_TOKEN
# WHATSAPP_PHONE_NUMBER_ID
# WHATSAPP_BUSINESS_ACCOUNT_ID
# OPENAI_API_KEY
# GCP_PROJECT_ID
# PINECONE_API_KEY
# PINECONE_ENVIRONMENT
# PINECONE_INDEX_NAME
```

For each secret, grant the service account access:

```bash
gcloud secrets add-iam-policy-binding SECRET_NAME \
    --member="serviceAccount:github-deploy@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

## Deployment

### Manual Deployment

You can trigger deployment manually from the GitHub Actions tab of your repository.

### Automatic Deployment

The workflow is configured to deploy automatically when you push to the `main` branch.

## Customization

### Environment Variables

You can customize the environment variables in the `.github/workflows/deploy-to-cloud-run.yml` file.

### Cloud Run Configuration

To modify the Cloud Run service configuration (memory, CPU, concurrency, etc.), edit the `flags` parameter in the workflow file.

## Local Testing

To test the Docker build locally:

```bash
docker build -t whatsapp-ai-billing-bot .
docker run -p 8000:8000 whatsapp-ai-billing-bot
```

## Accessing the Deployed Service

After deployment, you can access your service at the URL provided by Cloud Run:

```
https://whatsapp-ai-billing-bot-xxxxxxxxxxxx-uc.a.run.app
```
