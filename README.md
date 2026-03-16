# 📦 Material Aging Intelligence System
### From manual Excel reports to automated predictive inventory analysis

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![Pandas](https://img.shields.io/badge/Pandas-2.0-lightblue?logo=pandas)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.3-orange?logo=scikit-learn)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

---

## 🎯 The Problem

In manufacturing operations, aging inventory is one of the most significant — and often silent — threats to profitability. Materials sitting in the warehouse beyond their optimal usage window generate unnecessary capital lock-up, increased risk of obsolescence, and hidden costs that distort actual production cost.

The traditional process to manage this risk looks like this:

1. A weekly SAP extract is pulled manually
2. Two pivot tables are built in Excel
3. Both tables are compared side by side
4. A manager reviews the output and escalates critical cases

**The core problem is timing.** This process only identifies materials that have *already* crossed a critical threshold — at which point the options are limited to emergency subsidiary sales or scrap. There is no forward visibility, and without a detailed tool, escalations are often delayed or missed entirely.

---

## 💡 The Solution

This project replaces the manual Excel workflow with a three-notebook automated system that delivers:

| Notebook | Question answered | Output |
|---|---|---|
| `01_material_aging_exploracion` | What is the current aging status? | Aging dashboard + risk heatmap |
| `02_material_aging_comparativo` | How did it change vs. last week? | Migration matrix + weekly Excel report |
| `03_material_aging_predictivo` | What will happen in the next 30 days? | Prioritized escalation list |

---

## 📊 Key Findings (Sample Dataset)

- **$344M** total inventory value analyzed across 135 SKUs and 9 material types
- **47.8% ($164M)** of total inventory value is currently at risk (>60 days)
- **Zero materials improved** in the comparative week — confirming the problem is systemic, not isolated
- **92 out of 135 materials** will cross a critical threshold in the next 30 days
- **$226M** in projected at-risk value over the next 30-day horizon
- Finished Goods show a **higher aging rate (47.6%) than Raw Materials (38.8%)** — a demand signal inversion that points to a forecasting gap, not a procurement problem

---

## 🗂️ Project Structure

```
material-aging-analysis/
│
├── Data/
│   ├── material_aging_raw.csv          ← Inventory records with Input Date
│   └── material_aging_report.csv       ← Pre-aggregated aging report
│
├── Notebooks/
│   ├── 01_material_aging_exploracion.ipynb
│   ├── 02_material_aging_comparativo.ipynb
│   └── 03_material_aging_predictivo.ipynb
│
├── Outputs/
│   ├── 01_aging_overview.png
│   ├── 02_aging_by_material_type.png
│   ├── 03_aging_by_product_type.png
│   ├── 04_top15_at_risk.png
│   ├── 05_days_distribution.png
│   ├── 06_wow_band_comparison.png
│   ├── 07_migration_analysis.png
│   ├── 08_category_movement.png
│   ├── 09_rule_based_predictions.png
│   ├── 10_random_forest_results.png
│   ├── 11_model_comparison.png
│   ├── 12_escalation_priority.png
│   ├── weekly_aging_report.xlsx        ← Auto-generated weekly report
│   └── 30day_escalation_list.xlsx      ← Predictive escalation output
│
├── material_aging_generator.py         ← Synthetic dataset generator
└── README.md
```

---

## 🔬 Methodology

### Notebook 1 — Exploratory Analysis
- Data quality validation (nulls, duplicates, type consistency)
- Aging band classification: 0-30 / 31-60 / 61-90 / 91-120 / 121+ days
- Financial exposure quantification by band, material type and product tier
- Top 15 at-risk materials ranked by at-risk amount

### Notebook 2 — Week-over-Week Comparison
- Dual snapshot generation (current week vs. previous week)
- Band-level movement analysis with delta in USD and percentage
- Material migration matrix — tracks which materials moved between bands
- Automated classification: 🔴 URGENT / ⚠️ WATCH / ✅ OK
- Auto-export of weekly Excel report replacing manual pivot process

### Notebook 3 — Predictive Model
Two complementary approaches are built and compared:

**Rule-Based Model**
- Deterministic: projects current days in stock + 30 days
- Identifies which threshold (60 / 90 / 120 days) each material will cross
- 100% explainable to non-technical stakeholders
- Generates prioritized escalation list with urgency levels

**Random Forest Classifier**
- 13 features including financial exposure, batch count, material type and proximity to threshold
- Trained on rule-based labels as ground truth
- Key finding: model converged to the same predictions as the rules, confirming that days in stock is the dominant signal in the current dataset
- Feature importance analysis reveals secondary predictors: Total_Amt and Material_Type

**Combined Priority Score**
```
Priority = RF_Probability × 0.4 + Time_Urgency × 0.4 + Financial_Exposure × 0.2
```
This score merges both models and financial risk into a single ranking for the operations manager.

---

## ⚙️ Setup & Usage

### Requirements
```bash
pip install pandas numpy matplotlib seaborn scikit-learn openpyxl
```

### Run order
```bash
# 1. Generate the dataset
python material_aging_generator.py

# 2. Run notebooks in sequence
jupyter notebook Notebooks/01_material_aging_exploracion.ipynb
jupyter notebook Notebooks/02_material_aging_comparativo.ipynb
jupyter notebook Notebooks/03_material_aging_predictivo.ipynb
```

### Update the reference date
In each notebook, update this line to match your current week:
```python
DATE_CURRENT  = pd.Timestamp('YYYY-MM-DD')   # Current week
DATE_PREVIOUS = pd.Timestamp('YYYY-MM-DD')   # Previous week (DATE_CURRENT - 7 days)
```

---

## 🔭 Next Steps & Model Evolution

The current model uses only stock and aging data. The next evolution of this system would incorporate SAP transactional data to significantly increase predictive power:

| Data Source | SAP Module | Value Added |
|---|---|---|
| Open production orders | PP | Distinguish stranded stock from planned consumption |
| Open sales orders | SD | Identify finished goods with confirmed demand |
| Purchase order history | MM | Detect systematic over-purchasing patterns |
| BOM consumption rates | PP/MM | Calculate realistic time-to-consume per material |

With these features, the Random Forest model would be able to detect non-obvious risks that pure time-based rules cannot — materials that look safe by days in stock but have no confirmed consumption path in SAP.

The long-term architecture would run this system as a **weekly automated pipeline**: SAP extract → Python processing → Excel distribution → Looker Studio dashboard, replacing the current manual process end to end.

---

## 🏭 Background

This project was designed and built based on 20 years of SAP inventory management experience in manufacturing operations, spanning ECC 6.0 and S/4HANA environments across MM, SD, PP, CO and WM modules.

The aging bands, escalation thresholds and business rules used in this analysis reflect real operational decisions made in manufacturing environments — not academic assumptions. The problem of undetected aging inventory and delayed escalation is a pattern observed across multiple companies and SAP implementations.

---

## 🛠️ Tech Stack

`Python 3.10` · `Pandas` · `NumPy` · `Matplotlib` · `Seaborn` · `Scikit-learn` · `OpenPyXL`

---

## 📄 License

MIT License — free to use, adapt and build upon.
