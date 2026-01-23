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


