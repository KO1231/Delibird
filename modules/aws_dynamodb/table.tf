resource "aws_dynamodb_table" "link_table" {
  name         = "Delibird-${var.environment}-DelibirdLinkTable"
  billing_mode = "PAY_PER_REQUEST"

  hash_key  = "slug"
  range_key = "created_at"

  attribute {
    name = "slug"
    type = "S"
  }

  attribute {
    name = "created_at"
    type = "S"
  }
}
