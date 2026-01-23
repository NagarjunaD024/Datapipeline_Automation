# Datapipeline_Automation
A modular ETL pipeline for automating the validation, transformation, and analysis of green energy loan applications and portfolio performance.

## 🚀 Setup & Execution

Follow these steps to set up the environment and run the data pipeline.

### 1. Clone the Repository
```bash
git clone [YOUR_REPOSITORY_URL]
cd Datapipeline_Automation
```

### 2. Set Up Virtual Environment
```bash
# Create the virtual environment
python3 -m venv .venv

# Activate on Linux/macOS:
source .venv/bin/activate

# Activate on Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the ETL Pipeline
```bash
python -m src.pipeline
```
**Note:** Processed files and the Data Quality Report will be saved in \`src/output/\`.

### 5. Run Automated Tests
```bash
python -m pytest src/tests
```
**Note:** Total number of tests passed is 6.

---

## 📁 Project Structure
- **\`src/Data/\`**: Contains the raw input CSV files (\`applications_expanded.csv\`, \`lms_updates_expanded.csv\`).
- **\`src/output/\`**: Where the pipeline saves the final, cleaned CSVs and the JSON Data Quality Report.
- **\`src/tests/\`**: Contains \`pytest\` scripts to verify transformation logic and validation rules.
- **\`queries.sql\`**: Pre-written SQL queries for monthly cohort analysis, installer rankings, and delinquency tracking.
- **\`requirements.txt\`**: List of required Python packages (Pandas, Numpy, Pytest).

---

## 🛠 Design Decisions & Trade-offs
- **Hybrid Data Handling**: Designed to bridge the gap between real-time **API-driven application data** and **batch-based LMS updates**.
- **Modularity for API Integration**: Logic is encapsulated in classes (\`DataValidator\`, \`DataTransformer\`). This allows rules to be imported directly into a **Django Rest Framework Serializer** for real-time validation.
- **Traceability via JSON Flags**: Instead of deleting rows with errors, I added a \`data_quality_flags\` column. This allows the Risk team to see exactly why an application was flagged without losing data.

## ✅ Data Quality Checks
- **Email Validation**: Strict Regular Expression check to catch illegal characters, tabs, and formatting errors at the source.
- **LMS Integrity**: Cross-checks that \`current_balance_eur\` never exceeds original loan amounts.
- **Robust Ingestion**: Implemented \`on_bad_lines='warn'\` to handle inconsistent CSV exports without halting the automation.

## 🏭 Production Deployment
In a production environment, I would deploy this as follows:
1. **Django rest_framework**: Move validation logic into Serializers to catch errors during API submission.
2. **Celery Task Queue**: Use Celery to process LMS file updates asynchronously to avoid blocking the main application.
3. **Data Warehousing**: Pushing the final \`loan_portfolio\` view to a Read Replica or Snowflake to allow the Risk team to run heavy SQL Analytical queries without impacting the production database performance.

## 📈 Future Improvements
- **Schema Contracts**: Use **Great Expectations** to define strict data contracts with installer partners.
- **Dockerization**: Wrap the pipeline in a Docker container to ensure consistent behavior across different server environments.
- **Incremental Loading**: Move from full-file processing to an "Upsert" logic based on record timestamps.

