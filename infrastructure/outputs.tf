output "github_repo" {
  value = {
    clone_url = github_repository.github_repo.git_clone_url
    name      = github_repository.github_repo.name
  }
}

output "test_env" {
  value = github_repository_environment.test
}

output "test_env_vars" {
  value     = var.test_env_vars
  sensitive = true
}

output "gcp_docker_repo_name" {
  value = google_artifact_registry_repository.gcp_docker_repo
}

output "gcp_sa_deployer" {
  value = google_service_account.cloudrun_deployer.email
}