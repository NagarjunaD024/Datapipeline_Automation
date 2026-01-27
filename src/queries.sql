-- 1. Portfolio Overview: Monthly Cohort Analysis

SELECT 
    strftime('%Y-%m', application_date) AS cohort_month,
    installation_type,
    COUNT(application_id) AS total_applications,
    SUM(loan_amount_eur) AS total_loan_volume,
    ROUND(AVG(loan_amount_eur), 2) AS avg_loan_size,
    -- Approval Rate: (Approved Apps / Total Apps)
    ROUND(CAST(COUNT(CASE WHEN status = 'approved' THEN 1 END) AS FLOAT) / COUNT(*), 4) AS approval_rate
FROM cleaned_applications
GROUP BY 1, 2
ORDER BY 1 DESC;


-- 2. Risk Monitoring

SELECT 
    application_id,
    customer_email,
    credit_score,
    loan_to_income_ratio,
    risk_category,
    loan_amount_eur
FROM loan_portfolio 
WHERE credit_score < 680 AND loan_to_income_ratio > 0.35
ORDER BY loan_to_income_ratio DESC;


-- 3. Delinquency Analysis by Installer and Risk Category
-- Purpose: See if specific installer partners are bringing in "bad" customers.
SELECT 
    installer_partner_id,
    COUNT(loan_id) AS total_loans,
    -- Delinquency Rate: Percentage of all loans that are not "Current"
    ROUND(CAST(COUNT(CASE WHEN delinquency_bucket != 'Current' THEN 1 END) AS FLOAT) / COUNT(loan_id), 4) AS delinquency_rate
FROM loan_portfolio
WHERE loan_id IS NOT NULL
GROUP BY 1
ORDER BY delinquency_rate DESC;


-- 4. Performance Tracking: 30/60/90 Day Delinquency Rates
SELECT 
    strftime('%Y-%m', disbursement_date) AS disbursement_cohort,
    COUNT(loan_id) AS cohort_size,
    ROUND(CAST(COUNT(CASE WHEN days_past_due > 30 THEN 1 END) AS FLOAT) / COUNT(*), 4) AS rate_30_plus,
    ROUND(CAST(COUNT(CASE WHEN days_past_due > 60 THEN 1 END) AS FLOAT) / COUNT(*), 4) AS rate_60_plus,
    ROUND(CAST(COUNT(CASE WHEN days_past_due > 90 THEN 1 END) AS FLOAT) / COUNT(*), 4) AS rate_90_plus
FROM loan_portfolio
WHERE disbursement_date IS NOT NULL
GROUP BY 1
ORDER BY 1 DESC;


-- 5. Installer Performance Ranking (Window Function)
-- Purpose: Rank installers by total successful funding volume to identify top partners.
SELECT 
    installer_partner_id,
    installation_type,
    SUM(loan_amount_eur) AS total_funded_amount,
    -- Window Function: Ranks installers by volume within each installation type
    RANK() OVER (
        PARTITION BY installation_type 
        ORDER BY SUM(loan_amount_eur) DESC
    ) AS installer_rank_by_type
FROM loan_portfolio
WHERE status = 'approved' AND loan_id IS NOT NULL
GROUP BY 1, 2;
