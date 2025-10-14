resource "github_repository" "github_repo" {
  name        = "whatsapp-ai-billing-bot"  # Exact repo name  
  description = "WhatsApp AI Billing Bot: Revolutionize Your Invoice Management"  # Matches current description
  visibility  = "public"                   # Repo is public
  auto_init   = false                     # Repo already exists, so no initialization needed
  has_issues  = true                      # Issues are enabled (default GitHub setting)
  has_projects = true                    # No projects enabled (based on repo)
  has_wiki    = true 
  has_downloads = true                    # No wiki enabled (based on repo)
  topics = ["fastapi", "whatsapp-bot", "ai"]
}