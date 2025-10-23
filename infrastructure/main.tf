resource "github_repository" "github_repo" {
  name          = "whatsapp-ai-billing-bot"                                        # Exact repo name  
  description   = "WhatsApp AI Billing Bot: Revolutionize Your Invoice Management" # Matches current description
  visibility    = "public"                                                         # Repo is public
  auto_init     = false                                                            # Repo already exists, so no initialization needed
  has_issues    = true                                                             # Issues are enabled (default GitHub setting)
  has_projects  = true                                                             # No projects enabled (based on repo)
  has_wiki      = true
  has_downloads = true # No wiki enabled (based on repo)
  topics        = ["fastapi", "whatsapp-bot", "ai"]
}

resource "github_repository_environment" "test" {
  repository  = github_repository.github_repo.name
  environment = "test"
}

# Non-sensitive environment variables
resource "github_actions_environment_variable" "test_ENVIRONMENT" {
  repository    = github_repository.github_repo.name
  environment   = github_repository_environment.test.environment
  variable_name = "ENVIRONMENT"
  value         = var.test_env_vars.ENVIRONMENT
}

resource "github_actions_environment_variable" "test_WHATSAPP_PHONE_NUMBER_ID" {
  repository    = github_repository.github_repo.name
  environment   = github_repository_environment.test.environment
  variable_name = "WHATSAPP_PHONE_NUMBER_ID"
  value         = var.test_env_vars.WHATSAPP_PHONE_NUMBER_ID
}

resource "github_actions_environment_variable" "test_WHATSAPP_BUSINESS_ACCOUNT_ID" {
  repository    = github_repository.github_repo.name
  environment   = github_repository_environment.test.environment
  variable_name = "WHATSAPP_BUSINESS_ACCOUNT_ID"
  value         = var.test_env_vars.WHATSAPP_BUSINESS_ACCOUNT_ID
}

resource "github_actions_environment_variable" "test_OPENAI_MODEL" {
  repository    = github_repository.github_repo.name
  environment   = github_repository_environment.test.environment
  variable_name = "OPENAI_MODEL"
  value         = var.test_env_vars.OPENAI_MODEL
}

resource "github_actions_environment_variable" "test_GCP_PROJECT_ID" {
  repository    = github_repository.github_repo.name
  environment   = github_repository_environment.test.environment
  variable_name = "GCP_PROJECT_ID"
  value         = var.test_env_vars.GCP_PROJECT_ID
}

resource "github_actions_environment_variable" "test_GCP_LOCATION" {
  repository    = github_repository.github_repo.name
  environment   = github_repository_environment.test.environment
  variable_name = "GCP_LOCATION"
  value         = var.test_env_vars.GCP_LOCATION
}

resource "github_actions_environment_variable" "test_GCP_STORAGE_BUCKET" {
  repository    = github_repository.github_repo.name
  environment   = github_repository_environment.test.environment
  variable_name = "GCP_STORAGE_BUCKET"
  value         = var.test_env_vars.GCP_STORAGE_BUCKET
}

resource "github_actions_environment_variable" "test_LANGCHAIN_TRACING_V2" {
  repository    = github_repository.github_repo.name
  environment   = github_repository_environment.test.environment
  variable_name = "LANGCHAIN_TRACING_V2"
  value         = tostring(var.test_env_vars.LANGCHAIN_TRACING_V2)
}

resource "github_actions_environment_variable" "test_FIRESTORE_COLLECTION_CHAT_HISTORY" {
  repository    = github_repository.github_repo.name
  environment   = github_repository_environment.test.environment
  variable_name = "FIRESTORE_COLLECTION_CHAT_HISTORY"
  value         = var.test_env_vars.FIRESTORE_COLLECTION_CHAT_HISTORY
}

resource "github_actions_environment_variable" "test_FIRESTORE_COLLECTION_PROCESSED_MESSAGES" {
  repository    = github_repository.github_repo.name
  environment   = github_repository_environment.test.environment
  variable_name = "FIRESTORE_COLLECTION_PROCESSED_MESSAGES"
  value         = var.test_env_vars.FIRESTORE_COLLECTION_PROCESSED_MESSAGES
}

resource "github_actions_environment_variable" "test_PINECONE_INDEX_NAME" {
  repository    = github_repository.github_repo.name
  environment   = github_repository_environment.test.environment
  variable_name = "PINECONE_INDEX_NAME"
  value         = var.test_env_vars.PINECONE_INDEX_NAME
}

