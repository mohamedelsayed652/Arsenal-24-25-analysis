terraform {
  required_version = ">= 1.3.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 bucket to store Parquet outputs from the ETL.
resource "aws_s3_bucket" "etl_data" {
  bucket = var.s3_bucket_name

  tags = {
    Project = "arsenal-etl"
  }
}

resource "aws_s3_bucket_versioning" "etl_data" {
  bucket = aws_s3_bucket.etl_data.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "etl_data" {
  bucket = aws_s3_bucket.etl_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "etl_data" {
  bucket = aws_s3_bucket.etl_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# IAM role Redshift uses to COPY from S3.
data "aws_iam_policy_document" "redshift_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["redshift.amazonaws.com", "redshift-serverless.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "redshift_copy_role" {
  name               = "${var.project_name}-redshift-copy"
  assume_role_policy = data.aws_iam_policy_document.redshift_assume_role.json
}

data "aws_iam_policy_document" "redshift_s3_access" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:ListBucket"
    ]
    resources = [
      aws_s3_bucket.etl_data.arn,
      "${aws_s3_bucket.etl_data.arn}/*"
    ]
  }
}

resource "aws_iam_policy" "redshift_s3_access" {
  name   = "${var.project_name}-redshift-s3-access"
  policy = data.aws_iam_policy_document.redshift_s3_access.json
}

resource "aws_iam_role_policy_attachment" "redshift_s3_access" {
  role       = aws_iam_role.redshift_copy_role.name
  policy_arn = aws_iam_policy.redshift_s3_access.arn
}

# Redshift Serverless namespace and workgroup (optional but useful for end-to-end testing).
resource "aws_redshiftserverless_namespace" "this" {
  namespace_name = var.redshift_namespace
  db_name        = var.redshift_db_name
  iam_roles      = [aws_iam_role.redshift_copy_role.arn]
}

resource "aws_redshiftserverless_workgroup" "this" {
  workgroup_name = var.redshift_workgroup
  namespace_name = aws_redshiftserverless_namespace.this.namespace_name
  base_capacity  = var.redshift_base_capacity

  publicly_accessible = true

  tags = {
    Project = "arsenal-etl"
  }
}
