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
  value = {
    id   = google_artifact_registry_repository.gcp_docker_repo.id
    name = google_artifact_registry_repository.gcp_docker_repo.name
    uri  = google_artifact_registry_repository.gcp_docker_repo.registry_uri
  }
}

output "gcp_sa_deployer" {
  value = google_service_account.cloudrun_deployer.email
}

output "gcp_federation_pool" {
  value = google_iam_workload_identity_pool.github_pool_1.name
}

output "gcp_federation_provider" {
  value = google_iam_workload_identity_pool_provider.github_provider.name
}