resource "github_actions_environment_variable" "test_TEMP_FILE_PATH" {
  repository    = github_repository.github_repo.name
  environment   = github_repository_environment.test.environment
  variable_name = "TEMP_FILE_PATH"
  value         = var.test_env_vars.TEMP_FILE_PATH
}

resource "github_actions_environment_variable" "test_JWT_ALGORITHM" {
  repository    = github_repository.github_repo.name
  environment   = github_repository_environment.test.environment
  variable_name = "JWT_ALGORITHM"
  value         = var.test_env_vars.JWT_ALGORITHM
}

resource "github_actions_environment_variable" "test_JWT_ACCESS_TOKEN_EXPIRE_MINUTES" {
  repository    = github_repository.github_repo.name
  environment   = github_repository_environment.test.environment
  variable_name = "JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
  value         = tostring(var.test_env_vars.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
}

resource "github_actions_environment_variable" "test_DEBUG" {
  repository    = github_repository.github_repo.name
  environment   = github_repository_environment.test.environment
  variable_name = "DEBUG"
  value         = tostring(var.test_env_vars.DEBUG)
}

resource "github_actions_environment_variable" "test_LOG_LEVEL" {
  repository    = github_repository.github_repo.name
  environment   = github_repository_environment.test.environment
  variable_name = "LOG_LEVEL"
  value         = var.test_env_vars.LOG_LEVEL
}

resource "github_actions_environment_variable" "test_API_HOST" {
  repository    = github_repository.github_repo.name
  environment   = github_repository_environment.test.environment
  variable_name = "API_HOST"
  value         = var.test_env_vars.API_HOST
}

resource "github_actions_environment_variable" "test_API_PORT" {
  repository    = github_repository.github_repo.name
  environment   = github_repository_environment.test.environment
  variable_name = "API_PORT"
  value         = tostring(var.test_env_vars.API_PORT)
}

# Sensitive secrets
resource "github_actions_environment_secret" "test_WEBHOOK_TOKEN" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  secret_name     = "WEBHOOK_TOKEN"
  plaintext_value = var.test_env_vars.WEBHOOK_TOKEN
}

resource "github_actions_environment_secret" "test_WHATSAPP_API_TOKEN" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  secret_name     = "WHATSAPP_API_TOKEN"
  plaintext_value = var.test_env_vars.WHATSAPP_API_TOKEN
}

resource "github_actions_environment_secret" "test_OPENAI_API_KEY" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  secret_name     = "OPENAI_API_KEY"
  plaintext_value = var.test_env_vars.OPENAI_API_KEY
}

resource "github_actions_environment_secret" "test_GCP_CREDENTIALS_PATH" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  secret_name     = "GCP_CREDENTIALS_PATH"
  plaintext_value = var.test_env_vars.GCP_CREDENTIALS_PATH
}


resource "github_actions_environment_secret" "test_LANGCHAIN_API_KEY" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  secret_name     = "LANGCHAIN_API_KEY"
  plaintext_value = var.test_env_vars.LANGCHAIN_API_KEY
}

resource "github_actions_environment_secret" "test_PINECONE_API_KEY" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  secret_name     = "PINECONE_API_KEY"
  plaintext_value = var.test_env_vars.PINECONE_API_KEY
}

resource "github_actions_environment_secret" "test_JWT_SECRET_KEY" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  secret_name     = "JWT_SECRET_KEY"
  plaintext_value = var.test_env_vars.JWT_SECRET_KEY
}


# Google cloud 

resource "google_artifact_registry_repository" "gcp_docker_repo" {
  description   = "GCP cloud docker registry"
  location      = var.gcp_zone_india
  repository_id = var.gcp_docker_repo_name
  format        = "DOCKER"
  labels = {
    env       = "dev"
    team      = "devops"
    terraform = "true"
  }
}


resource "google_service_account" "cloudrun_deployer" {
  account_id   = var.sa_cloudrun_deployer
  display_name = "Cloud Run Deployer Service Account"
  description  = "Deploys to Cloud Run & pushes images to Artifact Registry"
}

# Create Workload Identity Pool
resource "google_iam_workload_identity_pool" "github_pool_1" {
  workload_identity_pool_id = "github-actions-pool-1"
  display_name              = "GitHub Actions Pool"
  description               = "Pool for GitHub Actions to impersonate cloudrun-deployer-sa"
}

