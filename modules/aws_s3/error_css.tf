resource "aws_s3_object" "error_css" {
  # アップロード元(ローカル)
  source = "${local.local_base_path}/css/error.css"

  # アップロード先(S3)
  bucket = var.bucket_name
  key    = "${var.remote_base_path}/css/error.css"

  # Content-Type の設定
  content_type = "text/css"

  # エンティティタグ (ファイル更新のトリガーに必要)
  etag = filemd5("${local.local_base_path}/css/error.css")
}

resource "aws_s3_object" "admin_portal_css" {
  # アップロード元(ローカル)
  source = "${local.local_base_path}/css/admin-portal.css"

  # アップロード先(S3)
  bucket = var.bucket_name
  key    = "${var.remote_base_path}/css/admin-portal.css"

  # Content-Type の設定
  content_type = "text/css"

  # エンティティタグ (ファイル更新のトリガーに必要)
  etag = filemd5("${local.local_base_path}/css/admin-portal.css")
}
