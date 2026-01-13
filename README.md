#  Arsenal FC Stats ETL Pipeline (AWS + PySpark)

##  Overview
This project is a fully modular **ETL pipeline** that extracts, transforms, and loads Arsenal FC’s 2023/24 season statistics using **API-Football**, **PySpark/Parquet**, and **AWS**.

The goal is to identify trends and performance insights by analyzing match data and automating the pipeline using cloud-native tools.

---

## Project Objectives
- **Extract** Arsenal match data from API-Football
- **Transform** using pandas (goal diff, rolling averages, trend analysis)
- **Load** into AWS Redshift from Parquet files on S3 (optional)
- **Automate** the pipeline with modular Python scripts

---

## Tech Stack
- **Python** — scripting and data ingestion
- **PySpark** — default transformation engine
- **pandas** — alternative local transformation path
- **pyarrow** — Parquet writing
- **AWS S3** — data lake storage (parquet format)
- **AWS Redshift** — structured data warehouse
- **boto3** — AWS SDK for Python
- **dotenv** — secure secrets management
- *(Optional: Streamlit or Tableau for dashboards)*

---

## Folder Structure

```
arsenal-etl-dashboard/
├── etl/
│   ├── extract.py       # API data extraction
│   ├── transform.py     # pandas transformation (writes Parquet locally or to S3)
│   ├── load.py          # Redshift COPY from S3
│   ├── transform_spark.py # Spark transformation (default path)
├── run_etl.py           # Orchestrates the ETL pipeline (extract -> transform -> load)
├── transform_data.py    # Run only the transform step on an existing CSV
├── .env                 # Environment variables (not committed)
├── requirements.txt     # Python dependencies
├── README.md            # You're here
```

---

## How to Run

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure AWS credentials**
   ```bash
   aws configure
   ```

3. **Set environment variables** in `.env` (see `.env.example`):
   ```
   API_FOOTBALL_KEY=your_api_key
   REDSHIFT_DB=your_db
   REDSHIFT_USER=your_user
   REDSHIFT_PASSWORD=your_password
   REDSHIFT_HOST=your_redshift_host
   REDSHIFT_PORT=5439
   REDSHIFT_IAM_ROLE=your_redshift_iam_role
   S3_PARQUET_PATH=s3://your-bucket-name/processed/arsenal_stats.parquet
   ```

4. **Run the pipeline**
   ```bash
   python run_etl.py
   ```
   - Spark transform runs by default. Set `USE_PANDAS=true` if you need the pandas path locally.
   - If `S3_PARQUET_PATH` is not set to an `s3://` path, the pipeline will run extract + transform and skip the Redshift load step.
   - To run only the transform step on an existing CSV (Spark by default), use:
     ```bash
     python transform_data.py --input arsenal_matches.csv --output arsenal_avg_goals.parquet
     ```
     Add `--engine pandas` to use pandas instead.

## Infrastructure (Terraform)
- The `infra/` folder provisions an S3 bucket, IAM role for Redshift COPY, and a Redshift Serverless namespace/workgroup.
- Requirements: Terraform >= 1.3, AWS credentials with permissions for S3, IAM, and Redshift Serverless.
- Quick start:
  ```bash
  cd infra
  terraform init
  terraform apply -var="s3_bucket_name=your-unique-bucket-name"
  ```
  Outputs include `s3_parquet_path`, `redshift_iam_role_arn`, and the Redshift endpoint to plug into your `.env`.
 - Optional Lake Formation/Glue registration: set `-var="enable_lakeformation=true"` and adjust `glue_catalog_db` if desired (requires LF permissions).
 - Spectrum external schema: see `sql/external_schema.sql` to create an external schema/table over the S3 Parquet data.

---

## Testing & Validation
- Install dev dependencies (already in `requirements.txt`): `pytest`, `pandera`.
- Run tests: `pytest`
- Data schema validation runs inside `run_transformation`; failures raise with details on offending columns/values.

---

## Metrics Analyzed
- Average goals (home/away)
- Goal difference trend
- Match outcomes vs. opponent
- Rolling 5-match averages for goals and goal diff

---

## Data Model & SQL
- Data model: `docs/data_model.md`
- DDL and sample views: `schema.sql`
- Sample analytical queries: `sql/usage_queries.sql`

---

## Future Enhancements
- Streamlit-based dashboard
- Redshift/Athena query explorer
- Real-time event tracking
- ML model for match outcome prediction

---

## Notes
- Requires AWS Free Tier or credentials with S3 + Redshift access
- API-Football is rate-limited under the free tier
