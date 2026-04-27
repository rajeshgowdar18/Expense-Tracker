# generate_sample.py
import pandas as pd, random, numpy as np

descriptions = [
    "Swiggy order", "Uber ride", "Amazon purchase", "Electricity bill",
    "Netflix subscription", "Apollo pharmacy", "Zomato delivery",
    "Ola cab", "Flipkart order", "Jio broadband", "Spotify premium",
    "Medplus medicine", "Restaurant bill", "Petrol bunk", "Myntra clothes",
    "Water bill", "Bookmyshow ticket", "Gym membership", "ATM withdrawal",
    "BigBasket grocery"
]

df = pd.DataFrame({
    "Date":        pd.date_range("2024-01-01", periods=50, freq="D").strftime("%Y-%m-%d"),
    "Description": [random.choice(descriptions) for _ in range(50)],
    "Amount":      np.random.randint(100, 2000, 50),
})

df.to_csv("sample_expenses.csv", index=False)
print("sample_expenses.csv created!")