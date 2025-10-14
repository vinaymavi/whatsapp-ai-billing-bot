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
  repository = github_repository.github_repo.name
  environment = "test"
}

# Non-sensitive environment variables
resource "github_actions_environment_variable" "test_ENVIRONMENT" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  variable_name   = "ENVIRONMENT"
  value           = var.test_env_vars.ENVIRONMENT
}

resource "github_actions_environment_variable" "test_WHATSAPP_PHONE_NUMBER_ID" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  variable_name   = "WHATSAPP_PHONE_NUMBER_ID"
  value           = var.test_env_vars.WHATSAPP_PHONE_NUMBER_ID
}

resource "github_actions_environment_variable" "test_WHATSAPP_BUSINESS_ACCOUNT_ID" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  variable_name   = "WHATSAPP_BUSINESS_ACCOUNT_ID"
  value           = var.test_env_vars.WHATSAPP_BUSINESS_ACCOUNT_ID
}

resource "github_actions_environment_variable" "test_OPENAI_MODEL" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  variable_name   = "OPENAI_MODEL"
  value           = var.test_env_vars.OPENAI_MODEL
}

resource "github_actions_environment_variable" "test_GCP_PROJECT_ID" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  variable_name   = "GCP_PROJECT_ID"
  value           = var.test_env_vars.GCP_PROJECT_ID
}

resource "github_actions_environment_variable" "test_GCP_LOCATION" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  variable_name   = "GCP_LOCATION"
  value           = var.test_env_vars.GCP_LOCATION
}

resource "github_actions_environment_variable" "test_GCP_STORAGE_BUCKET" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  variable_name   = "GCP_STORAGE_BUCKET"
  value           = var.test_env_vars.GCP_STORAGE_BUCKET
}

resource "github_actions_environment_variable" "test_LANGCHAIN_TRACING_V2" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  variable_name   = "LANGCHAIN_TRACING_V2"
  value           = tostring(var.test_env_vars.LANGCHAIN_TRACING_V2)
}

resource "github_actions_environment_variable" "test_FIRESTORE_COLLECTION_CHAT_HISTORY" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  variable_name   = "FIRESTORE_COLLECTION_CHAT_HISTORY"
  value           = var.test_env_vars.FIRESTORE_COLLECTION_CHAT_HISTORY
}

resource "github_actions_environment_variable" "test_FIRESTORE_COLLECTION_PROCESSED_MESSAGES" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  variable_name   = "FIRESTORE_COLLECTION_PROCESSED_MESSAGES"
  value           = var.test_env_vars.FIRESTORE_COLLECTION_PROCESSED_MESSAGES
}

resource "github_actions_environment_variable" "test_PINECONE_INDEX_NAME" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  variable_name   = "PINECONE_INDEX_NAME"
  value           = var.test_env_vars.PINECONE_INDEX_NAME
}

resource "github_actions_environment_variable" "test_TEMP_FILE_PATH" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  variable_name   = "TEMP_FILE_PATH"
  value           = var.test_env_vars.TEMP_FILE_PATH
}

resource "github_actions_environment_variable" "test_JWT_ALGORITHM" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  variable_name   = "JWT_ALGORITHM"
  value           = var.test_env_vars.JWT_ALGORITHM
}

resource "github_actions_environment_variable" "test_JWT_ACCESS_TOKEN_EXPIRE_MINUTES" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  variable_name   = "JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
  value           = tostring(var.test_env_vars.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
}

resource "github_actions_environment_variable" "test_DEBUG" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  variable_name   = "DEBUG"
  value           = tostring(var.test_env_vars.DEBUG)
}

resource "github_actions_environment_variable" "test_LOG_LEVEL" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  variable_name   = "LOG_LEVEL"
  value           = var.test_env_vars.LOG_LEVEL
}

resource "github_actions_environment_variable" "test_API_HOST" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  variable_name   = "API_HOST"
  value           = var.test_env_vars.API_HOST
}

resource "github_actions_environment_variable" "test_API_PORT" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  variable_name   = "API_PORT"
  value           = tostring(var.test_env_vars.API_PORT)
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

resource "github_actions_environment_secret" "test_GOOGLE_APPLICATION_CREDENTIALS" {
  repository      = github_repository.github_repo.name
  environment     = github_repository_environment.test.environment
  secret_name     = "GOOGLE_APPLICATION_CREDENTIALS"
  plaintext_value = var.test_env_vars.GOOGLE_APPLICATION_CREDENTIALS
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