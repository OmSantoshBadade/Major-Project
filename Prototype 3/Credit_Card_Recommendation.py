import tkinter as tk
from tkinter import messagebox
import pandas as pd

# Load the dataset
df = pd.read_csv("Credit_card_info_final.csv")

# Define scoring functions
def score_spending(row, value):
    # Custom logic based on your needs
    return 10  # Default scoring for now

def score_repayment(row, value):
    return 10  # Default scoring for now

def score_annual_fee_1(row, value):
    if row['AnnualFee1stYear'] <= value: return 10
    return 0

def score_annual_fee_2(row, value):
    if row['AnnualFee2ndYear'] <= value: return 10
    return 0

def score_minimum_spend(row, value):
    if row['MinimumSpendsForAnnualFeeReversal'] <= value: return 10
    return 0

def score_interest_rate(row, value):
    if row['OverdueMonthlyInterest'] <= value: return 10
    return 0

def score_foreign_fee(row, value):
    if row['ForeignCurrencyTransactionsFee'] <= value: return 10
    return 0

def score_domestic_lounge(row, value):
    if (value == "Yes" and str(row['DomesticAirportLoungeBenefits']).lower() == 'yes'):
        return 10
    elif value == "No":
        return 10
    return 0

def score_international_lounge(row, value):
    if (value == "Yes" and str(row['InternationalAirportLoungeBenefits']).lower() == 'yes'):
        return 10
    elif value == "No":
        return 10
    return 0

def score_railway_lounge(row, value):
    if (value == "Yes" and str(row['RailwayLounge']).lower() == 'yes'):
        return 10
    elif value == "No":
        return 10
    return 0

def score_fuel_waiver(row, value):
    if row['FuelSurchargeWaiverinPercentage'] <= value: return 10
    return 0

def score_reward_type(row, value):
    # You can add more sophisticated logic based on rewards
    if value == "Points":
        return 10
    elif value == "Cashback":
        return 10
    return 0

def score_ecommerce_cashback(row, value):
    if (value == "Yes" and row['E-Commerce Cashback in percentage'] > 0):
        return 10
    elif value == "No":
        return 10
    return 0

def score_utility_cashback(row, value):
    if (value == "Yes" and row['Utility Cashback in percentage'] > 0):
        return 10
    elif value == "No":
        return 10
    return 0

def score_spend_capability(row, value):
    if row['Mimimum Annual spend'] <= value: return 10
    return 0

# Calculate total scores
def calculate_scores(inputs):
    scores = []
    for _, row in df.iterrows():
        try:
            score = (
                score_spending(row, inputs['spending']) +
                score_repayment(row, inputs['repayment']) +
                score_annual_fee_1(row, inputs['annual_fee_1']) +
                score_annual_fee_2(row, inputs['annual_fee_2']) +
                score_minimum_spend(row, inputs['minimum_spend']) +
                score_interest_rate(row, inputs['interest_rate']) +
                score_foreign_fee(row, inputs['foreign_fee']) +
                score_domestic_lounge(row, inputs['domestic_lounge']) +
                score_international_lounge(row, inputs['international_lounge']) +
                score_railway_lounge(row, inputs['railway_lounge']) +
                score_fuel_waiver(row, inputs['fuel_waiver']) +
                score_reward_type(row, inputs['reward']) +
                score_ecommerce_cashback(row, inputs['ecommerce_cashback']) +
                score_utility_cashback(row, inputs['utility_cashback']) +
                score_spend_capability(row, inputs['spend_capability'])
            )
            scores.append((row['BankName-CardVariant'], score))
        except Exception as e:
            print(f"Skipping a row due to error: {e}")
    return sorted(scores, key=lambda x: x[1], reverse=True)[:5]

# GUI setup
root = tk.Tk()
root.title("Credit Card Recommendation System")
root.geometry("700x850")

entries = {}

fields = [
    ("Spending Category", ["Groceries", "Fuel", "Travel", "Dining", "Online Shopping"]),
    ("Repayment Preference", ["Full Payment", "Minimum Due", "Revolving Credit"]),
    ("Maximum 1st Year Annual Fee (in Rs)", tk.Entry),
    ("Maximum 2nd Year Annual Fee (in Rs)", tk.Entry),
    ("Minimum Spend Required for Fee Reversal (in Rs)", tk.Entry),
    ("Acceptable Monthly Interest Rate (%)", tk.Entry),
    ("Maximum Foreign Currency Transaction Fee (%)", tk.Entry),
    ("Domestic Airport Lounge Access Needed", ["Yes", "No"]),
    ("International Airport Lounge Access Needed", ["Yes", "No"]),
    ("Railway Lounge Access Needed", ["Yes", "No"]),
    ("Fuel Surcharge Waiver Minimum (%)", tk.Entry),
    ("Preferred Reward Type", ["Cashback", "Points"]),
    ("Cashback for E-commerce Spending Needed", ["Yes", "No"]),
    ("Cashback for Utility Bill Payments Needed", ["Yes", "No"]),
    ("Minimum Spend Capability (per year) (in Rs)", tk.Entry)
]

row = 0
for label, options in fields:
    tk.Label(root, text=label+":", font=("Arial", 12)).grid(row=row, column=0, sticky="w", pady=5, padx=10)
    if options == tk.Entry:
        entry = tk.Entry(root)
        entry.grid(row=row, column=1, pady=5)
    else:
        var = tk.StringVar()
        var.set(options[0])
        entry = tk.OptionMenu(root, var, *options)
        entry.grid(row=row, column=1, pady=5)
        entries[label] = var
    if options == tk.Entry:
        entries[label] = entry
    row += 1

# Recommendation Logic
def show_recommendations():
    try:
        inputs = {
            'spending': entries['Spending Category'].get(),
            'repayment': entries['Repayment Preference'].get(),
            'annual_fee_1': int(entries['Maximum 1st Year Annual Fee (in Rs)'].get()),
            'annual_fee_2': int(entries['Maximum 2nd Year Annual Fee (in Rs)'].get()),
            'minimum_spend': int(entries['Minimum Spend Required for Fee Reversal (in Rs)'].get()),
            'interest_rate': float(entries['Acceptable Monthly Interest Rate (%)'].get()),
            'foreign_fee': float(entries['Maximum Foreign Currency Transaction Fee (%)'].get()),
            'domestic_lounge': entries['Domestic Airport Lounge Access Needed'].get(),
            'international_lounge': entries['International Airport Lounge Access Needed'].get(),
            'railway_lounge': entries['Railway Lounge Access Needed'].get(),
            'fuel_waiver': float(entries['Fuel Surcharge Waiver Minimum (%)'].get()),
            'reward': entries['Preferred Reward Type'].get(),
            'ecommerce_cashback': entries['Cashback for E-commerce Spending Needed'].get(),
            'utility_cashback': entries['Cashback for Utility Bill Payments Needed'].get(),
            'spend_capability': int(entries['Minimum Spend Capability (per year) (in Rs)'].get())
        }

        top_cards = calculate_scores(inputs)
        result = "Top Credit Card Recommendations:\n\n"
        for i, (card, score) in enumerate(top_cards, start=1):
            result += f"{i}. {card} (Score: {score})\n"

        messagebox.showinfo("Recommendations", result)
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Submit Button
tk.Button(root, text="Get Recommendations", font=("Arial", 14), bg="green", fg="white", command=show_recommendations).grid(row=row, columnspan=2, pady=20)

root.mainloop()
