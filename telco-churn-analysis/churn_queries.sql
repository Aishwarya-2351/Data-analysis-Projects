-- Telco churn: SQL analysis (MySQL syntax; tested on the same data in SQLite)
-- Load churn_clean.csv into a table named churn first:
--   CREATE DATABASE telco; USE telco;
--   then use MySQL Workbench > Table Data Import Wizard on churn_clean.csv (table name: churn)

-- 1. Overall churn rate and revenue at risk
SELECT COUNT(*)                                        AS customers,
       SUM(ChurnFlag)                                  AS churned,
       ROUND(100 * AVG(ChurnFlag), 1)                  AS churn_rate_pct,
       ROUND(SUM(CASE WHEN ChurnFlag = 1 THEN MonthlyCharges END), 0) AS monthly_revenue_lost,
       ROUND(100 * SUM(CASE WHEN ChurnFlag = 1 THEN MonthlyCharges END) / SUM(MonthlyCharges), 1) AS pct_of_monthly_revenue
FROM churn;

-- 2. Churn rate by contract type
SELECT Contract,
       COUNT(*)                        AS customers,
       ROUND(100 * AVG(ChurnFlag), 1)  AS churn_rate_pct
FROM churn
GROUP BY Contract
ORDER BY churn_rate_pct DESC;

-- 3. Churn by tenure band and internet service (two-way breakdown)
SELECT TenureBand, InternetService,
       COUNT(*)                        AS customers,
       ROUND(100 * AVG(ChurnFlag), 1)  AS churn_rate_pct
FROM churn
GROUP BY TenureBand, InternetService
HAVING COUNT(*) >= 100
ORDER BY churn_rate_pct DESC;

-- 4. Do protective add-ons reduce churn? (tech support / online security)
SELECT TechSupport, OnlineSecurity,
       COUNT(*)                        AS customers,
       ROUND(100 * AVG(ChurnFlag), 1)  AS churn_rate_pct
FROM churn
WHERE InternetService <> 'No'
GROUP BY TechSupport, OnlineSecurity
ORDER BY churn_rate_pct DESC;

-- 5. Payment method ranking with a window function
SELECT PaymentMethod,
       ROUND(100 * AVG(ChurnFlag), 1)                              AS churn_rate_pct,
       RANK() OVER (ORDER BY AVG(ChurnFlag) DESC)                  AS risk_rank
FROM churn
GROUP BY PaymentMethod;

-- 6. Highest-value at-risk customers still active (retention call list)
SELECT customerID, Contract, tenure, MonthlyCharges, ChurnProbability
FROM churn
WHERE ChurnFlag = 0
  AND RiskLevel = 'High'
ORDER BY MonthlyCharges DESC, ChurnProbability DESC
LIMIT 20;
