terraform {
  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
     google = {
      source = "hashicorp/google"
      version = "~>7.7.0"
    }
  }
}

provider "github" {
  token = var.github_token
  owner = "vinaymavi"
}

provider "google" {
  project = var.gcp_project_id
  region = var.gcp_zone_india  
}