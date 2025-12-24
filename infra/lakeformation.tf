variable "enable_lakeformation" {
  description = "Whether to register the S3 location with Lake Formation and create a Glue catalog database."
  type        = bool
  default     = false
}

variable "glue_catalog_db" {
  description = "Glue/Lake Formation database name for external tables."
  type        = string
  default     = "arsenal_etl"
}

data "aws_caller_identity" "current" {}

resource "aws_glue_catalog_database" "this" {
  count = var.enable_lakeformation ? 1 : 0

  name = var.glue_catalog_db
}

resource "aws_lakeformation_resource" "s3_data_location" {
  count = var.enable_lakeformation ? 1 : 0

  arn  = aws_s3_bucket.etl_data.arn
  role_arn = aws_iam_role.redshift_copy_role.arn
  depends_on = [aws_s3_bucket.etl_data]
}
