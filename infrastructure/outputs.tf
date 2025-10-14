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