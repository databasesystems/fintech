import streamlit as st
import sys
sys.path.insert(0, '/workspaces/fintech/procedures')
from procedures.calculate_amortisation import calculate_amortisation
import datetime
import pandas as pd
import requests


wide_mode = True

# Streamlit App
st.title(" Loan Amortization Calculator")

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

def get_currency_from_ip():
    try:
        response = requests.get("https://ipapi.co/json/")
        data = response.json()
        country = data.get("country_name", "Unknown")
        currency = data.get("currency", "USD")  # Default to USD if not found
        return country, currency
    except Exception as e:
        st.error(f"Error getting location: {e}")
        return "Unknown", "USD"

# Get country and currency
country, currency = get_currency_from_ip()

# User Inputs
start_date = st.date_input("Start Date", value=datetime.datetime.now().date())
col1, col2 = st.columns(2)

with col1:
    loan_amount = st.number_input("Loan Amount (£/$/€)", min_value=1000.0, value=50000.0)
with col2:
    annual_rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, value=5.0)

col3, col4 = st.columns(2)

with col3:
    loan_term_years = st.number_input("Loan term (years)", min_value=0, value=15)
with col4:
    loan_term_months = st.number_input("Loan term (months)", min_value=0, value=7)

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
df = calculate_amortisation(loan_amount, annual_rate, loan_term,  extra_payment, lump_sum, lump_sum_date, start_date)

if loan_term['years'] == 0 and loan_term['months'] == 0:
    st.error("Loan term cannot be zero")
else:
    df = calculate_amortisation(loan_amount, annual_rate, loan_term,  extra_payment, lump_sum, lump_sum_date, start_date)

# Add a selectbox to choose the currency


with st.expander("Loan Summary", expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    if currency == "None":
        col1.metric("Monthly Payments", f"{df['Payment'].iloc[1]:,.2f}", delta=None)
        col2.metric("Total Interest Paid", f"{df['Interest'].sum():,.2f}", delta=None)
        col3.metric("Total Principal Paid", f"{df['Principal'].sum():,.2f}", delta=None)
        col4.metric("Total Monies Paid", f"{df['Payment'].sum():,.2f}", delta=None)
    else:
        col1.metric(f"Monthly Payments ({currency})", f"{currency}{df['Payment'].iloc[1]:,.2f}", delta=None)
        col2.metric(f"Total Interest Paid ({currency})", f"{currency}{df['Interest'].sum():,.2f}", delta=None)
        col3.metric(f"Total Principal Paid ({currency})", f"{currency}{df['Principal'].sum():,.2f}", delta=None)
        col4.metric(f"Total Monies Paid ({currency})", f"{currency}{df['Payment'].sum():,.2f}", delta=None)


# Display Graph
    df['Date'] = pd.to_datetime(df['Date'])
    st.line_chart(df.set_index('Date')[['Balance']], width=0, height=0, use_container_width=True)
    st.write("Loan Balance Over Time")

# Display Table
st.subheader("Amortization Schedule")
st.dataframe(df)

# Download as CSV
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Download Amortization Schedule", data=csv, file_name="loan_amortization.csv", mime="text/csv")

st.success("Loan amortization calculated successfully! ")