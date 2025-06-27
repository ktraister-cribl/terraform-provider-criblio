resource "criblio_group" "my_group" {
  cloud = {
    provider = "azure"
    region   = "...my_region..."
  }
  estimated_ingest_rate = 4.46
  id                    = "...my_id..."
  is_fleet              = false
  name                  = "...my_name..."
  on_prem               = false
  product               = "stream"
  provisioned           = true
  streamtags = [
    "..."
  ]
  worker_remote_access = false
}