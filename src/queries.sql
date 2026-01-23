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