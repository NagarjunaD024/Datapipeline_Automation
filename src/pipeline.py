import pandas as pd
from src.Data_Validation import DataValidator
from src.Data_Transformation import DataTransformer
import json

def run_pipeline():
    
    # 1. Ingest
    apps_raw = pd.read_csv('src/Data/applications_expanded.csv', on_bad_lines='warn')
    lms_raw = pd.read_csv('src/Data/lms_updates_expanded.csv', on_bad_lines='warn')

    # 2. Validate
    apps_validated = DataValidator.validate_applications(apps_raw)
    lms_validated = DataValidator.validate_lms(lms_raw, apps_validated)
    
    # 3. Transform
    cleaned_apps = DataTransformer.transform_applications(apps_validated)
    loan_portfolio = DataTransformer.create_portfolio_view(cleaned_apps, lms_validated)
    
    # 4. Generate Quality Report
   
    # 1. Count of records processed
    total_processed = len(cleaned_apps)

    # 2. Count of validation failures by type
    all_flags = []
    problematic_ids = []

    for idx, row in cleaned_apps.iterrows():
        flags_dict = json.loads(row['data_quality_flags'])
        
        if flags_dict:  # If there are ANY errors
            all_flags.extend(flags_dict.keys()) # Add the error names to our list
            problematic_ids.append(row['application_id']) # Save the ID of this broken row


    # Create the Summary of Failure Types (This is good for CSV)
    dq_summary = pd.Series(all_flags).value_counts().reset_index()
    dq_summary.columns = ['issue_type', 'failure_count']

    # Create the Full Report (This is best for JSON)
    quality_report = {
        "summary_metrics": {
            "total_records_processed": total_processed,
            "total_problematic_records": len(set(problematic_ids)),
            "overall_health_percentage": round(((total_processed - len(set(problematic_ids))) / total_processed) * 100, 2)
        },
        "failures_by_type": dq_summary.to_dict(orient='records'),
        "problematic_application_ids": list(set(problematic_ids))
    }

    
    # 5. Output
    cleaned_apps.to_csv('src/output/cleaned_applications.csv', index=False)
    loan_portfolio.to_csv('src/output/loan_portfolio.csv', index=False)
    dq_summary.to_csv('src/output/data_quality_summary.csv', index=False)
    with open('src/output/data_quality_report.json', 'w') as f:
        json.dump(quality_report, f, indent=4)
    
    print(f"ETL Pipeline completed. Processed {total_processed} records.")

if __name__ == "__main__":
    run_pipeline()
    
    