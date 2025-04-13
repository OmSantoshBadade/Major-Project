# Credit Card Recommendation System with Relaxed Filtering

import pandas as pd

# Load the dataset
df = pd.read_csv("comprehensive-indian-banks-dataset.csv")

# Preprocess Credit Limit Range and Annual Fee Range for numeric comparison
def extract_min_max(value):
    try:
        nums = [int(x.replace("₹", "").replace(",", "").strip()) 
                for x in value.split('-') if x.strip().startswith("₹") or x.strip().isdigit()]
        return nums if len(nums) == 2 else [0, 0]
    except:
        return [0, 0]

df[['Credit_Limit_Min', 'Credit_Limit_Max']] = df['Credit Limit Range'].apply(lambda x: pd.Series(extract_min_max(x)))
df[['Fee_Min', 'Fee_Max']] = df['Annual Fee Range'].apply(lambda x: pd.Series(extract_min_max(x)))

# Credit Card Recommender with Relaxed Filtering
def recommend_cards_relaxed(
    spending_category,
    repayment_behavior,
    annual_fee_limit,
    credit_limit_required,
    reward_preference,
    international_usage,
    introductory_offer,
    branch_importance,
    emi_preference,
    bank_type_preference
):
    base_df = df.copy()
    print(f"\nInitial dataset size: {len(base_df)} cards")

    # Pre-filter: annual fee and credit limit
    recommendations = base_df[
        (base_df['Fee_Max'] <= annual_fee_limit) &
        (base_df['Credit_Limit_Max'] >= credit_limit_required)
    ]
    print(f"After fee and credit limit filter: {len(recommendations)} cards")

    # Apply filters progressively
    def apply_filters(data, strict=True):
        filtered = data.copy()

        # Reward Preference
        if reward_preference.lower() == "cash back":
            filtered = filtered[filtered["Cash Back"].str.lower().str.contains("cash|fuel|groceries|dining", na=False)]
        elif reward_preference.lower() == "travel":
            filtered = filtered[filtered["Loyalty Points/Rewards"].str.lower().str.contains("flight|air miles|hotel", na=False)]
        elif reward_preference.lower() == "merchandise":
            filtered = filtered[filtered["Loyalty Points/Rewards"].str.lower().str.contains("merchandise|vouchers", na=False)]

        # International Usage - Only apply if specifically requested
        if international_usage and strict:
            filtered = filtered[filtered["Cash Back"].str.lower().str.contains("international", na=False)]

        # Introductory Offers - Only apply if specifically requested
        if introductory_offer and strict:
            filtered = filtered[filtered["Introductory Interest Rates"].str.contains("0%", na=False)]

        # Bank Type Preference - Only apply if specifically requested
        if bank_type_preference and strict:
            filtered = filtered[filtered["Bank Type"].str.lower() == bank_type_preference.lower()]

        return filtered

    # First pass (strict filters)
    strict_filtered = apply_filters(recommendations, strict=True)
    print(f"After strict filtering: {len(strict_filtered)} cards")

    # Fallback: relaxed filters
    if len(strict_filtered) < 5:
        print("Not enough matches with strict filtering, applying relaxed filters...")
        relaxed_filtered = apply_filters(recommendations, strict=False)
        recommendations = relaxed_filtered
        print(f"After relaxed filtering: {len(recommendations)} cards")
    else:
        recommendations = strict_filtered

    # Sort by credit limit and low fees
    recommendations = recommendations.sort_values(by=["Credit_Limit_Max", "Fee_Min"], ascending=[False, True])

    # If still not enough recommendations, return all available matches
    if len(recommendations) < 5:
        print(f"Only found {len(recommendations)} matching cards. Returning all matches.")
        return recommendations[[
            'Bank Name',
            'Rewards',
            'Cash Back',
            'Annual Fee Range',
            'Credit Limit Range',
            'Introductory Interest Rates',
            'Loyalty Points/Rewards',
            'Bank Type'
        ]]
    
    return recommendations[[
        'Bank Name',
        'Rewards',
        'Cash Back',
        'Annual Fee Range',
        'Credit Limit Range',
        'Introductory Interest Rates',
        'Loyalty Points/Rewards',
        'Bank Type'
    ]].head(5)

def user_questionnaire():
    print("Answer the following 10 questions to get the best credit card recommendation:\n")

    spending = input("1. What's your primary spending category? (e.g., groceries, fuel, dining, shopping): ")
    repay = input("2. Do you repay your credit card in full each month? (yes/no): ").strip().lower()
    repay_behavior = "full" if repay == "yes" else "balance"

    fee_limit = int(input("3. What is your max comfortable annual fee (₹)? (e.g., 0, 500, 2000): "))
    credit_limit = int(input("4. What minimum credit limit do you expect (₹)? (e.g., 25000, 100000): "))

    reward = input("5. What's your reward preference? (cash back / travel / merchandise): ").strip().lower()

    international = input("6. Do you need international transaction benefits? (yes/no): ").strip().lower() == "yes"

    intro_offer = input("7. Would you like introductory offers like 0% interest? (yes/no): ").strip().lower() == "yes"

    access = input("8. Is having a large branch/ATM network important to you? (yes/no): ").strip().lower() == "yes"

    emi = input("9. Do you often prefer EMI options for large purchases? (yes/no): ").strip().lower() == "yes"

    bank_type = input("10. Do you prefer a bank type? (Public Sector / Private Sector / Foreign Bank / Any): ").strip()
    bank_type = None if bank_type.lower() == "any" else bank_type

    return {
        "spending_category": spending,
        "repayment_behavior": repay_behavior,
        "annual_fee_limit": fee_limit,
        "credit_limit_required": credit_limit,
        "reward_preference": reward,
        "international_usage": international,
        "introductory_offer": intro_offer,
        "branch_importance": access,
        "emi_preference": emi,
        "bank_type_preference": bank_type
    }

if __name__ == "__main__":
    try:
        user_input = user_questionnaire()
        print("\nProcessing your input and finding the best card options...\n")

        result = recommend_cards_relaxed(**user_input)

        print("\n✅ Top Credit Card Matches for You:\n")
        print(result.reset_index(drop=True))
    except FileNotFoundError:
        print("Error: The dataset file 'comprehensive-indian-banks-dataset.csv' is missing.")
        print("Please make sure the dataset file is in the same directory as this script.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
