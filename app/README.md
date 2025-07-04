# 🏭 Stock Monitoring Dashboard (CHINA_inventory)

A Streamlit web application for visualizing and monitoring stock movement (inbound, outbound, and balance) of various materials from **CHINA_inventory**. This dashboard helps track stock flow trends, detect negative balances, and analyze sales targets effectively.

---

## 📦 Features

### 1. **Report**
Visualize stock movement in different time ranges:
- **Custom Range**: Choose any start and end date
- **Month**: View stock flow throughout January 2024
- **Week**: View stock flow for any 7-day period
- **Day**: View daily stock and summary

Includes:
- 📈 Line chart of net out in KT per day
- 🧮 Pie charts of inbound/outbound material shares
- 📊 Table summary of top materials

---

### 2. **Check Stock**
- View **net stock balance** of each material as of a selected date (based on `CHINA_inventory.csv` and `stock_flow_2.csv`)

---

### 3. **Check Target Amount**
- Select material and sales target (in MT)
- Compare actual outbound amount with the target
- Displays whether the target has been met or how many more units are needed

---

### 4. **Hot Material**
- Lists top 10 materials with the **highest outbound amount** during the selected week

---

### 5. **Stock Balance per Material**
- Visual summary of materials’ current balances
- Highlights:
  - 🚨 Materials with **negative balance**
  - 🥇 Top 5 materials by balance
  - 📊 Horizontal bar chart for easy comparison

---

## 🗂️ File Requirements

Make sure these CSV files are in the same directory as the Streamlit app:

- `stock_flow_2.csv` – contains daily log of stock changes
- `CHINA_inventory.csv` – contains initial stock data

---

## ▶️ Getting Started

### Install dependencies

```bash
pip install streamlit pandas matplotlib
