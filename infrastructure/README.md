# Infrastructure

This folder contains Terraform configuration and helper scripts used to provision infrastructure for the project.

## Purpose

Keep Terraform configuration, backend setup and environment helper scripts in this folder. Use these steps to export environment variables (from `.env`) and run Terraform safely.

## Prerequisites

- macOS (instructions use zsh)
- Terraform installed (v1.0+ recommended)
- Appropriate cloud provider credentials configured (AWS/GCP/Azure) if required by the Terraform modules in this repo
- A `.env` file placed in this directory with the required variables. Do NOT commit secrets or credentials to git.

## Step 1 — Export environment variables

The repository includes a helper script `init_env.sh` that exports variables from the `.env` file into your current shell session.

Important: you must source the script (not run it) so the variables are exported into your current shell environment.

From the `infrastructure` directory run:

```bash
# from repo root
cd infrastructure

# edit .env as needed, do not commit secrets
# export variables into the current shell session
source ./init_env.sh
```

Notes:
- The script prints each line as it exports it. It ignores blank lines and lines starting with `#`.
- For Terraform variable injection make sure `.env` uses the `TF_VAR_` prefix for any Terraform input variables you want to supply via environment variables (for example `TF_VAR_project_id=my-project`).

## Basic Terraform workflow

After exporting environment variables (Step 1):

```bash
# initialize the working directory (downloads providers, sets up backend)
terraform init

# optional: format your HCL files
terraform fmt

# validate configuration
terraform validate

# create an execution plan (review carefully)
terraform plan -out=tfplan

# apply the plan (interactive approval unless you pass -auto-approve)
terraform apply "tfplan"

# later, to tear down
terraform destroy
```

If you prefer to pass variable files instead of environment variables, create a `.tfvars` file and use `-var-file=secrets.tfvars` with `terraform plan`/`apply`.

## Backend and state

This repository uses a Terraform backend (see `backend.tf`). Ensure any backend-specific environment variables or credentials are set before running `terraform init`.

## Security and best practices

- Do not commit `.env` or any secrets. Add them to your personal vault or CI secrets store.
- Use `TF_VAR_` environment variables or `.tfvars` files for sensitive values; prefer environment-based secrets in CI.
- Lock provider versions and keep your Terraform binary updated.

## Troubleshooting

- "terraform: command not found" — install Terraform and ensure it is on your PATH.
- Backend init errors — verify cloud credentials and network access.
- Variable not set in Terraform — confirm that variables in `.env` are prefixed with `TF_VAR_` or use a `.tfvars` file.
- If the script doesn't export variables, ensure you used `source ./init_env.sh` (not `./init_env.sh`).

## Files of interest

- `init_env.sh` — helper to export variables from `.env` into the current shell session
- `.env` — environment variables (contains secrets; keep locally)
- `backend.tf`, `main.tf`, `variables.tf`, `outputs.tf` — Terraform configuration files

## What's provisioned by Terraform

This Terraform configuration provisions:

### GitHub Resources
- Repository settings and environment configuration
- Environment variables and secrets for GitHub Actions

### Google Cloud Resources
- **Artifact Registry**: Docker image repository with retention policy
- **Service Accounts**: Cloud Run deployer and Eventarc trigger service accounts with appropriate IAM roles
- **Workload Identity**: Federation between GitHub Actions and GCP
- **Cloud Storage**: Bucket for Celery worker files (7-day TTL)
- **Firestore**: Database for chat history and processed messages
- **Pub/Sub**: Celery message queue topic
- **Eventarc Trigger**: Pub/Sub to Cloud Run trigger for event-driven Celery task processing

### Cloud Run Pub/Sub Trigger

The infrastructure includes an Eventarc trigger that connects Pub/Sub (Celery message queue) to your Cloud Run service:

- **Pub/Sub Topic**: `celery` topic for task queue
- **Eventarc Trigger**: Automatically invokes Cloud Run endpoint when messages are published
- **Service Account**: Dedicated service account with invoker and subscriber permissions

This enables event-driven processing where Celery tasks published to Pub/Sub automatically trigger your Cloud Run service endpoint.

For detailed information about the Pub/Sub trigger setup, see [../docs/CLOUD_RUN_PUBSUB_TRIGGER.md](../docs/CLOUD_RUN_PUBSUB_TRIGGER.md).

If you'd like, I can also:

- add an `.env.example` template that lists required variables (without secrets), or
- add a small Makefile or convenience scripts to wrap `source` + `terraform` commands.
