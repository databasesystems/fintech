import streamlit as st
import datetime
import pandas as pd
import plotly.express as px
from procedures.calculate_amortisation import calculate_amortisation
from dateutil.relativedelta import relativedelta

# Sidebar Inputs
st.sidebar.header("Loan Details")

start_date = st.sidebar.date_input("Start Date", value=datetime.datetime.now().date())
loan_amount = st.sidebar.number_input("Loan Amount", min_value=1000.0, value=100000.0)
annual_rate = st.sidebar.number_input("Annual Interest Rate (%)", min_value=0.0, value=5.38)
loan_term_years = st.sidebar.number_input("Loan Term (Years)", min_value=0, value=6)
loan_term_months = st.sidebar.number_input("Loan Term (Months)", min_value=0, value=11)
extra_payment = st.sidebar.number_input("Extra Monthly Payment", min_value=0.0, value=0.0)
lump_sum = st.sidebar.number_input("One-Time Lump Sum Payment", min_value=0.0, value=0.0)
lump_sum_date = st.sidebar.date_input("Lump Sum Payment Date", value=start_date) if lump_sum > 0 else None

# Calculate Amortization without overpayments
loan_term = {'years': loan_term_years, 'months': loan_term_months}
df_no_overpayment, term_end_date_no_overpayment = calculate_amortisation(loan_amount, annual_rate, loan_term, 0.0, 0.0, None, start_date, None)

# Calculate Amortization with overpayments (either monthly or lump sum)
df_with_overpayment, term_end_date_with_overpayment = calculate_amortisation(
    loan_amount, annual_rate, loan_term, extra_payment, lump_sum, lump_sum_date, start_date, None
)

# Loan Summary for both scenarios
def create_loan_summary(df, term_end_date, lump_sum, extra_payment):
    # Loan summary data (cumulative sums)
    remaining_balance = df['Balance'].iloc[-1]  # Last row for the remaining balance

    # If balance is small (due to rounding), force it to zero
    if remaining_balance < 1.0:
        remaining_balance = 0.0

    return {
        "Loan to pay": f"£{loan_amount:,.2f}",
        "Interest rate": f"{annual_rate}% per annum",
        "Loan term": f"{loan_term_years} years {loan_term_months} months",
        "Monthly payments": f"£{df['Payment'].iloc[0]:,.2f}",
        "Overpayment": f"£{lump_sum:,.2f}" if lump_sum > 0 else f"£{extra_payment:,.2f}" if extra_payment > 0 else "£0.00",
        "Principal": f"£{df['Principal'].sum():,.2f}",
        "Interest": f"£{df['Interest'].sum():,.2f}",
        # "Principal + Interest": f"£{(df['Principal'].sum() + df['Interest'].sum()):,.2f}",
        "Remaining balance": f"£{remaining_balance:,.2f}",
        "Loan end date": term_end_date.strftime("%Y-%m-%d")
    }

# Create loan summary for both scenarios
loan_summary_no_overpayment = create_loan_summary(df_no_overpayment, term_end_date_no_overpayment, lump_sum, extra_payment)
loan_summary_with_overpayment = create_loan_summary(df_with_overpayment, term_end_date_with_overpayment, lump_sum, extra_payment)

# Display loan summaries side by side for comparison
with st.container():
    st.subheader("Loan summary comparison")
    col1, col2, col3 = st.columns([2, 2, 4])
    with col1:
        st.write("**Details**")
    with col2:
        st.write("**Without Overpayment**")
    with col3:
        st.write("**With Overpayment**")

    loan_summary_no_overpayment["Overpayment"] = "£0.00"
    for key, value in loan_summary_no_overpayment.items():
        col1, col2, col3 = st.columns([2, 2, 4])
        with col1:
            st.write(key)
        with col2:
            st.write(value)
        with col3:
            if loan_summary_no_overpayment[key] != loan_summary_with_overpayment[key] and key in ["Interest", "Loan end date"]:
                st.markdown(f"<span style='color: green;'>{loan_summary_with_overpayment[key]}</span>", unsafe_allow_html=True)
            else:
                st.write(loan_summary_with_overpayment[key])

# X-axis dates for both scenarios based on start_date and term
df_no_overpayment['Date'] = [start_date + relativedelta(months=i) for i in range(len(df_no_overpayment))]
df_with_overpayment['Date'] = [start_date + relativedelta(months=i) for i in range(len(df_with_overpayment))]

# Define the end date of the term based on the original loan term for both scenarios
original_end_date = start_date + relativedelta(years=loan_term_years, months=loan_term_months)

# Plot Remaining Loan Balance Over Time for both scenarios
fig = px.line(
    pd.concat([df_no_overpayment[['Date', 'Balance']].assign(Situation='Without Overpayment'),
               df_with_overpayment[['Date', 'Balance']].assign(Situation='With Overpayment')]),
    x="Date", y="Balance", color="Situation",
    labels={"Balance": "Remaining Loan Balance", "Date": "Payment Date"},
    title="📉 Remaining Loan Balance Over Time (With and Without Overpayment)",
    line_shape="spline", color_discrete_sequence=["red", "green"]
)

# Update layout for better visuals and comparison
fig.update_layout(
    xaxis_title="Payment Date",
    yaxis_title="Remaining Loan Balance (£)",
    showlegend=True,
    xaxis=dict(
        range=[start_date, original_end_date],  # Keep original loan term on x-axis
        tickformat="%Y-%m",  # Show Year-Month format
        tickangle=0          # Rotate labels for readability
    )
)

# Display the plotly chart
st.plotly_chart(fig, use_container_width=True)

# Provide downloadable CSV for amortization schedules
csv_no_overpayment = df_no_overpayment.to_csv(index=False).encode('utf-8')
csv_with_overpayment = df_with_overpayment.to_csv(index=False).encode('utf-8')

st.download_button("⬇️ Download Amortization Schedule (Without Overpayment)", data=csv_no_overpayment, file_name="loan_amortization_no_overpayment.csv", mime="text/csv")
st.download_button("⬇️ Download Amortization Schedule (With Overpayment)", data=csv_with_overpayment, file_name="loan_amortization_with_overpayment.csv", mime="text/csv")

st.success("Loan amortization comparison calculated successfully! 🚀")
