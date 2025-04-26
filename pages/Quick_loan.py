import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px


def car_loan_amortization(loan_amount, loan_term, interest_rate):
    # Convert interest rate to decimal
    interest_rate = interest_rate / 100
    
    # Calculate monthly interest rate
    monthly_interest_rate = interest_rate / 12
    
    # Calculate daily interest rate
    daily_interest_rate = monthly_interest_rate / 30
    
    # Calculate monthly payment
    monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** loan_term) / ((1 + monthly_interest_rate) ** loan_term - 1)
  
    daily_payment = monthly_payment / 30 

    # Create amortization schedule
    amortization_schedule = np.zeros((loan_term * 30, 6))
    balance = loan_amount
    total_interest = 0
    day = 0
    for i in range(loan_term * 30):
        interest = np.round(balance * daily_interest_rate, 2)
        principal = np.round(daily_payment - interest, 2)
        if principal > balance:
            principal = balance
        balance -= principal
        total_interest += interest
        amortization_schedule[i, :] = [day + 1, daily_payment, interest, principal, balance, total_interest]
        day += 1

    # Create DataFrame
    df = pd.DataFrame(amortization_schedule, columns=['Day', 'Payment', 'Interest', 'Principal', 'Balance', 'Total Interest'])
    return df

st.title("Very quick loan calculator")
st.write("See the interest you will have to pay on a loan. Use sidebar to enter loan details")
st.sidebar.header("Loan Details")

loan_amount = st.sidebar.number_input("Loan Amount (£)", min_value=1.0, value=15000.0)
loan_term = st.sidebar.number_input("Loan Term (Months)", min_value=1, value=60)
interest_rate = st.sidebar.number_input("Interest Rate (%)", min_value=0.0, value=6.1)

df = car_loan_amortization(loan_amount, loan_term, interest_rate)
total_interest = df['Interest'].sum()
total_principal = df['Principal'].sum()
total_payment = df['Payment'].sum()


st.subheader("Loan Summary")

col1, col2, col3 = st.columns(3)

col1.metric("Your Loan", f"£{total_principal:,.0f}")
col2.metric("Interest to pay", f"£{total_interest:,.0f}")
col3.metric("Total Payment at the end of term **", f"£{total_payment:,.0f}")

st.write("**Calculations for the total payment at the end of the term show the total amount you will pay, including interest.")

# st.write("See the schedule of payments below...")

# st.write(df)