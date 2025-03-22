import datetime
from datetime import date
import pandas as pd
from dateutil.relativedelta import relativedelta  # Better month handling

def calculate_amortisation(loan_amount, annual_rate, loan_term, extra_payment=0, lump_sum=0, lump_sum_date=None, start_date=None):
    # Convert loan term from years/months to total months
    total_months = loan_term['years'] * 12 + loan_term['months']
    
    # Convert annual interest rate to periodic rate
    rate_per_period = (annual_rate / 100) / 12  # Monthly interest rate
    
    # Calculate fixed monthly payment
    if rate_per_period > 0:
        payment = (loan_amount * rate_per_period) / (1 - (1 + rate_per_period) ** -total_months)
    else:
        payment = loan_amount / total_months  # No interest case

    # Initialize variables
    balance = loan_amount
    current_date = start_date
    amortization_data = [["Date", "Payment", "Principal", "Interest", "Balance"]]
    amortization_data.append([current_date.strftime('%Y-%m-%d'), 0, 0, 0, round(balance, 2)])  # Initial row

    total_payment_made = 0  # Track the total payment made
    term_end_date = start_date  # Initialize the term end date

    # Generate schedule
    for _ in range(1, total_months + 1):
        interest = balance * rate_per_period
        principal = payment - interest

        # Apply extra payments (before reducing balance)
        if extra_payment:
            principal += extra_payment
        
        # Apply lump sum payment (only once)
        if lump_sum and lump_sum_date and current_date >= lump_sum_date:
            principal += lump_sum
            total_payment_made += lump_sum  # Add lump sum to total payments
            lump_sum = 0  # Ensure lump sum is applied only once
        
        # Ensure principal does not exceed remaining balance
        principal = min(principal, balance)
        balance -= principal

        # Add the regular payment amount to the total payment made
        total_payment_made += payment + extra_payment

        # Store amortization row
        amortization_data.append([
            current_date.strftime('%Y-%m-%d'),
            round(payment + extra_payment, 2),
            round(principal, 2),
            round(interest, 2),
            round(balance, 2)
        ])

        # Update term end date
        term_end_date = current_date

        # Advance to next month
        current_date += relativedelta(months=1)

        # Stop early if balance is fully paid
        if balance <= 0:
            break

    # Convert to DataFrame
    df = pd.DataFrame(amortization_data[1:], columns=amortization_data[0])  # Remove header row for DataFrame
    
    return df, term_end_date  # Return DataFrame and the calculated term end date
