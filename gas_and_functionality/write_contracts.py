import os
import pandas as pd

# Get absolute path to the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# CSV paths
gt_path = os.path.join(script_dir, "..", "data", "sample_of_interest.csv")

chatGPT_path = os.path.join(script_dir, "..", "scripts", "ChatGPT", "chatGPT.csv")
gemini_path = os.path.join(script_dir, "..", "scripts", "Gemini", "gemini.csv")
codellama_path = os.path.join(script_dir, "..", "scripts", "codellama", "codellama.csv")
deepseek_path = os.path.join(script_dir, "..", "scripts", "deepseek", "deepseek.csv")

chatGPT_rag_path = os.path.join(script_dir, "..", "scripts", "ChatGPT", "chatGPT_with_rag.csv")
gemini_rag_path = os.path.join(script_dir, "..", "scripts", "Gemini", "gemini_with_rag.csv")
codellama_rag_path = os.path.join(script_dir, "..", "scripts", "codellama", "codellama_with_rag.csv")
deepseek_rag_path = os.path.join(script_dir, "..", "scripts", "deepseek", "deepseek_with_rag.csv")

# Output directories
output_dirs = {
    gt_path: "gt_contracts",
    chatGPT_path: "chatGPT_contracts",
    chatGPT_rag_path: "chatGPT_rag_contracts",
    gemini_path: "gemini_contracts",
    gemini_rag_path: "gemini_rag_contracts",
    codellama_path: "codellama_contracts",
    codellama_rag_path: "codellama_rag_contracts",
    deepseek_path: "deepseek_coder_contracts",
    deepseek_rag_path: "deepseek_coder_rag_contracts"
}


# Function to extract and write contracts from a CSV
def export_contracts(csv_path, output_dir):
    print(f"Processing: {csv_path}")
    df = pd.read_csv(csv_path)
    gt_df = pd.read_csv(gt_path)
    gt_df["ID"] = gt_df["ID"].astype(str)
    gt_df["IsCorrect"] = gt_df["IsCorrect"].fillna(False)

    os.makedirs(output_dir, exist_ok=True)

    for index, row in df.iterrows():
        contract_code = row.get("contract_with_constructor")
        ID = row.get("ID")

        # Skip rows with missing contract code or ID
        if pd.isna(contract_code) or pd.isna(ID):
            continue

        ID_str = str(ID)

        # Check if the ID exists in the ground truth and is marked as correct
        match = gt_df.loc[gt_df["ID"] == ID_str]
        if match.empty or not bool(match["IsCorrect"].values[0]):
            continue  # Skip if not found or marked as incorrect


        # Save the contract to a .sol file
        filepath = os.path.join(output_dir, f"{ID_str}.sol")
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(str(contract_code))
        print(f"Smart contract saved as: {filepath}")


# Apply the function to each dataset
for csv_path, output_dir in output_dirs.items():
    export_contracts(csv_path, output_dir)
