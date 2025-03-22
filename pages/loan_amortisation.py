import streamlit as st
import sys
sys.path.insert(0, '/workspaces/fintech/procedures')
from procedures.calculate_amortisation import calculate_amortisation
import plotly.express as px
import plotly.graph_objects as go

import datetime
import pandas as pd
from forex_python.converter import CurrencyCodes

import pycountry_convert as pc
import json
from streamlit_javascript import st_javascript
from procedures.curr import get_currency_symbol 



wide_mode = True

# Streamlit App
st.title(" Loan amortisation calculator")

# Add CSS to make font smaller
# Inject CSS for styling metric numbers
st.markdown("""
    <style>
        div[data-testid="stMetricValue"] {
            font-size: 20px !important;  /* Adjust the font size as needed */
            color: #FF0000;  /* Optional: Change text color */
        }
    </style>
""", unsafe_allow_html=True)



# User Inputs form
start_date = st.date_input("Start Date", value=datetime.datetime.now().date())
col1, col2 = st.columns(2)

with col1:
    loan_amount = st.number_input("Loan Amount", min_value=1000.0, value=100000.0)
with col2:
    annual_rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, value=5.38)

col3, col4 = st.columns(2)

with col3:
    loan_term_years = st.number_input("Loan term (years)", min_value=0, value=25)
with col4:
    loan_term_months = st.number_input("Loan term (months)", min_value=0, value=0)

col5, col6 = st.columns(2)

with col5:
    extra_payment = st.number_input("Extra Monthly Payment (£/$/€)", min_value=0.0, value=0.0)
with col6:
    lump_sum = st.number_input("One-Time Lump Sum Payment (£/$/€)", min_value=0.0, value=0.0)

if lump_sum > 0:
    col7, _ = st.columns(2)
    with col7:
        lump_sum_date = st.date_input("Lump Sum Payment Date", value=datetime.datetime.now().date())
else:
    lump_sum_date = None

# Compute Amortization Schedule
loan_term = {'years': loan_term_years, 'months': loan_term_months}
# Compute Amortization Schedule
df, term_end_date = calculate_amortisation(loan_amount, annual_rate, loan_term, extra_payment, lump_sum, lump_sum_date, start_date)

# Convert term_end_date to formatted string
term_end_date_str = term_end_date.strftime("%Y-%m-%d")
if loan_term['years'] == 0 and loan_term['months'] == 0:
    st.error("Loan term cannot be zero")
else:
    # Compute Amortization Schedule
    df, term_end_date = calculate_amortisation(loan_amount, annual_rate, loan_term, extra_payment, lump_sum, lump_sum_date, start_date)

# Convert term_end_date to formatted string
term_end_date_str = term_end_date.strftime("%Y-%m-%d")
# Add a routine to choose the currency
# Use JavaScript to get the browser's locale
browser_locale = st_javascript("JSON.stringify(navigator.language || navigator.userLanguage)")

# If browser locale is returned, use it to get the currency symbol
if browser_locale:
    browser_locale = json.loads(browser_locale)  # Convert the locale to Python string
    currency = get_currency_symbol(browser_locale)  # Get the currency symbol

    st.write(f"Detected Browser Locale: **{browser_locale}**, Currency Symbol: **{currency}**")
else:
    st.write("Could not detect browser locale, no currency symbol will be displayed.")

df['Interest'] = pd.to_numeric(df['Interest'], errors='coerce')
df['Principal'] = pd.to_numeric(df['Principal'], errors='coerce')
df['Payment'] = pd.to_numeric(df['Payment'], errors='coerce')



with st.expander("Loan Summary", expanded=True):
    col1, col2, col3, col4, col5 = st.columns(5)
    if currency == "None":
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric(f"Monthly Payments ({currency})", f"{currency}{df['Payment'].iloc[1]:,.2f}")
        col2.metric(f"Total Interest Paid ({currency})", f"{currency}{df['Interest'].sum():,.2f}")
        col3.metric(f"Total Principal Paid ({currency})", f"{currency}{df['Principal'].sum():,.2f}")
        col4.metric(f"Total Monies Paid ({currency})", f"{currency}{(df['Principal'].sum() + df['Interest'].sum()):,.2f}")
        col5.metric("Term End Date", term_end_date_str)
    else:
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric(f"Monthly Payments ({currency})", f"{currency}{df['Payment'].iloc[1]:,.2f}")
        col2.metric(f"Total Interest Paid ({currency})", f"{currency}{df['Interest'].sum():,.2f}")
        col3.metric(f"Total Principal Paid ({currency})", f"{currency}{df['Principal'].sum():,.2f}")
        col4.metric(f"Total Monies Paid ({currency})", f"{currency}{(df['Principal'].sum() + df['Interest'].sum()):,.2f}")
        col5.metric("Term End Date", term_end_date_str)

# Display Graph

# Ensure Date column is in datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Extract year for aggregation
df['Year'] = df['Date'].dt.year

# Group by Year to sum Interest and Principal paid
df_yearly = df.groupby('Year', as_index=False).sum(numeric_only=True)[['Year', 'Principal', 'Interest']]

# Create a stacked bar chart with Yearly Principal and Interest payments
fig = px.bar(
    df_yearly, x="Year", y=["Principal", "Interest"],
    labels={"value": "Total Paid", "variable": "Payment Breakdown"},
    title="Loan Amortization: Yearly Cumulative Principal & Interest",
    color_discrete_map={"Principal": "blue", "Interest": "red"},
    barmode="stack"
)

# Display in Streamlit
st.plotly_chart(fig, use_container_width=True)



fig = px.line(
    df, x="Date", y="Balance",
    labels={"Balance": "Remaining Loan Balance"},
    title="Remaining Loan Balance Over Time",
    line_shape="spline",  # Smooth curve
    color_discrete_sequence=["red"]
)

st.plotly_chart(fig, use_container_width=True)

total_principal = df["Principal"].sum()
total_interest = df["Interest"].sum()
total_paid = total_principal + total_interest
interest_percentage = (total_interest / total_paid) * 100

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=interest_percentage,
    title={"text": "Interest as % of Total Payments"},
    gauge={"axis": {"range": [0, 100]}, "bar": {"color": "red"}}
))





# Display Table
st.subheader("Amortisation Schedule")
st.dataframe(df)

# Download as CSV
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Download Amortization Schedule", data=csv, file_name="loan_amortization.csv", mime="text/csv")

st.success("Loan amortization calculated successfully! ")