import pandas as pd

# Step 1: Load the filtered dataset
filtered_df = pd.read_csv("functions_and_comments_filtered.csv")

# Step 2: Extract a random sample of 500 rows
sample_of_interest = filtered_df.sample(n=500, random_state=42)

# Step 3: Save the sample to a new CSV file
sample_of_interest.to_csv("sample_of_interest.csv", index=False)

print("Random sample saved to sample_of_interest.csv")
