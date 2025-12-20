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

resource "aws_dynamodb_table" "link_nonce" {
  name         = "Delibird-${var.environment}-DelibirdLinkNonceTable"
  billing_mode = "PAY_PER_REQUEST"

  deletion_protection_enabled = true

  hash_key = "nonce"

  attribute {
    name = "nonce"
    type = "S"
  }

  ttl {
    attribute_name = "expired_timestamp"
    enabled        = true
  }
}
