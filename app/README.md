# 📦 Stock Flow Dashboard

This Streamlit web application provides insightful visualizations and interactive tools for monitoring stock flow, analyzing material movement, and evaluating sales performance within a selected time frame.

## 🚀 Features

### 📊 Report
Visualize stock movement over custom, daily, weekly, or monthly ranges:
- **Net Out Trend** in kilotons (KT)
- **Material Summary** with inbound/outbound pie charts
- Daily net-out summaries with comparisons to max capacity

### 🧮 Check Stock
Check the latest available stock **per material** as of a selected date:
- View net stock derived from inventory logs
- See balance highlights:
  - 🔴 Negative balances
  - 🔝 Top 5 materials by stock balance
- Horizontal bar chart with color-coded stocks

### 🎯 Check Target Amount
Track how much of a specific material has been sold compared to a target:
- Choose material and input target amount
- See if the sales goal has been met or how much more is needed

### 🔥 Hot Material
Discover the **top 10 most-sold materials** in the last 7 days:
- Ranked list of materials based on outbound volume

---

## 🗂️ File Structure
.
├── app.py # Main Streamlit app

├── stock_flow_2.csv # Stock movement log

├── CHINA_inventory.csv # Initial inventory data

└── README.md # Project documentation

---

## 📁 Data Sources

- `stock_flow_2.csv`: Contains columns such as `DATE`, `MATERIAL_NAME`, `INBOUND`, `OUTBOUND`, `NET_OUT_MT`, and `AFTER`.
- `CHINA_inventory.csv`: Initial stock for each material (`TOTAL_UNRESTRICTED_STOCK`).

---

## 🛠️ Requirements

Install dependencies using:

```bash
pip install -r requirements.txt
```
---

## ▶️ How to Run

```streamlit run app.py```


