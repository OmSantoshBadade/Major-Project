# Credit Card Recommendation System with GUI

import pandas as pd
import os
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(script_dir, "Credit_card_details.csv")

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

    try:
        # Convert all inputs to strings for comparison and ensure they're not None
        category = str(user.get("spending_category", "")).lower()
        repayment = str(user.get("repayment_behavior", "")).lower()
        reward_type = str(user.get("reward_type", "")).lower()
        intl = str(user.get("intl", "")).lower()
        emi = str(user.get("emi", "")).lower()
        digital_pref = str(user.get("digital_pref", "")).lower()

        # Safely convert card features to strings
        card_cashback = str(card["Cash Back"]).lower() if not pd.isna(card["Cash Back"]) else ""
        card_rewards = str(card["Rewards"]).lower() if not pd.isna(card["Rewards"]) else ""
        card_loyalty = str(card["Loyalty Points/Rewards"]).lower() if not pd.isna(card["Loyalty Points/Rewards"]) else ""
        
        # Define category-specific terms
        category_terms = {
            "fuel": ["fuel", "petrol", "diesel", "gas station", "surcharge waiver"],
            "shopping": ["shopping", "retail", "merchant", "store"],
            "travel": ["travel", "air", "flight", "hotel", "holiday"],
            "dining": ["dining", "restaurant", "food", "culinary"],
            "groceries": ["grocery", "groceries", "supermarket", "mart"]
        }

        # Check for category match in all relevant fields
        if category in category_terms:
            search_terms = category_terms[category]
            # Check each term in all relevant card features
            for term in search_terms:
                if term in card_cashback:
                    category_score = 2
                    reasons.append(f"Excellent match for your {category} spending with {term} cashback.")
                    score += category_score
                    break
                elif term in card_rewards:
                    category_score = 1.5
                    reasons.append(f"Good match for your {category} spending with {term} rewards.")
                    score += category_score
                    break
                elif term in card_loyalty:
                    category_score = 1
                    reasons.append(f"Basic match for your {category} spending with {term} benefits.")
                    score += category_score
                    break

        # Payment Discipline (Max: 1 point)
        card_interest = str(card["Introductory Interest Rates"]).lower() if not pd.isna(card["Introductory Interest Rates"]) else ""
        if repayment == "delay" and "0%" in card_interest:
            score += 1
            reasons.append("Offers 0% introductory interest rate.")
        elif repayment == "on-time" and "reward" in card_rewards:
            score += 0.5
            reasons.append("Good rewards for full payment behavior.")

        # Annual Fee Fit (Max: 1.5 points)
        try:
            fee_comfort = float(user.get("fee_comfort", 0))
            annual_fee = float(card["Annual Fee"])
            if annual_fee <= fee_comfort:
                score += 1.5
                reasons.append("Annual fee within your budget.")
            elif annual_fee <= fee_comfort * 1.2:
                score += 0.5
                reasons.append("Annual fee slightly above your budget.")
        except (ValueError, TypeError):
            pass

        # Credit Limit (Max: 1.5 points)
        try:
            min_credit_limit = float(user.get("min_credit_limit", 0))
            credit_limit = float(card["Credit Limit"])
            if credit_limit >= min_credit_limit:
                score += 1.5
                reasons.append("Meets your credit limit requirement.")
            elif credit_limit >= min_credit_limit * 0.9:
                score += 0.5
                reasons.append("Credit limit slightly below your requirement but still substantial.")
        except (ValueError, TypeError):
            pass

        # International Usage (Max: 1 point)
        if intl == "yes":
            if "international" in card_cashback:
                score += 1
                reasons.append("Good for international transactions.")
            elif "international" in card_loyalty:
                score += 0.5
                reasons.append("Offers some international benefits.")

        # EMI Preference (Max: 0.5 points)
        if emi == "yes":
            if "emi" in card_interest or "emi" in card_loyalty:
                score += 0.5
                reasons.append("Offers EMI conversion facility.")

        # Bank Type Preference (Max: 0.5 points)
        bank_type = str(card["Bank Type"]).lower() if not pd.isna(card["Bank Type"]) else ""
        if digital_pref == "digital" and "private" in bank_type:
            score += 0.5
            reasons.append("Private sector bank with good digital features.")
        elif digital_pref == "branch" and "public" in bank_type:
            score += 0.5
            reasons.append("Public sector bank with extensive branch network.")

    except Exception as e:
        print(f"Error in score_card: {str(e)}")
        return 0, "Error in calculating score"

    # Round the final score to one decimal place
    score = round(score, 1)
    return score, "; ".join(reasons) if reasons else "No specific benefits found"

