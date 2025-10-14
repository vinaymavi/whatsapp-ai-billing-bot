
terraform {
  backend "gcs" {
    prefix = "whatsapp-ai-billing-bot"
    bucket = "vm-terraform-state-file"
  }
}
