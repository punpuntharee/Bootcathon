import streamlit as st
import numpy as np
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, timedelta

def load_and_filter_data(filepath, start, end):
    df = pd.read_csv(filepath)
    df['DATE'] = pd.to_datetime(df['DATE'], dayfirst=True)
    start_date = pd.to_datetime(start)
    end_date = pd.to_datetime(end)
    mask = (df['DATE'] >= start_date) & (df['DATE'] <= end_date)
    return df[mask]

def plot_net_out_kt(df_filtered):
    daily_last_rows = df_filtered.sort_values(['DATE']).drop_duplicates('DATE', keep='last')
    daily_last_rows['NET_OUT_KT'] = daily_last_rows['NET_OUT_MT'] / 1000
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(daily_last_rows['DATE'], daily_last_rows['NET_OUT_KT'], marker='o', label='Net Out (KT)')
    ax.axhline(y=58, color='red', linestyle='--', label='Max Capacity (58 KT)')
    ax.set_title('Daily Net Out (Last Row per Day) in KT')
    ax.set_xlabel('Date')
    ax.set_ylabel('Total Quality')
    ax.set_xticks(daily_last_rows['DATE'])
    ax.set_xticklabels(daily_last_rows['DATE'].dt.strftime('%Y-%m-%d'), rotation=45)
    ax.set_ylim(0, 70)
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    return fig 

def show_net_out_summary(df_filtered):
    daily_last_rows = df_filtered.sort_values(['DATE']).drop_duplicates('DATE', keep='last')
    if daily_last_rows.empty:
        st.warning("No Net Out In This Time")
        return
    daily_last_rows['NET_OUT_KT'] = daily_last_rows['NET_OUT_MT'] / 1000
    latest_row = daily_last_rows.tail(1)  
    net_out_kt = latest_row['NET_OUT_KT'].values[0]  
    max_capacity = 58.0
    used = net_out_kt
    remaining = max_capacity - used
    st.subheader("📊 Net Out Summary")
    st.write(f"Used: **{used:.2f} KT**")
    st.write(f"Remaining: **{remaining:.2f} KT**")
    st.write(f"Total capacity: **{max_capacity:.2f} KT**")


def group_small_slices(series, threshold=0.01):
    total = series.sum()
    frac = series / total
    large = series[frac >= threshold]
    small = series[frac < threshold]
    if small.sum() > 0:
        large['Others'] = small.sum()
    return large

def group_small_slices(series, threshold=0.01):
    total = series.sum()
    frac = series / total
    large = series[frac >= threshold].copy()
    small = series[frac < threshold]
    if small.sum() > 0:
        large['Others'] = small.sum()
    return large

def plot_material_summary(df_filtered):
    if df_filtered.empty:
        st.warning("❌ No data available in the selected range.")
        return None
    inbound_sum = df_filtered.groupby('MATERIAL_NAME')['INBOUND'].sum() / 1000
    outbound_sum = df_filtered.groupby('MATERIAL_NAME')['OUTBOUND'].sum() / 1000

    summary_df = pd.DataFrame({
        'INBOUND_KT': inbound_sum,
        'OUTBOUND_KT': outbound_sum
    }).fillna(0).round(2)
    st.write("📊 **Material Summary (in KT)**")
    st.dataframe(summary_df.sort_values(by='OUTBOUND_KT', ascending=False))

    inbound_grouped = group_small_slices(inbound_sum, threshold=0.01)
    outbound_grouped = group_small_slices(outbound_sum, threshold=0.01)

    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    axes[0].pie(inbound_grouped, labels=inbound_grouped.index, autopct='%1.1f%%', startangle=140)
    axes[0].set_title('Inbound Material Share (KT)')
    axes[1].pie(outbound_grouped, labels=outbound_grouped.index, autopct='%1.1f%%', startangle=140)
    axes[1].set_title('Outbound Material Share (KT)')
    fig.tight_layout()
    return fig