# ---------------- Recommendation Engine ---------------- #
def recommend_top_cards(user_preferences, top_n=5):
    scores = []
    for _, card in df.iterrows():
        try:
            score, reason = score_card(card, user_preferences)
            card_info = {
                "Bank": str(card["Bank Name"]) if not pd.isna(card["Bank Name"]) else "",
                "Score": score,
                "Why It's Good for You": reason,
                "Card Features": {
                    "Annual Fee": str(card["Annual Fee Range"]) if not pd.isna(card["Annual Fee Range"]) else "N/A",
                    "Credit Limit": str(card["Credit Limit Range"]) if not pd.isna(card["Credit Limit Range"]) else "N/A",
                    "Cashback": str(card["Cash Back"]) if not pd.isna(card["Cash Back"]) else "N/A",
                    "Rewards": str(card["Rewards"]) if not pd.isna(card["Rewards"]) else "N/A",
                    "Interest Rates": str(card["Introductory Interest Rates"]) if not pd.isna(card["Introductory Interest Rates"]) else "N/A",
                    "Loyalty Program": str(card["Loyalty Points/Rewards"]) if not pd.isna(card["Loyalty Points/Rewards"]) else "N/A",
                    "Bank Type": str(card["Bank Type"]) if not pd.isna(card["Bank Type"]) else "N/A"
                }
            }
            scores.append(card_info)
        except Exception as e:
            print(f"Error processing card: {e}")
            continue

    # Sort by score and get top N
    top_cards = sorted(scores, key=lambda x: x["Score"], reverse=True)[:top_n]
    
    # Convert to DataFrame
    df_data = []
    for card in top_cards:
        df_data.append({
            "Bank": card["Bank"],
            "Score": card["Score"],
            "Why It's Good for You": card["Why It's Good for You"],
            "Card Features": str(card["Card Features"])
        })
    
    return pd.DataFrame(df_data)

