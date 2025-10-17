variable "github_token" {
  description = "GitHub token with repo and workflow permissions"
  type        = string
}

variable "git_hub_owner" {
  description = "GitHub owner or organization name"
  type        = string
  default     = "vinaymavi"
}

variable "test_env_vars" {
  description = "Test environment variables for Github"
  type = object({
    ENVIRONMENT                             = string
    WEBHOOK_TOKEN                           = string
    WHATSAPP_API_TOKEN                      = string
    WHATSAPP_PHONE_NUMBER_ID                = string
    WHATSAPP_BUSINESS_ACCOUNT_ID            = string
    OPENAI_API_KEY                          = string
    OPENAI_MODEL                            = string
    GCP_PROJECT_ID                          = string
    GCP_LOCATION                            = string
    GCP_CREDENTIALS_PATH                    = string
    GOOGLE_APPLICATION_CREDENTIALS          = string
    GCP_STORAGE_BUCKET                      = string
    LANGCHAIN_API_KEY                       = string
    LANGCHAIN_TRACING_V2                    = bool
    FIRESTORE_COLLECTION_CHAT_HISTORY       = string
    FIRESTORE_COLLECTION_PROCESSED_MESSAGES = string
    PINECONE_API_KEY                        = string
    PINECONE_INDEX_NAME                     = string
    TEMP_FILE_PATH                          = string
    JWT_SECRET_KEY                          = string
    JWT_ALGORITHM                           = string
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES         = number
    DEBUG                                   = bool
    LOG_LEVEL                               = string
    API_HOST                                = string
    API_PORT                                = number
  })
}

# GCP Variables
variable "gcp_project_id" {
  description = "GCP cloud project_id"
}

variable "gcp_project_number" {
  description = "GCP project number"
  type        = string
}

variable "gcp_zone_india" {
  description = "GCP project india zone"
}

variable "gcp_docker_repo_name" {
  description = "GCP docker repository name"
  type        = string
  default     = "whatsapp-chatbot-repo"
}

variable "sa_cloudrun_deployer" {
  description = "GCP service account email"
  type        = string
  default     = "whatsapp-chatbot-deployer"
}