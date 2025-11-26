resource "aws_dynamodb_table" "link_table" {
  name         = "Delibird-${var.environment}-DelibirdLinkTable"
  billing_mode = "PAY_PER_REQUEST"

  deletion_protection_enabled = true

  hash_key  = "domain"
  range_key = "slug"

  attribute {
    name = "domain"
    type = "S"
  }

  attribute {
    name = "slug"
    type = "S"
  }
}
