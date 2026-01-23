import pandas as pd
import numpy as np
import json

class DataValidator:
    @staticmethod
    def validate_applications(df):
        """Validates application data according to business rules."""
        flags = []
        
        # Valid installation types
        valid_types = {'solar_pv', 'solar_battery', 'heat_pump'}
        
        for idx, row in df.iterrows():
            row_flags = {}
            
            # 1. Unique and Non-null application_id
            if pd.isna(row['application_id']):
                row_flags['id_missing'] = True
            if df['application_id'].duplicated().iloc[idx]:
                row_flags['id_duplicate'] = True
            
            # 2. Loan amount must be positive
            if row['loan_amount_eur'] <= 0:
                row_flags['negative_loan_amount'] = True
            
            # 3. Credit Score (300-850)
            score = row['credit_score']
            if pd.isna(score) or score < 300 or score > 850:
                row_flags['credit_score_out_of_range'] = True
            
            # 4. Postal Code (German 5-digit)
            pc = str(row['postal_code']).strip()
            if not (pc.isdigit() and len(pc) == 5):
                row_flags['invalid_postal_code'] = True
            
            # 5. Installation Type be one of: solar_pv, solar_battery, heat_pump
            if row['installation_type'] not in valid_types:
                row_flags['invalid_installation_type'] = True
                
            # 6. System Size (must be positive if not null)
            if pd.notna(row['system_size_kwp']) and row['system_size_kwp'] <= 0:
                row_flags['invalid_system_size'] = True

            flags.append(json.dumps(row_flags) if row_flags else "{}")
            
        df['data_quality_flags'] = flags
        return df
    

    @staticmethod
    def validate_lms(lms_df, app_df):
        """Validates LMS updates against existing applications."""
        flags = []
        approved_app_ids = set(app_df['application_id'].unique())
        
        # Convert dates to datetime for comparison
        lms_df['disbursement_date'] = pd.to_datetime(lms_df['disbursement_date'], errors='coerce')
        
        # We need original loan amounts for balance checks
        orig_amounts = app_df.set_index('application_id')['loan_amount_eur'].to_dict()

        for idx, row in lms_df.iterrows():
            row_flags = {}
            
            # 1. Unique loan_id
            if lms_df['loan_id'].duplicated().iloc[idx]:
                row_flags['duplicate_loan_id'] = True
            
            # 2. Valid application link
            if row['application_id'] not in approved_app_ids:
                row_flags['unlinked_application'] = True
            
            # 3. Current balance <= Original loan amount
            orig_amt = orig_amounts.get(row['application_id'], float('inf'))
            if row['current_balance_eur'] > orig_amt:
                row_flags['balance_exceeds_original'] = True
                
            flags.append(json.dumps(row_flags) if row_flags else "{}")
            
        lms_df['lms_quality_flags'] = flags
        return lms_df
