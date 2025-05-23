terraform {
  required_providers {
    criblio = {
      source = "criblio/criblio"
    }
  }
}

provider "criblio" {
  # Configuration options
  #server_url ="https://app.cribl-playground.cloud/organizations/beautiful-nguyen-y8y4azd/workspaces/main/app/api/v1"
}

resource "criblio_pack" "my_pack" {
  id           = "pack-from-source"
  group_id     = "default"
  description  = "Pack from source"
  disabled     = true
  display_name = "Pack from source"
  source       = "file:/opt/cribl_data/failover/groups/default/default/HelloPacks"
  version      = "1.0.0"
  
}

# Output the pack details to see the read-only attributes
output "pack_details" {
  value = criblio_pack.my_pack
} 