# Create GitHub OIDC Provider
resource "google_iam_workload_identity_pool_provider" "github_provider" {
  workload_identity_pool_provider_id = "github-provider"
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_pool_1.workload_identity_pool_id
  display_name                       = "GitHub Actions Provider"
  attribute_mapping = {
    "google.subject"             = "assertion.sub"
    "attribute.actor"            = "assertion.actor"
    "attribute.aud"              = "assertion.aud"
    "attribute.repository"       = "assertion.repository"
    "attribute.repository_owner" = "assertion.repository_owner"
  }
  attribute_condition = "attribute.repository == '${var.git_hub_owner}/${github_repository.github_repo.name}' && attribute.repository_owner == '${var.git_hub_owner}'"
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

#  Grant Artifact Registry Writer (for pushing Docker images)
resource "google_project_iam_member" "sa_artifact_onpush_admin" {
  project = var.gcp_project_id
  role    = "roles/artifactregistry.createOnPushRepoAdmin"
  member  = "serviceAccount:${google_service_account.cloudrun_deployer.email}"
}

# Grant Artifact Registry Writer (for pushing Docker images)
resource "google_project_iam_member" "sa_artifact_admin" {
  project = var.gcp_project_id
  role    = "roles/artifactregistry.admin"
  member  = "serviceAccount:${google_service_account.cloudrun_deployer.email}"
}

# 3. Grant Cloud Run Developer (for deploying services)
resource "google_project_iam_member" "sa_cloudrun_developer" {
  project = var.gcp_project_id
  role    = "roles/run.developer"
  member  = "serviceAccount:${google_service_account.cloudrun_deployer.email}"
}


# 4. (Optional but recommended) Grant Cloud Build Service Account User
# This lets Cloud Build use this SA during deployments
resource "google_project_iam_member" "sa_cloudbuild_user" {
  project = var.gcp_project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.cloudrun_deployer.email}"
}

# 5. Allow the Cloud Run Deployer SA to act as the Default Compute SA
resource "google_service_account_iam_member" "cloudrun_deployer_act_as_compute" {
  service_account_id = data.google_service_account.compute_default.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.cloudrun_deployer.email}"
}

resource "google_service_account_iam_member" "github_act_as_deployer" {
  service_account_id = google_service_account.cloudrun_deployer.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_pool_1.name}/*"
}

# GCS bucket with ttl 

resource "google_storage_bucket" "chabot-celery-files" {
  name     = "${var.gcp_project_id}-chabot-celery-files"
  location = var.gcp_zone_india
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 7
    }
  }
}
# Github Environment Variables for GCP

#  GCP workload identity pool name
resource "github_actions_environment_variable" "test_GCP_WLIP_GITHUB_PROVIDER" {
  repository    = github_repository.github_repo.name
  environment   = github_repository_environment.test.environment
  variable_name = "GCP_WLIP_GITHUB_PROVIDER"
  value         = google_iam_workload_identity_pool_provider.github_provider.name
}

# GCP service account email
resource "github_actions_environment_variable" "test_GCP_SA_EMAIL" {
  repository    = github_repository.github_repo.name
  environment   = github_repository_environment.test.environment
  variable_name = "GCP_SA_EMAIL"
  value         = google_service_account.cloudrun_deployer.email
}

# GCP docker registry name
resource "github_actions_environment_variable" "test_GCP_DOCKER_REGISTRY_URI" {
  repository    = github_repository.github_repo.name
  environment   = github_repository_environment.test.environment
  variable_name = "GCP_DOCKER_REGISTRY_URI"
  value         = google_artifact_registry_repository.gcp_docker_repo.registry_uri
}

resource "google_project_service" "firestore_api" {
  project            = var.gcp_project_id
  service            = "firestore.googleapis.com"
  disable_on_destroy = false
}

resource "google_firestore_database" "default" {
  project     = var.gcp_project_id
  name        = "(default)"
  location_id = var.gcp_zone_india
  type        = "FIRESTORE_NATIVE"

  depends_on = [google_project_service.firestore_api]
}

resource "google_firestore_field" "celery_ttl" {
  project    = var.gcp_project_id
  database   = google_firestore_database.default.name
  collection = "celery"
  field      = "expires_at"
  ttl_config {
  }
}
