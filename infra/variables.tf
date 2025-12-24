variable "project_name" {
  description = "Prefix used for naming AWS resources."
  type        = string
  default     = "arsenal-etl"
}

variable "aws_region" {
  description = "AWS region to deploy infrastructure."
  type        = string
  default     = "us-east-1"
}

variable "s3_bucket_name" {
  description = "S3 bucket name for Parquet outputs."
  type        = string
}

variable "redshift_namespace" {
  description = "Redshift Serverless namespace name."
  type        = string
  default     = "arsenal-etl-namespace"
}

variable "redshift_workgroup" {
  description = "Redshift Serverless workgroup name."
  type        = string
  default     = "arsenal-etl-workgroup"
}

variable "redshift_db_name" {
  description = "Default database name within the Redshift namespace."
  type        = string
  default     = "dev"
}

variable "redshift_base_capacity" {
  description = "Redshift Serverless base capacity in RPU (between 8 and 512)."
  type        = number
  default     = 8
}
