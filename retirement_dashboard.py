"""
Carissa Hicks
June 23 2025
For Konvergent Wealth Partners
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title='Client: Kyle Konvergent',layout='wide')

# --- Sidebar Inputs ---
st.sidebar.header("Tools")
include_ss = st.sidebar.checkbox("Include Social Security?", value=False)
if include_ss:
    ss_estimate = st.sidebar.number_input(
        "Estimated Annual Social Security (in today's dollars)", 
        value=30_000, step=1_000
    )
start_age = 55
retirement_age = st.sidebar.slider("Retirement Age", 60, 70, 67)
current_assets_non_qualified = st.sidebar.number_input("Current Non-Qualified Account Balance ($)", value=700_000, step=10_000)
current_assets_401k = st.sidebar.number_input("Current 401(k) Balance ($)", value=500_000, step=10_000)
annual_contribution = st.sidebar.number_input("Annual 401(k) Contribution", value=20_000, step=1_000)
annual_spending = st.sidebar.number_input("Annual Spending (Today)", value=120_000, step=1_000)
inflation_rate = st.sidebar.slider("Inflation Rate (%)", 0.0, 5.0, 3.0) / 100
investment_return = st.sidebar.slider("Investment Return (%)", 0.0, 10.0, 6.0) / 100
tax_rate = st.sidebar.slider("Effective Tax Rate (%)", 0.0, 40.0, 25.0) / 100

# --- Projection Parameters ---
years_until_retirement = retirement_age - start_age
projection_years = list(range(start_age, 101))

# --- Pre-Retirement Growth ---
assets_401k = [current_assets_401k]
assets_non_qualified = [current_assets_non_qualified]

for i in range(1, years_until_retirement + 1):
    new_401k = assets_401k[-1] * (1 + investment_return) + annual_contribution
    new_non_qualified = assets_non_qualified[-1] * (1 + investment_return)
    assets_401k.append(new_401k)
    assets_non_qualified.append(new_non_qualified)

# Merge balances at retirement
total_at_retirement = assets_401k[-1] + assets_non_qualified[-1]
combined_assets = [total_at_retirement]

# --- Retirement Spending Simulation ---
base_retirement_spending = annual_spending * (1 + inflation_rate) ** years_until_retirement

if include_ss:
    ss_income = ss_estimate * (1 + inflation_rate) ** years_until_retirement
    retirement_spending = max(0, base_retirement_spending - ss_income)
else:
    retirement_spending = base_retirement_spending

spending_over_time = [retirement_spending]

for year in range(retirement_age + 1, 101):
    next_spending = spending_over_time[-1] * (1 + inflation_rate)
    gross_withdrawal = next_spending / (1 - tax_rate)
    next_balance = combined_assets[-1] * (1 + investment_return) - gross_withdrawal
    if next_balance <= 0:
        combined_assets.append(0)
        spending_over_time.append(next_spending)
        break
    combined_assets.append(next_balance)
    spending_over_time.append(next_spending)

# --- Output ---
st.markdown("<h1 style='text-align: center;'>Kyle Konvergent's Retirement Projection</h1>", unsafe_allow_html=True)

c1,c2, c3 = st.columns(3)

with c1:
    st.subheader("Projected Asset Growth (Age 55 to " + str(retirement_age) + ")")
    growth_years = list(range(start_age, retirement_age + 1))
    df_growth_phase = pd.DataFrame({
        "Age": growth_years,
        "401(k)": assets_401k,
        "Non-Qualified": assets_non_qualified,
        "Total Portfolio": [a + b for a, b in zip(assets_401k, assets_non_qualified)]
    })
    st.line_chart(df_growth_phase.set_index("Age"))

with c2:
    st.subheader("Projected Retirement Account Balance (Post-Retirement)")
    projected_years = list(range(retirement_age, retirement_age + len(combined_assets)))
    df_growth = pd.DataFrame({
        "Age": projected_years,
        "Portfolio Value": combined_assets
    })
    st.line_chart(df_growth.set_index("Age"))

with c3:
    st.subheader("Estimated Annual Spending Covered by Savings")
    df_spending = pd.DataFrame({
        "Age": projected_years,
        "Annual Spending": spending_over_time
    })
    st.line_chart(df_spending.set_index("Age"))

# summary section
st.subheader("Summary")
final_age = projected_years[len(combined_assets) - 1]
if include_ss:
    st.markdown(f"**🛡️ Social Security Included:** Estimated ${ss_income:,.0f} per year")
else:
    st.markdown("**🛡️ Social Security Not Included**")
st.markdown(f"**📌 Projected Portfolio at Retirement (Age {retirement_age}):** `${total_at_retirement:,.0f}`")
st.markdown(f"**💸 Annual Spending at Retirement (Inflation-Adjusted):** `${retirement_spending:,.0f}`")
st.markdown(f"**🧮 Portfolio lasts until Age:** `{final_age}`")

if final_age < 90:
    st.error("⚠️ Retirement plan may fall short. Consider saving more, retiring later, or include social security.")
else:
    st.success("✅ On track for retirement based on current assumptions.")
