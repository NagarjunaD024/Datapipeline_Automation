import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from src.Data_Transformation import DataTransformer

# 1. Test individual logic for Risk Categories
def test_get_risk_category():
    transformer = DataTransformer()
    assert transformer.get_risk_category(800) == "Excellent"
    assert transformer.get_risk_category(720) == "Good"
    assert transformer.get_risk_category(680) == "Fair"
    assert transformer.get_risk_category(500) == "Poor"
    assert transformer.get_risk_category(np.nan) == "Unknown"

# 2. Test individual logic for Delinquency Buckets
def test_get_delinquency_bucket():
    transformer = DataTransformer()
    assert transformer.get_delinquency_bucket(0) == "Current"
    assert transformer.get_delinquency_bucket(15) == "Late"
    assert transformer.get_delinquency_bucket(45) == "Delinquent"
    assert transformer.get_delinquency_bucket(120) == "Default"
    assert transformer.get_delinquency_bucket(None) == "Current"

# 3. Test the full Application Transformation (Cleaning & LTI)
def test_transform_applications():
    # Setup dummy data
    data = {
        'customer_email': [' KUNDE@example.DE ', 'user@TEST.com'],
        'credit_score': [720, 500],
        'loan_amount_eur': [15000, 10000],
        'annual_income_eur': [60000, 0] # Test division by zero
    }
    df = pd.DataFrame(data)
    
    transformed_df = DataTransformer.transform_applications(df)
    
    # Check email cleaning
    assert transformed_df['customer_email'].iloc[0] == 'kunde@example.de'
    
    # Check Risk Category assignment
    assert transformed_df['risk_category'].iloc[0] == 'Good'
    
    # Check Loan-to-Income Ratio
    assert transformed_df['loan_to_income_ratio'].iloc[0] == 0.25 # 15000 / 60000
    assert np.isnan(transformed_df['loan_to_income_ratio'].iloc[1]) # 10000 / 0 should be NaN

# 4. Test the Portfolio Join and Balance Logic
def test_create_portfolio_view():
    # Setup Apps
    app_data = {
        'application_id': ['APP001'],
        'loan_amount_eur': [20000]
    }
    app_df = pd.DataFrame(app_data)
    
    # Setup LMS
    lms_data = {
        'application_id': ['APP001'],
        'disbursement_date': ['2024-01-01'],
        'current_balance_eur': [15000],
        'days_past_due': [0]
    }
    lms_df = pd.DataFrame(lms_data)
    
    portfolio = DataTransformer.create_portfolio_view(app_df, lms_df)
    
    # Check if the join happened
    assert len(portfolio) == 1
    
    # Check Estimated Balance (should take current balance from LMS)
    assert portfolio['estimated_remaining_balance'].iloc[0] == 15000
    
    # Test fallback: what if LMS is missing for an app?
    app_only_data = {'application_id': ['APP002'], 'loan_amount_eur': [5000]}
    app_only_df = pd.DataFrame(app_only_data)
    empty_lms = pd.DataFrame(columns=['application_id', 'disbursement_date', 'current_balance_eur', 'days_past_due'])
    
    portfolio_fallback = DataTransformer.create_portfolio_view(app_only_df, empty_lms)
    # Should use the original loan amount since LMS info is missing
    assert portfolio_fallback['estimated_remaining_balance'].iloc[0] == 5000