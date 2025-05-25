#  Arsenal FC Stats ETL Pipeline (AWS + PySpark)

##  Overview
This project is a fully modular **ETL pipeline** that extracts, transforms, and loads Arsenal FC’s 2023/24 season statistics using **API-Football**, **PySpark**, and **AWS**.

The goal is to identify trends and performance insights by analyzing match data and automating the pipeline using cloud-native tools.

---

## Project Objectives
- **Extract** Arsenal match data from API-Football
- **Transform** using PySpark (goal diff, averages, trend analysis)
- **Load** into AWS Redshift from Parquet files on S3
- **Automate** the pipeline with modular Python scripts

---

## Tech Stack
- **Python** — scripting and data ingestion
- **PySpark** — transformation and analytics
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
│   ├── transform.py     # PySpark transformation
│   ├── load.py          # Redshift COPY from S3
├── run_etl.py           # Orchestrates the ETL pipeline
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

3. **Set environment variables** in `.env`:
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

---

## Metrics Analyzed
- Average goals (home/away)
- Goal difference trend
- Match outcomes vs. opponent
- (More to come...)

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
