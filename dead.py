import streamlit as st
import pandas as pd

st.set_page_config(page_title="Low Margin Item Analysis", layout="wide")

# --- File path (uploaded file) ---
file_path = "oud mehta sales.Xlsx"  # change if different

# --- Load Excel with no header first ---
df_raw = pd.read_excel(file_path, header=None)

# Find header row dynamically (search for "Item Code")
header_row = df_raw[df_raw.apply(lambda row: row.astype(str).str.contains("Item Code", case=False).any(), axis=1)].index[0]

# Reload with correct header row
df = pd.read_excel(file_path, header=header_row)

# --- Ensure required columns exist ---
required_cols = ["Item Code", "Items", "Qty Sold", "Total Cost", "Total Sales", "Total Profit", "Excise Margin (%)"]

missing = [col for col in required_cols if col not in df.columns]
if missing:
    st.error(f"❌ Missing columns: {missing}")
    st.stop()

# --- Convert to numeric where possible ---
for col in ["Qty Sold", "Total Cost", "Total Sales", "Total Profit", "Excise Margin (%)"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# --- Filter low margin items ---
low_margin = df[df["Excise Margin (%)"] < 5].copy()

# --- Simulate price increases (3% and 4%) ---
for inc in [0.03, 0.04]:
    low_margin[f"Profit +{int(inc*100)}% Price"] = low_margin["Total Profit"] + (low_margin["Total Sales"] * inc)
    low_margin[f"Change in Profit +{int(inc*100)}%"] = low_margin[f"Profit +{int(inc*100)}% Price"] - low_margin["Total Profit"]

st.subheader("📉 Items with < 5% Margin")
st.dataframe(low_margin[[
    "Item Code", "Items", "Qty Sold", "Total Cost", "Total Sales", "Total Profit", "Excise Margin (%)", 
    "Profit +3% Price", "Change in Profit +3%", 
    "Profit +4% Price", "Change in Profit +4%"
]])

# --- Insights ---
total_current_profit = low_margin["Total Profit"].sum()
total_profit_3 = low_margin["Profit +3% Price"].sum()
total_profit_4 = low_margin["Profit +4% Price"].sum()

st.subheader("📊 Insights")
st.write(f"👉 Current Profit from low margin items: **{total_current_profit:,.2f}**")
st.write(f"👉 Profit if price increased by 3%: **{total_profit_3:,.2f}** (Change: {total_profit_3-total_current_profit:,.2f})")
st.write(f"👉 Profit if price increased by 4%: **{total_profit_4:,.2f}** (Change: {total_profit_4-total_current_profit:,.2f})")
