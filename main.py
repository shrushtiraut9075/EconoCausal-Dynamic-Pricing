# Project: EconoCausal
# Dynamic Pricing via Double Machine Learning
# Domain: Data Science and Machine Learning

import pandas as pd

print("Welcome to EconoCausal Project!")

# Create a sample dataset
data = {
    "Product": ["A", "B", "C", "D", "E"],
    "Price": [100, 150, 200, 120, 180],
    "Demand": [50, 40, 30, 45, 35]
}

# Convert data into a DataFrame
df = pd.DataFrame(data)

# Display the dataset
print("\nSample Dataset:")
print(df)

# Calculate average price and demand
average_price = df["Price"].mean()
average_demand = df["Demand"].mean()

print("\nAverage Price:", average_price)
print("Average Demand:", average_demand)

print("\nInitial project setup completed successfully!")
