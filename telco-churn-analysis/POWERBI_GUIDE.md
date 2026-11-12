# Power BI Build Guide (about 2.5 to 3 hours)

Requires Power BI Desktop (Windows). Data file: `churn_clean.csv`.

## 1. Load and prepare data (15 min)

1. Home > Get data > Text/CSV > select `churn_clean.csv` > Transform Data.
2. In Power Query, check types: `tenure`, `MonthlyCharges`, `TotalCharges`, `ChurnProbability`, `AddOnCount`, `ChurnFlag` = number; everything else = text. Rename the table to `churn`. Close & Apply.
3. Sort order for bands (so charts don't sort alphabetically): select column `TenureBand` > Column tools > Sort by column > a helper column.
   - Add column (Power Query or DAX): `TenureSort = SWITCH(churn[TenureBand], "0-12 months",1, "13-24 months",2, "25-48 months",3, 4)`
   - Then set `TenureBand` to sort by `TenureSort`. Do the same for `RiskLevel` (Low=1, Medium=2, High=3) and `ChargeBand` (Under 35=1, 35-70=2, 70-90=3, Over 90=4).

## 2. DAX measures (create in a table called `_Measures`)

```
Total Customers = COUNTROWS(churn)

Churned Customers = CALCULATE([Total Customers], churn[Churn] = "Yes")

Churn Rate % = DIVIDE([Churned Customers], [Total Customers])

Monthly Revenue = SUM(churn[MonthlyCharges])

Monthly Revenue Lost = CALCULATE([Monthly Revenue], churn[Churn] = "Yes")

Revenue Lost % = DIVIDE([Monthly Revenue Lost], [Monthly Revenue])

Avg Tenure (months) = AVERAGE(churn[tenure])

Avg Monthly Charge = AVERAGE(churn[MonthlyCharges])

High Risk Active Customers =
CALCULATE([Total Customers], churn[RiskLevel] = "High", churn[Churn] = "No")

Revenue At Risk =
CALCULATE([Monthly Revenue], churn[RiskLevel] = "High", churn[Churn] = "No")

Churn Rate vs Overall =
[Churn Rate %] - CALCULATE([Churn Rate %], ALL(churn))
```

Format `Churn Rate %`, `Revenue Lost %` as percentage (1 decimal); revenue measures as currency or whole numbers.

## 3. Page 1: Overview

- **Cards (top row):** Total Customers, Churn Rate %, Monthly Revenue Lost, Revenue Lost %.
- **Clustered column:** axis `Contract`, values `Churn Rate %`. Sort descending.
- **Column chart:** axis `TenureBand`, values `Churn Rate %`.
- **Donut or bar:** axis `InternetService`, values `Churn Rate %`.
- **Slicers:** `SeniorCitizen`, `InternetService`, `gender`, `Partner`.
- **Text box takeaway** (use your own wording from the data): month-to-month customers in their first year are the biggest churn pocket.

## 4. Page 2: Drivers

- **Bar chart:** `PaymentMethod` vs `Churn Rate %`.
- **Matrix (heatmap):** rows `TenureBand`, columns `InternetService`, values `Churn Rate %`. Conditional formatting > Background colour > colour scale (low = light, high = dark). The 0-12 month fibre cell should stand out at 69.9%.
- **Matrix:** rows `TechSupport`, columns `OnlineSecurity`, values `Churn Rate %`. Add a visual-level filter `InternetService` is not "No".
- **Decomposition tree:** Analyze = `Churned Customers` (or `ChurnFlag` sum), Explain by = `Contract`, `InternetService`, `PaymentMethod`, `TenureBand`, `TechSupport`.
- **Scatter:** x `tenure`, y `MonthlyCharges`, legend `Churn` (optional).

## 5. Page 3: At-Risk Customers

- **Cards:** High Risk Active Customers, Revenue At Risk.
- **Table:** `customerID`, `Contract`, `tenure`, `MonthlyCharges`, `ChurnProbability`.
  - Visual-level filters: `Churn` = No, `RiskLevel` = High.
  - Sort by `MonthlyCharges` descending. Data bars on `ChurnProbability`.
- **Bar chart:** count of customers by `RiskLevel`.
- **Drill-through:** create a hidden page "Customer Detail" with `customerID` in its drill-through field, then right-click a row on this page to drill through.

## 6. Polish (30 min)

- Consistent theme (View > Themes), one accent colour for churn.
- Titles that state the point, e.g. "Month-to-month contracts churn at 42.7%".
- Align and size visuals using View > Gridlines, Snap to grid.
- Add a page navigator or buttons (Insert > Buttons > Navigator > Page navigator).
- Check the slicers filter every visual (Format > Edit interactions).

## 7. Publish and document

- Save as `telco_churn_dashboard.pbix`.
- Take PNG screenshots of each page (File > Export > PDF also works) into `screenshots/`.
- Push the whole folder to GitHub. Optional: publish to the web if your account allows it, and link it from your resume.

## Sanity checks before you screenshot

These numbers should match the cards and charts: 7,043 customers, 26.5% churn rate, month-to-month 42.7%, one-year 11.3%, two-year 2.8%, fibre optic 41.9%, electronic check 45.3%.
