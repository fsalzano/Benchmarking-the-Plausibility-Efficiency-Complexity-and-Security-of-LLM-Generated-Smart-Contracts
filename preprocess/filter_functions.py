import pandas as pd

# Step 1: Read both files as text
with open("../../../data/train.token.code", "r") as function_file:
    functions = function_file.readlines()

print(len(functions))

with open("../../../data/train.token.nl", "r") as comment_file:
    comments = comment_file.readlines()


# Step 2: Prepare the output data
output_data = []

# Step 3: Iterate through both datasets
for i, (function, comment) in enumerate(zip(functions, comments), 1):
    function_cleaned = function.strip()
    comment_cleaned = comment.strip()

    # Skip if "modifier" is in the function
    if "modifier" in function_cleaned:
        continue

    # Append to the output data
    output_data.append({
        "ID": i,
        "Function": function_cleaned,
        "Comment": comment_cleaned
    })

# Step 4: Create a DataFrame
output_df = pd.DataFrame(output_data)

# Step 5: Remove rows where the Comment has fewer than 8 words
output_df = output_df[output_df["Comment"].apply(lambda x: len(x.split()) >= 8)]

# Step 6: Save to CSV
output_df.to_csv("functions_and_comments_filtered.csv", index=False)

print("Filtered CSV created: functions_and_comments_filtered.csv")
