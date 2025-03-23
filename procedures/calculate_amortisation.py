import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta

def calculate_amortisation(loan_amount, annual_rate, loan_term, extra_payment, lump_sum, lump_sum_date, start_date, end_date):
    # Calculate monthly interest rate
    monthly_interest_rate = (annual_rate / 100) / 12
    
    # Calculate loan term in months
    if loan_term['years'] > 0:
        loan_term_months = loan_term['years'] * 12 + loan_term['months']
    else:
        loan_term_months = loan_term['months']
    
    # Calculate monthly payment
    monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** loan_term_months) / ((1 + monthly_interest_rate) ** loan_term_months - 1)
    
    # Create amortization schedule
    amortization_schedule = []
    balance = loan_amount
    for i in range(loan_term_months):
        if balance <= 0:
            interest = 0
            principal = 0
            payment = 0
        else:
            interest = balance * monthly_interest_rate
            principal = monthly_payment - interest
            if extra_payment > 0:
                principal += extra_payment
            if lump_sum > 0 and start_date + relativedelta(months=i) == lump_sum_date:
                principal += lump_sum
                balance -= lump_sum
                # Recalculate monthly payment
                monthly_payment = balance * (monthly_interest_rate * (1 + monthly_interest_rate) ** (loan_term_months - i - 1)) / ((1 + monthly_interest_rate) ** (loan_term_months - i - 1) - 1)
            if principal > balance:
                principal = balance
            balance -= principal
            payment = monthly_payment + extra_payment
        amortization_schedule.append({
            'Month': i + 1,
            'Payment': payment,
            'Interest': interest,
            'Principal': principal,
            'Balance': balance
        })
    
    # Create DataFrame from amortization schedule
    df = pd.DataFrame(amortization_schedule)
    
    # Calculate end date of loan term
    if end_date is None:
        end_date = start_date + relativedelta(months=len(df[df['Balance'] > 0]))
    
    return df, end_date