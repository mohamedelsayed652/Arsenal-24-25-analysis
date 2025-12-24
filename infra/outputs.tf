output "s3_bucket_name" {
  description = "Name of the S3 bucket storing ETL parquet outputs."
  value       = aws_s3_bucket.etl_data.bucket
}

output "s3_parquet_path" {
  description = "Convenience path to point S3_PARQUET_PATH at."
  value       = "s3://${aws_s3_bucket.etl_data.bucket}/processed/arsenal_stats.parquet"
}

output "redshift_iam_role_arn" {
  description = "IAM role ARN Redshift uses to COPY from S3."
  value       = aws_iam_role.redshift_copy_role.arn
}

output "redshift_workgroup_endpoint" {
  description = "JDBC endpoint for the Redshift Serverless workgroup."
  value       = aws_redshiftserverless_workgroup.this.endpoint
}

output "redshift_database" {
  description = "Database name inside the Redshift namespace."
  value       = var.redshift_db_name
}
