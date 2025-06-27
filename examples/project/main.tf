terraform {
  required_providers {
    criblio = {
      source = "criblio/criblio"
    }
  }
}

provider "criblio" {
  # Configuration options
}

resource "criblio_project" "my_project" {
  consumers = {
  }
  description = "test project"
  destinations = [
  ]
  group_id = "default"
  id       = "my_project"
  subscriptions = [
  ]
}

output "project" {
  value = criblio_project.my_project
}