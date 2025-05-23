resource "criblio_commit" "my_commit" {
  effective = true
  files = [
    "..."
  ]
  group   = "...my_group..."
  message = "...my_message..."
}