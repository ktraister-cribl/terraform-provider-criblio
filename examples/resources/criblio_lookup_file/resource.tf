resource "criblio_lookup_file" "my_lookupfile" {
  group_id = "...my_group_id..."
  id       = "...my_id..."
  lookup_file_input1 = {
    description = "...my_description..."
    file_info = {
      filename = "...my_filename..."
    }
    id   = "...my_id..."
    mode = "disk"
    size = 3.57
    tags = "...my_tags..."
  }
  lookup_file_input2 = {
    content     = "...my_content..."
    description = "...my_description..."
    id          = "...my_id..."
    mode        = "disk"
    size        = 5.1
    tags        = "...my_tags..."
  }
}