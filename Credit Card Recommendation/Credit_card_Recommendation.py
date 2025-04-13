# Credit Card Recommendation System with Scoring and Explanations

import pandas as pd
import os
import numpy as np

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(script_dir, "comprehensive-indian-banks-dataset.csv")

# Load and preprocess data
try:
    df = pd.read_csv(dataset_path)
except FileNotFoundError:
    print(f"Error: Dataset file not found at {dataset_path}")
    print("Please make sure the dataset file is in the same directory as this script.")
    exit(1)

# Clean & preprocess fee and credit limits
def extract_number(value):
    try:
        # Handle range values (e.g., "₹500-₹2000")
        if isinstance(value, str) and "-" in value:
            parts = value.split("-")
            # Return the average of the range
            return np.mean([int(p.replace("₹", "").replace(",", "").strip()) for p in parts])
        return int(str(value).replace("₹", "").replace(",", "").strip())
    except:
        return 0

# Process numeric fields
df["Annual Fee"] = df["Annual Fee Range"].apply(extract_number)
df["Credit Limit"] = df["Credit Limit Range"].apply(extract_number)

# ---------------- Scoring Function ---------------- #
def score_card(card, user):
    score = 0
    reasons = []

    # 1. Spending Category Matching
    category = user["spending_category"].lower()
    if category in str(card["Cash Back"]).lower():
        score += 2
        reasons.append(f"Great match for your {category} spending with good cashback.")

    # 2. Payment Discipline
    if user["repayment_behavior"] == "delay":
        if "0%" in str(card["Introductory Interest Rates"]):
            score += 2
            reasons.append("Offers 0% introductory interest rate.")
    else:
        if "reward" in str(card["Rewards"]).lower():
            score += 1
            reasons.append("Good rewards for full payment behavior.")

    # 3. Annual Fee Fit
    if card["Annual Fee"] <= user["fee_comfort"]:
        score += 2
        reasons.append("Annual fee within your budget.")

    # 4. Reward Preference
    reward_type = user["reward_type"].lower()
    if reward_type == "cashback" and "cash back" in str(card["Cash Back"]).lower():
        score += 2
        reasons.append("Excellent cashback rewards.")
    elif reward_type == "travel" and "air miles" in str(card["Loyalty Points/Rewards"]).lower():
        score += 2
        reasons.append("Great travel rewards and benefits.")
    elif reward_type == "shopping" and "vouchers" in str(card["Loyalty Points/Rewards"]).lower():
        score += 2
        reasons.append("Good shopping rewards and vouchers.")

    # 5. Credit Limit
    if card["Credit Limit"] >= user["min_credit_limit"]:
        score += 2
        reasons.append("Meets your credit limit requirement.")

    # 6. International Usage
    if user["intl"] and "international" in str(card["Cash Back"]).lower():
        score += 1
        reasons.append("Good for international transactions.")

    # 7. EMI Preference
    if user["emi"] and "EMI" in str(card["Introductory Interest Rates"]):
        score += 1
        reasons.append("Offers EMI conversion facility.")

    # 8. Digital or Physical Banking
    if user["digital_pref"] == "digital":
        score += 1
        reasons.append("Good digital banking features.")
    elif user["digital_pref"] == "branch" and card["Bank Type"] == "Public Sector":
        score += 1
        reasons.append("Large branch network available.")

    return score, "; ".join(reasons)

# ---------------- Recommendation Engine ---------------- #
def recommend_top_cards(user_preferences, top_n=5):
    scores = []
    for _, card in df.iterrows():
        score, reason = score_card(card, user_preferences)
        scores.append({
            "Bank": card["Bank Name"],
            "Card Features": {
                "Annual Fee": card["Annual Fee Range"],
                "Credit Limit": card["Credit Limit Range"],
                "Cashback": card["Cash Back"],
                "Rewards": card["Rewards"],
                "Special Offers": card["Introductory Interest Rates"]
            },
            "Score": score,
            "Why It's Good for You": reason
        })

    # Sort by score and get top N
    top_cards = sorted(scores, key=lambda x: x["Score"], reverse=True)[:top_n]
    
    # Convert to DataFrame for better display
    rec_df = pd.DataFrame(top_cards)
    return rec_df

# ---------------- CLI Interface ---------------- #
def ask_user_questions():
    print("\n💳 Let's find your ideal credit card. Answer a few quick questions:\n")

    try:
        spending_category = input("1. What do you spend the most on? (groceries/shopping/travel/dining/fuel): ").strip().lower()
        
        repay_behavior = input("2. Do you usually pay bills on time or delay? (on-time/delay): ").strip().lower()
        while repay_behavior not in ["on-time", "delay"]:
            print("Please enter either 'on-time' or 'delay'")
            repay_behavior = input("2. Do you usually pay bills on time or delay? (on-time/delay): ").strip().lower()

        fee = int(input("3. What is your max acceptable annual fee (₹)? e.g., 0, 1000, 2000: "))
        while fee < 0:
            print("Annual fee cannot be negative")
            fee = int(input("3. What is your max acceptable annual fee (₹)? e.g., 0, 1000, 2000: "))

        reward_type = input("4. What's your preferred reward type? (cashback/travel/shopping): ").strip().lower()
        while reward_type not in ["cashback", "travel", "shopping"]:
            print("Please enter either 'cashback', 'travel', or 'shopping'")
            reward_type = input("4. What's your preferred reward type? (cashback/travel/shopping): ").strip().lower()

        credit_limit = int(input("5. What's your expected minimum credit limit (₹)? e.g., 25000, 100000: "))
        while credit_limit < 0:
            print("Credit limit cannot be negative")
            credit_limit = int(input("5. What's your expected minimum credit limit (₹)? e.g., 25000, 100000: "))

        intl = input("6. Do you travel internationally or shop in USD/EUR online? (yes/no): ").strip().lower() == "yes"
        
        emi = input("7. Do you prefer EMI conversion for big purchases? (yes/no): ").strip().lower() == "yes"
        
        digital = input("8. Do you prefer digital-first cards or branch access? (digital/branch): ").strip().lower()
        while digital not in ["digital", "branch"]:
            print("Please enter either 'digital' or 'branch'")
            digital = input("8. Do you prefer digital-first cards or branch access? (digital/branch): ").strip().lower()

        return {
            "spending_category": spending_category,
            "repayment_behavior": repay_behavior,
            "fee_comfort": fee,
            "reward_type": reward_type,
            "min_credit_limit": credit_limit,
            "intl": intl,
            "emi": emi,
            "digital_pref": digital
        }

    except ValueError as e:
        print("\nError: Please enter a valid number for fees and credit limit.")
        return ask_user_questions()

# ---------------- Main Script ---------------- #
if __name__ == "__main__":
    try:
        print("\n=== Credit Card Recommendation System ===")
        print("This system will help you find the best credit card based on your preferences.")
        
        user_pref = ask_user_questions()
        print("\n🔍 Analyzing credit cards based on your preferences...")
        recommendations = recommend_top_cards(user_pref)

        print("\n🎯 Top 5 Credit Card Recommendations:\n")
        
        # Display each recommendation in a formatted way
        for idx, row in recommendations.iterrows():
            print(f"\n{idx + 1}. {row['Bank']}")
            print(f"Score: {row['Score']}/13")
            print(f"Why This Card: {row['Why It\'s Good for You']}")
            print("\nCard Features:")
            for feature, value in row['Card Features'].items():
                print(f"  • {feature}: {value}")
            print("-" * 80)

    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print("Please try again or contact support if the problem persists.")
