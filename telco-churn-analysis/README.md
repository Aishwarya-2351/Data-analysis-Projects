# Telco Customer Churn Analysis and Power BI Dashboard

End-to-end churn analysis: Python cleaning and modelling, SQL analysis, and a three-page Power BI dashboard that tells a retention team who is leaving, why, and who to call next.

**Dataset:** IBM Telco Customer Churn sample data (7,043 customers, 21 columns). It is a public, simulated dataset, so findings illustrate the method rather than describe a real company.

## Business question

Which customers churn, what drives it, and how much monthly revenue does it cost?

## Method

1. **Clean (Python, Pandas):** converted `TotalCharges` to numeric (11 blank values belonged to customers with tenure 0 and were set to 0), simplified "No internet/phone service" values, and added tenure bands, charge bands, add-on count and an auto-pay flag. No duplicate customer IDs were found.
2. **Explore:** churn rate by contract, tenure, internet service, payment method, add-ons and demographics.
3. **Model:** compared Logistic Regression and Random Forest with a stratified 75/25 split. Both reached a ROC-AUC of about 0.85; Logistic Regression was selected for interpretability. Customers are bucketed into Low / Medium / High risk from its churn probability.
4. **SQL (MySQL):** six queries covering churn by segment, a two-way breakdown, add-on effects, a window-function ranking and a retention call list (`churn_queries.sql`).
5. **Dashboard (Power BI):** three pages, Overview, Drivers and At-Risk Customers (see `POWERBI_GUIDE.md`).

## Key findings

- **26.5%** of customers churned (1,869 of 7,043), taking **30.5%** of monthly revenue with them, because churners pay more on average (74.44 vs 61.27 per month).
- **Contract type is the strongest segment signal:** month-to-month churn is 42.7%, versus 11.3% on one-year and 2.8% on two-year contracts.
- **The first year is the danger zone:** churn is 47.4% in months 0-12 and falls to 9.5% after 48 months. New fibre-optic customers are the worst case, at 69.9%.
- **Fibre optic customers churn at 41.9%**, against 19.0% for DSL.
- **Electronic check users churn at 45.3%**, versus 15.2-16.7% for customers on automatic payments.
- **Support add-ons go with lower churn:** customers with neither tech support nor online security churn at 49.0%; with both, 9.0% (internet customers only). This is an association, not proof that add-ons cause retention.
- **Senior citizens churn at 41.7%**, versus 23.6% for others.

## Recommendations

1. Offer incentives to move month-to-month customers onto one- or two-year contracts, especially in their first year.
2. Run an onboarding programme for new fibre customers and investigate service quality.
3. Encourage automatic payment with a small discount or credit.
4. Bundle tech support and online security into trial offers for customers without them.
5. Use the High-risk list (`churn_queries.sql`, query 6) to prioritise outreach to the highest-paying active customers.

## Limitations

- The risk scores come from a model trained on 75% of the data and applied to all customers, so use them for ranking, not as validated forecasts.
- The data is cross-sectional with no dates, so trends over time cannot be analysed.
- Findings show association only.

## Files

| File | Purpose |
| --- | --- |
| `churn_analysis.py` | Cleaning, EDA, model, export |
| `churn_clean.csv` | Cleaned data with bands, churn probability and risk level (load into Power BI / MySQL) |
| `churn_queries.sql` | SQL analysis |
| `POWERBI_GUIDE.md` | DAX measures and page-by-page dashboard build steps |
| `summary_stats.txt` | Full output of the analysis script |
| `fig_churn_drivers.png` | Quick EDA chart |
| `screenshots/` | Add your dashboard screenshots here |

## How to run

```bash
pip install pandas numpy scikit-learn matplotlib seaborn
python churn_analysis.py Telco-Customer-Churn.csv output/
```
