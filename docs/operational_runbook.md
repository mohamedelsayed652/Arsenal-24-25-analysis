# Operational Runbook (Local & Dev)

## Prereqs
- Python 3.10+
- AWS credentials (S3 + Redshift Serverless + IAM)
- API-Football key
- Terraform >= 1.3 (for infra)

## Local Env
1) `cp .env.example .env` and fill in values.
2) `pip install -r requirements.txt`
3) `python run_etl.py`
   - Spark transform runs by default; set `USE_PANDAS=true` to use the pandas path locally.
   - If `S3_PARQUET_PATH` is local (no `s3://`), Redshift load is skipped.

## Terraform (no deploy yet)
- `cd infra && terraform init`
- `terraform plan -var="s3_bucket_name=your-unique-bucket"`
- Apply only when ready.

## Data Quality Checks
- Pandera validation runs inside `run_transformation`; failures raise with column/type context.
- Tests: `pytest` (uses small in-memory fixtures).

## Troubleshooting
- Extraction failures: check `API_FOOTBALL_KEY`, network, and API quota.
- S3 upload failures: verify AWS creds and bucket name/region.
- Redshift load failures: confirm `S3_PARQUET_PATH` is s3://, IAM role has S3 Get/List, and Redshift can assume it.
