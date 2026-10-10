import pandas as pd

print("EconoCausal: Dynamic Pricing Project")

data = {
    "Product": ["A", "B", "C", "D", "E"],
    "Price": [100, 150, 200, 120, 180],
    "Demand": [50, 40, 30, 45, 35]
}

df = pd.DataFrame(data)

print("\nSample Dataset:")
print(df)

print("\nAverage Price:", df["Price"].mean())
print("Average Demand:", df["Demand"].mean())
