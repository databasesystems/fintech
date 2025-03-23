from datetime import datetime
import pandas as pd
from dateutil.relativedelta import relativedelta

def calculate_amortisation(loan_amount, annual_rate, loan_term, extra_payment, lump_sum, lump_sum_date, start_date, repayment_option):
    # Monthly interest rate
    monthly_rate = annual_rate / 12 / 100

    # Total payments based on loan term (years or months)
    if loan_term['years'] > 0:
        total_payments = loan_term['years'] * 12
    elif loan_term['months'] > 0:
        total_payments = loan_term['months']
    else:
        raise ValueError("Loan term cannot be zero")

    # Monthly payment calculation (standard amortization formula)
    if monthly_rate > 0:
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** total_payments) / ((1 + monthly_rate) ** total_payments - 1)
    else:
        monthly_payment = loan_amount / total_payments

    schedule = []
    balance = loan_amount
    current_date = start_date

    # Loop to generate payment schedule
    for i in range(total_payments):
        if balance <= 0:
            break  # Stop if the loan is fully paid

        interest = balance * monthly_rate
        principal = monthly_payment - interest + extra_payment

        # Apply lump sum if the current date matches the lump sum payment date
        if lump_sum_date and current_date >= lump_sum_date and lump_sum > 0:
            balance -= lump_sum
            lump_sum = 0  # Ensure lump sum is applied only once

        # Subtract principal from balance
        balance -= principal

        # Ensure balance never goes below 0 (important for final payment)
        balance = max(0, balance)

        # Add to schedule
        schedule.append({
            "Date": current_date.strftime("%Y-%m-%d"),
            "Balance": balance,
            "Interest": interest,
            "Principal": principal,
            "Payment": principal + interest
        })

        # Move to the next month with accurate date handling
        current_date += relativedelta(months=1)

    # If there's a balance remaining (due to rounding), adjust the last payment
    if balance > 0:
        final_payment = balance + schedule[-1]['Principal'] + schedule[-1]['Interest']
        schedule[-1]['Payment'] = final_payment  # Adjust final payment to cover the remaining balance
        schedule[-1]['Balance'] = 0.0  # Force the balance to 0

    term_end_date = current_date

    # Convert to DataFrame
    df = pd.DataFrame(schedule)

    return df, term_end_date

