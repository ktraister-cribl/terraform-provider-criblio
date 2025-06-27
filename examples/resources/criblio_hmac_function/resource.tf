resource "criblio_hmac_function" "my_hmacfunction" {
  description       = "...my_description..."
  group_id          = "...my_group_id..."
  header_expression = "...my_header_expression..."
  header_name       = "...my_header_name..."
  id                = "...my_id..."
  lib               = "cribl"
  string_builders = [
    "..."
  ]
  string_delim = "...my_string_delim..."
}