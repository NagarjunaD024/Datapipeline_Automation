import pandas as pd
import numpy as np
from datetime import datetime

class DataTransformer:
    @staticmethod
    def get_risk_category(score):
        if pd.isna(score): return "Unknown"
        if score >= 750: return "Excellent"
        if score >= 700: return "Good"
        if score >= 650: return "Fair"
        return "Poor"

    @staticmethod
    def get_delinquency_bucket(dpd):
        if pd.isna(dpd) or dpd <= 0: return "Current"
        if dpd <= 30: return "Late"
        if dpd <= 90: return "Delinquent"
        return "Default"

    @classmethod
    def transform_applications(cls, df):
        """Applies cleaning and adds derived application fields."""
        df = df.copy()
        
        # Standardize email
        df['customer_email'] = df['customer_email'].str.strip().str.lower()
        
        # Risk Category
        df['risk_category'] = df['credit_score'].apply(cls.get_risk_category)
        
        # Loan to Income Ratio
        # Handle division by zero or NaN income
        df['loan_to_income_ratio'] = np.where(
            df['annual_income_eur'] > 0,
            df['loan_amount_eur'] / df['annual_income_eur'],
            np.nan
        )
        
        df['processed_at'] = datetime.now()
        return df

    @classmethod
    def create_portfolio_view(cls, app_df, lms_df):
        """Joins apps and LMS and adds performance metrics."""
        # Ensure we only use the latest LMS update per application (if duplicates exist)
        lms_latest = lms_df.sort_values('disbursement_date').drop_duplicates('application_id', keep='last')
        
        portfolio = pd.merge(
            app_df, 
            lms_latest, 
            on='application_id', 
            how='left', 
            suffixes=('', '_lms')
        )
        
        # Delinquency Bucket
        portfolio['delinquency_bucket'] = portfolio['days_past_due'].apply(cls.get_delinquency_bucket)
        
        # Months since disbursement
        today = pd.to_datetime(datetime.now())
        portfolio['disbursement_date'] = pd.to_datetime(portfolio['disbursement_date'])
        portfolio['months_since_disbursement'] = (
            (today.year - portfolio['disbursement_date'].dt.year) * 12 + 
            (today.month - portfolio['disbursement_date'].dt.month)
        )
        
        # Estimated remaining balance
        portfolio['estimated_remaining_balance'] = portfolio['current_balance_eur'].fillna(portfolio['loan_amount_eur'])
        
        return portfolio