class CreditCardRecommender(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Credit Card Recommendation System")
        self.geometry("800x900")
        self.configure(bg='#f0f0f0')

        # Create main frame with padding
        main_frame = ttk.Frame(self, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Style configuration
        style = ttk.Style()
        style.configure('TLabel', font=('Arial', 10))
        style.configure('TCombobox', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10, 'bold'))

        # Variables
        self.spending_var = tk.StringVar()
        self.repayment_var = tk.StringVar()
        self.fee_var = tk.StringVar()
        self.reward_var = tk.StringVar()
        self.credit_limit_var = tk.StringVar()
        self.intl_var = tk.StringVar()
        self.emi_var = tk.StringVar()
        self.digital_var = tk.StringVar()

        # Set default values
        self.fee_var.set("2000")
        self.credit_limit_var.set("100000")

        # Create and place widgets
        self.create_widgets(main_frame)

        # Results Text Widget
        self.results_text = tk.Text(main_frame, height=20, width=80, font=('Arial', 10))
        self.results_text.grid(row=9, column=0, columnspan=2, pady=20)

    def create_widgets(self, frame):
        # Spending Category
        ttk.Label(frame, text="1. What do you spend the most on?").grid(row=0, column=0, sticky=tk.W, pady=5)
        spending_combo = ttk.Combobox(frame, textvariable=self.spending_var, 
                                    values=["groceries", "shopping", "travel", "dining", "fuel"])
        spending_combo.grid(row=0, column=1, sticky=tk.W, pady=5)

        # Repayment Behavior
        ttk.Label(frame, text="2. Do you usually pay bills on time or delay?").grid(row=1, column=0, sticky=tk.W, pady=5)
        repayment_combo = ttk.Combobox(frame, textvariable=self.repayment_var,
                                     values=["on-time", "delay"])
        repayment_combo.grid(row=1, column=1, sticky=tk.W, pady=5)

        # Annual Fee
        ttk.Label(frame, text="3. What is your max acceptable annual fee (₹)?").grid(row=2, column=0, sticky=tk.W, pady=5)
        fee_entry = ttk.Entry(frame, textvariable=self.fee_var)
        fee_entry.grid(row=2, column=1, sticky=tk.W, pady=5)

        # Reward Type
        ttk.Label(frame, text="4. What's your preferred reward type?").grid(row=3, column=0, sticky=tk.W, pady=5)
        reward_combo = ttk.Combobox(frame, textvariable=self.reward_var,
                                  values=["cashback", "travel", "shopping"])
        reward_combo.grid(row=3, column=1, sticky=tk.W, pady=5)

        # Credit Limit
        ttk.Label(frame, text="5. What's your expected minimum credit limit (₹)?").grid(row=4, column=0, sticky=tk.W, pady=5)
        credit_limit_entry = ttk.Entry(frame, textvariable=self.credit_limit_var)
        credit_limit_entry.grid(row=4, column=1, sticky=tk.W, pady=5)

        # International Usage
        ttk.Label(frame, text="6. Do you travel internationally or shop in USD/EUR online?").grid(row=5, column=0, sticky=tk.W, pady=5)
        intl_combo = ttk.Combobox(frame, textvariable=self.intl_var,
                                values=["yes", "no"])
        intl_combo.grid(row=5, column=1, sticky=tk.W, pady=5)

        # EMI Preference
        ttk.Label(frame, text="7. Do you prefer EMI conversion for big purchases?").grid(row=6, column=0, sticky=tk.W, pady=5)
        emi_combo = ttk.Combobox(frame, textvariable=self.emi_var,
                               values=["yes", "no"])
        emi_combo.grid(row=6, column=1, sticky=tk.W, pady=5)

        # Digital/Branch Preference
        ttk.Label(frame, text="8. Do you prefer digital-first cards or branch access?").grid(row=7, column=0, sticky=tk.W, pady=5)
        digital_combo = ttk.Combobox(frame, textvariable=self.digital_var,
                                   values=["digital", "branch"])
        digital_combo.grid(row=7, column=1, sticky=tk.W, pady=5)

        # Submit Button
        submit_btn = ttk.Button(frame, text="Get Recommendations", command=self.get_recommendations)
        submit_btn.grid(row=8, column=0, columnspan=2, pady=20)

    def get_recommendations(self):
        try:
            # Validate inputs
            if not all([self.spending_var.get(), self.repayment_var.get(), self.reward_var.get(),
                       self.intl_var.get(), self.emi_var.get(), self.digital_var.get()]):
                messagebox.showerror("Error", "Please fill in all fields")
                return

            try:
                fee = int(self.fee_var.get())
                credit_limit = int(self.credit_limit_var.get())
                if fee < 0 or credit_limit < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for fee and credit limit")
                return

            # Create user preferences dictionary with string values
            user_pref = {
                "spending_category": self.spending_var.get(),
                "repayment_behavior": self.repayment_var.get(),
                "fee_comfort": fee,
                "reward_type": self.reward_var.get(),
                "min_credit_limit": credit_limit,
                "intl": self.intl_var.get(),  # Keep as string
                "emi": self.emi_var.get(),    # Keep as string
                "digital_pref": self.digital_var.get()
            }

            recommendations = recommend_top_cards(user_pref)
            
            # Clear previous results
            self.results_text.delete(1.0, tk.END)
            
            # Display recommendations
            self.results_text.insert(tk.END, "🎯 Top 5 Credit Card Recommendations:\n\n")
            
            for idx, row in recommendations.iterrows():
                self.results_text.insert(tk.END, f"{idx + 1}. {row['Bank']}\n")
                self.results_text.insert(tk.END, f"Score: {row['Score']}/10\n")
                self.results_text.insert(tk.END, f"Why This Card: {row['Why It\'s Good for You']}\n")
                self.results_text.insert(tk.END, "\nCard Features:\n")
                
                try:
                    features = eval(row['Card Features'])
                    for feature, value in features.items():
                        if value and value != "N/A":  # Only show non-empty and non-N/A values
                            self.results_text.insert(tk.END, f"  • {feature}: {value}\n")
                except Exception as e:
                    self.results_text.insert(tk.END, "  Error displaying features\n")
                
                self.results_text.insert(tk.END, "-" * 80 + "\n\n")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

# ---------------- Main Script ---------------- #
if __name__ == "__main__":
    app = CreditCardRecommender()
    app.mainloop()
