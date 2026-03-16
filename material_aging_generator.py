import pandas as pd
import numpy as np
from datetime import date, timedelta
import random

# ─────────────────────────────────────────
# 1. MASTER DATA
# ─────────────────────────────────────────

random.seed(42)
np.random.seed(42)

TODAY = date(2026, 3, 13)

# Material catalog
materials = [
    # (Code, Description, Product Type, Material Type, UoM)
    ("PR", "Componente para Refrigerador", "Raw Material",       "Partes para Refrigeradores", "PC"),
    ("PL", "Componente para Lavadora",     "Raw Material",       "Partes para Lavadoras",      "PC"),
    ("R",  "Resina",                        "Raw Material",       "Resina",                     "KG"),
    ("A",  "Acero",                         "Raw Material",       "Acero",                      "PC"),
    ("PQ", "Producto Quimico",              "Raw Material",       "Productos Quimicos",         "KG"),
    ("TE", "Tarjeta Electronica",           "Semi Ensamble",      "Tarjetas Electronicas",      "PC"),
    ("PI", "Parte Inyectada",               "Semi Ensamble",      "Partes Inyectadas",          "PC"),
    ("RF", "Refrigerador",                  "Producto Terminado", "Refrigeradores",             "PC"),
    ("LV", "Lavadora",                      "Producto Terminado", "Lavadoras",                  "PC"),
]

# How many SKUs per material type
N_PER_TYPE = 15

# ─────────────────────────────────────────
# 2. GENERATE INVENTORY RECORDS
#    Each SKU can have multiple batch entries
#    (simulates real SAP stock layers)
# ─────────────────────────────────────────

records = []

for prefix, desc, prod_type, mat_type, uom in materials:
    for i in range(1, N_PER_TYPE + 1):
        mat_code = f"{prefix}-{str(i).zfill(5)}"
        mat_desc = f"{desc} {str(i).zfill(5)}"

        # Each SKU has 1-4 batch layers with different input dates
        n_batches = random.randint(1, 4)
        for _ in range(n_batches):
            # Spread dates: some very old, some recent — realistic aging mix
            days_ago = int(np.random.choice(
                [
                    random.randint(0,  30),   # fresh
                    random.randint(31, 60),   # mild
                    random.randint(61, 90),   # moderate
                    random.randint(91, 120),  # aged
                    random.randint(121, 365), # critical
                ],
                p=[0.30, 0.25, 0.20, 0.15, 0.10]
            ))
            input_date = TODAY - timedelta(days=days_ago)

            # Quantities and amounts vary by type
            if uom == "KG":
                qty = round(random.uniform(100, 5000), 2)
                unit_cost = round(random.uniform(5, 50), 2)
            else:
                qty = random.randint(10, 10000)
                unit_cost = round(random.uniform(10, 500), 2)

            amt = round(qty * unit_cost, 2)

            records.append({
                "Material Code":    mat_code,
                "Material Desc":    mat_desc,
                "Product Type":     prod_type,
                "Material Type":    mat_type,
                "UoM":              uom,
                "Qty":              qty,
                "Amt":              amt,
                "Input Date":       input_date,
            })

df = pd.DataFrame(records)

# ─────────────────────────────────────────
# 3. CALCULATE AGING
# ─────────────────────────────────────────

df["Input Date"] = pd.to_datetime(df["Input Date"])
TODAY_TS = pd.Timestamp(TODAY)
df["Days in Stock"] = (TODAY_TS - df["Input Date"]).dt.days

def aging_band(days):
    if days <= 30:   return "0-30"
    elif days <= 60: return "31-60"
    elif days <= 90: return "61-90"
    elif days <= 120: return "91-120"
    else:            return "121+"

df["Aging Band"] = df["Days in Stock"].apply(aging_band)

# ─────────────────────────────────────────
# 4. BUILD FINAL REPORT (pivot by aging band)
# ─────────────────────────────────────────

bands      = ["0-30", "31-60", "61-90", "91-120", "121+"]
group_keys = ["Material Code", "Material Desc", "Product Type", "Material Type", "UoM"]

# Total on-hand (all bands)
totals = (
    df.groupby(group_keys)
    .agg(
        **{"On-Hand Qty": ("Qty", "sum"),
           "On-Hand Amt": ("Amt", "sum")}
    )
    .reset_index()
)

# Qty & Amt per aging band
pivot_qty = (
    df.pivot_table(index=group_keys, columns="Aging Band", values="Qty", aggfunc="sum")
    .fillna(0)
    .rename(columns={b: f"{b} days Qty" for b in bands})
    .reset_index()
)
pivot_amt = (
    df.pivot_table(index=group_keys, columns="Aging Band", values="Amt", aggfunc="sum")
    .fillna(0)
    .rename(columns={b: f"{b} days Amt" for b in bands})
    .reset_index()
)

# Merge everything
report = totals.merge(pivot_qty, on=group_keys).merge(pivot_amt, on=group_keys)

# Order columns logically
ordered_cols = group_keys + ["On-Hand Qty", "On-Hand Amt"]
for b in bands:
    ordered_cols += [f"{b} days Qty", f"{b} days Amt"]
report = report[ordered_cols]

# Round numeric columns
num_cols = [c for c in report.columns if c not in group_keys]
report[num_cols] = report[num_cols].round(2)

# ─────────────────────────────────────────
# 5. SAVE FILES
# ─────────────────────────────────────────

# Raw dataset (for analysis notebooks)
df.to_csv("/mnt/user-data/outputs/material_aging_raw.csv", index=False)

# Final aging report
report.to_csv("/mnt/user-data/outputs/material_aging_report.csv", index=False)

# ─────────────────────────────────────────
# 6. QUICK SUMMARY
# ─────────────────────────────────────────

print("=" * 55)
print("  MATERIAL AGING DATASET — GENERATION COMPLETE")
print("=" * 55)
print(f"\n📦 Total SKUs:              {report.shape[0]}")
print(f"📋 Total inventory records: {df.shape[0]}")
print(f"💰 Total On-Hand Amt:       ${df['Amt'].sum():,.0f}")
print(f"\n📊 Stock distribution by aging band:")
band_summary = df.groupby("Aging Band")["Amt"].sum().reindex(bands)
for band, amt in band_summary.items():
    pct = amt / df["Amt"].sum() * 100
    bar = "█" * int(pct / 2)
    print(f"   {band:>7} days  |{bar:<25}| ${amt:>12,.0f}  ({pct:.1f}%)")
print(f"\n📁 Files saved:")
print(f"   • material_aging_raw.csv    → for Python notebooks")
print(f"   • material_aging_report.csv → final aging report")
print("=" * 55)
