import datetime
from datetime import timedelta
import pandas as pd

def calculate_amortisation(loan_amount, annual_rate, loan_term, extra_payment=0, lump_sum=0, lump_sum_date=None, start_date=None):
    # Convert loan term from years/months to total months
    total_months = loan_term['years'] * 12 + loan_term['months']
    
    # Convert annual interest rate to periodic rate
    periods = total_months
    rate_per_period = (annual_rate / 100) / 12  # Assume monthly payments
    
    # Calculate fixed periodic payment
    if rate_per_period > 0:
        payment = (loan_amount * rate_per_period) / (1 - (1 + rate_per_period) ** -periods)
    else:
        payment = loan_amount / periods  # No interest case

    # Create amortization schedule
    balance = loan_amount
    amortization_data = [[start_date.strftime('%Y-%m-%d'), 0, 0, 0, round(balance, 2)]]  # Initial row with start date
    current_date = start_date

    for i in range(1, periods + 1):
        interest = balance * rate_per_period
        principal = payment - interest
        balance -= principal

        # Apply extra payments
        if extra_payment:
            balance -= extra_payment
            principal += extra_payment

        # Apply lump sum if applicable
        if lump_sum and lump_sum_date and current_date >= lump_sum_date:
            balance -= lump_sum
            principal += lump_sum
            lump_sum = 0  # Ensure it is applied only once

        if balance < 0:
            balance = 0

        amortization_data.append([current_date.strftime('%Y-%m-%d'), round(payment, 2), round(principal, 2), round(interest, 2), round(balance, 2)])

        current_date += timedelta(days=30)  # Assume monthly payments

    df = pd.DataFrame(amortization_data, columns=['Date', 'Payment', 'Principal', 'Interest', 'Balance'])
    return df