def get_net_stock_on(date):
    log_df = pd.read_csv("stock_flow_2.csv")
    log_df['DATE'] = pd.to_datetime(log_df['DATE'], dayfirst=True)
    initial_stock = pd.read_csv("CHINA_inventory.csv")
    initial_stock = initial_stock[['MATERIAL_NAME', 'TOTAL_UNRESTRICTED_STOCK']]
    initial_stock = initial_stock.rename(columns={'TOTAL_UNRESTRICTED_STOCK': 'AFTER'})
    initial_stock = initial_stock.dropna().drop_duplicates(subset='MATERIAL_NAME', keep='first')
    date = pd.to_datetime(date)  
    df = log_df[log_df['DATE'] <= date]
    df_sorted = df.sort_values(by=['MATERIAL_NAME', 'DATE'], ascending=[True, False])
    latest_after = (
        df_sorted.dropna(subset=['AFTER'])
        .drop_duplicates(subset='MATERIAL_NAME', keep='first')
        [['MATERIAL_NAME', 'AFTER']]
    )

    merged = pd.merge(
        latest_after,
        initial_stock,
        on='MATERIAL_NAME',
        how='outer',
        suffixes=('_log', '_init')
    )

    merged['NET(MT)'] = merged['AFTER_log'].combine_first(merged['AFTER_init'])
    merged['NET(MT)'] = merged['NET(MT)'].fillna(0)
    return merged[['MATERIAL_NAME', 'NET(MT)']].drop_duplicates().sort_values(by='NET(MT)').reset_index(drop=True)

def find_outnound_of_material(df_filtered, material, amount):
    filtered = df_filtered[df_filtered['MATERIAL_NAME'] == material]
    outbound_sum = filtered['OUTBOUND'].sum()
    sale = amount - outbound_sum
    st.write("---")
    if sale < 0:
        st.markdown(f"### ✅ Surpassed the sales target by {abs(sale):,.0f} units.")
    elif sale > 0:
        st.markdown(f"### 📦 Need to sell **{sale:,.0f} more units** to reach the target.")
    return outbound_sum

def hot_material(df_filtered):
    outbound_sum = df_filtered.groupby('MATERIAL_NAME')['OUTBOUND'].sum().sort_values(ascending=False)
    hot_product = outbound_sum.head(10)
    for i, (material_name, outbound_value) in enumerate(hot_product.items(), start=1):
        if outbound_value > 0:
            st.markdown(f"#### {i}. {material_name} — outbound: {outbound_value:.2f}")

def result_of_balance(df_filtered):
    df_sorted = df_filtered.sort_values(by='DATE', ascending=False)
    selected_columns = df_sorted[['DATE', 'MATERIAL_NAME', 'AFTER']]
    result = selected_columns.groupby('MATERIAL_NAME', as_index=False).first()
    result = result.rename(columns={'AFTER': 'BALANCE'})
    plot_stock_balance(result)

def plot_stock_balance(merged_df):
    negative_df = merged_df[merged_df['BALANCE'] < 0].copy()

    top5_df = merged_df.sort_values(by='BALANCE', ascending=False).head(5).copy()

    st.subheader("🔴 Materials with Negative Balance")
    if not negative_df.empty:
        for _, row in negative_df.iterrows():
            st.markdown(f"- **{row['MATERIAL_NAME']}**: {row['BALANCE']:.3f}")
    else:
        st.markdown("_No materials have a negative balance._")

    st.subheader("🔝 Top 5 Materials by Balance")
    for _, row in top5_df.iterrows():
        st.markdown(f"- **{row['MATERIAL_NAME']}**: {row['BALANCE']:.3f}")

    fig, ax = plt.subplots(figsize=(14, 8))
    bars = ax.barh(merged_df['MATERIAL_NAME'], merged_df['BALANCE'], color='skyblue')

    for bar, val in zip(bars, merged_df['BALANCE']):
        if val < 0:
            bar.set_color('salmon')

    ax.axvline(0, color='gray', linewidth=0.8)
    ax.set_title("Stock Balance per Material", fontsize=16)
    ax.set_xlabel("Balance", fontsize=14)
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=3)
    ax.grid(axis='x', linestyle='--', alpha=0.5)

    plt.tight_layout()
    st.pyplot(fig)

