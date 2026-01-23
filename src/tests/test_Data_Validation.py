import pytest
import pandas as pd
import json
from src.Data_Validation import DataValidator

# 1. Test Application Validation (Checks all business rules)
def test_validate_applications_logic():
    # Setup a DataFrame with 1 Good row and several Bad rows
    data = {
        'application_id': ['APP_GOOD', 'APP_GOOD', None, 'APP_NEG', 'APP_SCORE', 'APP_ZIP', 'APP_EMAIL'],
        'customer_email': ['test@test.com', 'test@test.com', 'test@test.com', 'test@test.com', 'test@test.com', 'test@test.com', 'bad,email@test.com'],
        'loan_amount_eur': [15000, 15000, 15000, -500, 15000, 15000, 15000],
        'credit_score': [700, 700, 700, 700, 999, 700, 700],
        'postal_code': ['10115', '10115', '10115', '10115', '10115', '123', '10115'],
        'installation_type': ['solar_pv', 'solar_pv', 'solar_pv', 'solar_pv', 'solar_pv', 'solar_pv', 'solar_pv'],
        'system_size_kwp': [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0]
    }
    df = pd.DataFrame(data)
    
    validated_df = DataValidator.validate_applications(df)
    
    # Helper function to get flags as a dict
    def get_flags(row_idx):
        return json.loads(validated_df['data_quality_flags'].iloc[row_idx])

    # Row 0: Should be clean
    assert get_flags(0) == {}

    # Row 1: Duplicate ID check
    assert get_flags(1)['id_duplicate'] is True

    # Row 2: Missing ID check
    assert get_flags(2)['id_missing'] is True

    # Row 3: Negative loan amount
    assert get_flags(3)['negative_loan_amount'] is True

    # Row 4: Credit Score out of range (999)
    assert get_flags(4)['credit_score_out_of_range'] is True

    # Row 5: Invalid Postal Code (too short)
    assert get_flags(5)['invalid_postal_code'] is True

    # Row 6: Invalid Email (the comma trap)
    assert get_flags(6)['invalid_email_format'] is True

# 2. Test LMS Validation (Links between systems)
def test_validate_lms_logic():
    # Setup approved applications
    app_data = {
        'application_id': ['APP001'],
        'loan_amount_eur': [10000]
    }
    app_df = pd.DataFrame(app_data)
    
    # Setup LMS updates
    lms_data = {
        'loan_id': ['LN1', 'LN1'], # Duplicate Loan ID
        'application_id': ['APP001', 'APP_GHOST'], # APP_GHOST doesn't exist in app_df
        'current_balance_eur': [5000, 15000], # Row 1 balance is > original amount
        'disbursement_date': ['2024-01-01', '2024-01-01']
    }
    lms_df = pd.DataFrame(lms_data)
    
    validated_lms = DataValidator.validate_lms(lms_df, app_df)
    
    def get_lms_flags(row_idx):
        return json.loads(validated_lms['lms_quality_flags'].iloc[row_idx])

    # Row 0: Should flag duplicate loan ID (second occurrence)
    assert get_lms_flags(1)['duplicate_loan_id'] is True
    
    # Row 1: Should flag unlinked application
    assert get_lms_flags(1)['unlinked_application'] is True
    
    # Row 1: Balance check (15,000 > 10,000)
    # Note: Even though Row 1 is unlinked, our code uses float('inf') 
    # but let's test a linked one with high balance
    high_balance_data = {
        'loan_id': ['LN3'],
        'application_id': ['APP001'],
        'current_balance_eur': [999999], 
        'disbursement_date': ['2024-01-01']
    }
    hb_df = pd.DataFrame(high_balance_data)
    validated_hb = DataValidator.validate_lms(hb_df, app_df)
    assert json.loads(validated_hb['lms_quality_flags'].iloc[0])['balance_exceeds_original'] is True