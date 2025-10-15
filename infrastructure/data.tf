# Default Compute Service Account
data "google_service_account" "compute_default" {
  account_id = "${var.gcp_project_number}-compute@developer.gserviceaccount.com"
  project    = var.gcp_project_id
}