#------------Main--------------------

option = st.selectbox(
    "Select Option",
    ("Hot Material","Report","Check Stock","Check Target Amount"),index=None
)
if option == "Report" :
    jan_start = date(2024, 1, 1)
    jan_end = date(2024, 1, 31)
    date = st.selectbox(
    "Select Range",
    ("Custom Range","Month","Week","Day"),index=None
)
    if date == "Custom Range" :
        col1, col2 = st.columns([1,1])
        with col1:
            start = st.date_input("Start date", min_value=jan_start, max_value=jan_end, value=None)
        with col2:
            end = st.date_input("End date", min_value=start, max_value=jan_end, value=None)
        if start and end:
            df_filtered = load_and_filter_data("stock_flow_2.csv", start, end)
            st.pyplot(plot_net_out_kt(df_filtered))
            st.pyplot(plot_material_summary(df_filtered))

    elif date == "Month" :
        df_filtered = load_and_filter_data("stock_flow_2.csv", jan_start, jan_end)
        st.pyplot(plot_net_out_kt(df_filtered))
        st.pyplot(plot_material_summary(df_filtered))

    elif date == "Week":
        start = None
        min_to_select = datetime.date(2024, 1, 7)
        end = st.date_input("End date", min_value=min_to_select, max_value=jan_end, value=None)
        if end:
            start = end - timedelta(days=6)
        if start and end:
            df_filtered = load_and_filter_data("stock_flow_2.csv", start, end)
            st.pyplot(plot_net_out_kt(df_filtered))
            st.pyplot(plot_material_summary(df_filtered))

    elif date == "Day" :
        day = st.date_input("Select date", min_value=jan_start, max_value=jan_end, value=None)
        if day:
            df_filtered = load_and_filter_data("stock_flow_2.csv", day, day)
            show_net_out_summary(df_filtered)
            st.pyplot(plot_material_summary(df_filtered))


elif option == "Check Stock" :
    jan_start = date(2024, 1, 1)
    jan_end = date(2024, 1, 31)
    date = st.date_input("Select date", min_value=jan_start, max_value=jan_end, value=None)
    if date:
        df_filtered = load_and_filter_data("stock_flow_2.csv",jan_start,date)
        result_of_balance(df_filtered)
        st.write(get_net_stock_on(date))


elif option == "Check Target Amount" :
    jan_start = date(2024, 1, 1)
    jan_end = date(2024, 1, 31)

    col1, col2 ,col3= st.columns([1,1,1])
    df = pd.read_csv("CHINA_inventory.csv")
    name_of_material = df['MATERIAL_NAME']

    with col1:
        material = st.selectbox(
    "Select Material",
    (name_of_material),
    index=None,
    placeholder="Select Material...",
)
    with col2:
        date = st.date_input("Select date", min_value=jan_start, max_value=jan_end, value=None)
    with col3:
        amount = st.number_input("Enter the amount (MT)", min_value=0, step=1)
    
    if material and date and amount :
        df_filtered = load_and_filter_data("stock_flow_2.csv", jan_start, jan_end)
        outBount = find_outnound_of_material(df_filtered,material,amount)

elif option == "Hot Material":
    jan_start = date(2024, 1, 1)
    jan_end = date(2024, 1, 31)
    start = None
    min_to_select = datetime.date(2024, 1, 7)
    end = st.date_input("Select date", min_value=min_to_select, max_value=jan_end, value=None)
    if end:
        start = end - timedelta(days=6)
        df_filtered = load_and_filter_data("stock_flow_2.csv",start,end)
        material = hot_material(df_filtered)

st.markdown("""
---
<div style='text-align: center; font-size: 12px; color: gray;'>
    By เลิกกั๊กแล้วรักก่อนนะเตง ❤️
</div>
""", unsafe_allow_html=True)

