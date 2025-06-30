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

resource "criblio_global_var" "my_globalvar" {
  description = "test"
  group_id    = "default"
  id          = "my_globalvar"
  lib         = "test"
  tags        = "test"
  type        = "number"
  value       = 100
}

output "global_var" {
  value = criblio_global_var.my_globalvar
}