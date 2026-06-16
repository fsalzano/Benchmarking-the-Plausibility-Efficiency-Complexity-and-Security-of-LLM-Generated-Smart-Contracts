import pandas as pd
import json
import ast
import numpy as np

# Paths to all datasets
datasets = {
    "codellama": '../scripts/codellama/codellama.csv',
    "codellama_improved": '../scripts/codellama/codellama_with_rag.csv',
    "deepseek": '../scripts/deepseek/deepseek.csv',
    "deepseek_improved": '../scripts/deepseek/deepseek_with_rag.csv',
    "gemini": '../scripts/Gemini/gemini.csv',
    "gemini_improved": '../scripts/Gemini/gemini_with_rag.csv',
    "gpt": '../scripts/ChatGPT/chatGPT.csv',
    "gpt_improved": '../scripts/ChatGPT/chatGPT_with_rag.csv'
}

columns_of_interest = ['SemanticSimilarity', 'TED', 'BLEU']

def extract_complexity(cognitive_complexity_input, target_function):
    try:
        if isinstance(cognitive_complexity_input, str):
            try:
                complexity_data = json.loads(cognitive_complexity_input)
            except json.JSONDecodeError:
                complexity_data = ast.literal_eval(cognitive_complexity_input)
        elif isinstance(cognitive_complexity_input, list):
            complexity_data = cognitive_complexity_input
        else:
            return None
        for entry in complexity_data:
            if entry.get('function') == target_function:
                return entry.get('complexity')
    except Exception as e:
        print(f"Error extracting complexity: {e}")
    return None

def calculate_cognitive_complexity_statistics(cognitive_complexity_column, target_function_column, name):
    complexities = []
    for cognitive_complexity_str, target_function in zip(cognitive_complexity_column, target_function_column):
        complexity = extract_complexity(cognitive_complexity_str, target_function)
        if complexity is not None and int(complexity) > 0:
            complexities.append(complexity)

    if complexities:
        complexities = np.array(complexities)
        print(f" cognitive complexities for: {name}")
        print(f"    Cognitive Complexity - Min: {complexities.min()}")
        print(f"    Cognitive Complexity - Max: {complexities.max()}")
        print(f"    Cognitive Complexity - Mean: {complexities.mean():.4f}")
        print(f"    Cognitive Complexity - Std: {complexities.std():.4f}")
    else:
        print(f"    No valid cognitive complexity data found.")

def calculate_statistics(df, columns):
    stats = {}
    for col in columns:
        if col in df.columns:
            non_null_values = df[col].dropna()
            non_null_values = non_null_values[non_null_values >= 0]
            stats[col] = {
                "min": round(non_null_values.min(), 4),
                "max": round(non_null_values.max(), 4),
                "mean": round(non_null_values.mean(), 4),
                "std": round(non_null_values.std(), 4)
            }
        else:
            stats[col] = {"min": None, "max": None, "mean": None, "std": None}
    return stats

def print_cyclomatic_complexity(cyclomatic_complexity, name):
    min_val = cyclomatic_complexity.min()
    max_val = cyclomatic_complexity.max()
    mean_val = cyclomatic_complexity.mean()
    std_val = cyclomatic_complexity.std()
    print(f"cyclomatic complexity for: {name}")
    print(f"  Min: {min_val}")
    print(f"  Max: {max_val}")
    print(f"  Mean: {mean_val:.4f}")
    print(f"  Std: {std_val:.4f}")
    print("--------------------------------------------------")

# Load ground truth once
gt = pd.read_csv("../data/sample_of_interest.csv")
gt["ID"] = gt["ID"].astype(str)
gt["target_function"] = gt["target_function"].astype(str)
gt["IsCorrect"] = gt["IsCorrect"].astype(bool)
correct_ids = set(gt.loc[gt["IsCorrect"], "ID"])

# For difference analysis: which columns map to each model
complexity_columns = {
    "codellama": "CodeLLamaCognitiveComplexity",
    "codellama_improved": "CodeLLamaCognitiveComplexity",
    "deepseek": "DeepseekCognitiveComplexity",
    "deepseek_improved": "DeepseekCognitiveComplexity",
    "gemini": "GeminiCognitiveComplexity",
    "gemini_improved": "GeminiCognitiveComplexity",
    "gpt": "GPTCognitiveComplexity",
    "gpt_improved": "GPTCognitiveComplexity"
}

# Process all datasets
for name, path in datasets.items():
    print(name)
    df = pd.read_csv(path)
    df["ID"] = df["ID"].astype(str)
    df["target_function"] = df["target_function"].astype(str)

    print(f"Similarity Statistics for {name} ({path}):")
    stats = calculate_statistics(df, columns_of_interest)
    for col, col_stats in stats.items():
        print(f"  {col}:")
        print(f"    Min: {col_stats['min']}")
        print(f"    Max: {col_stats['max']}")
        print(f"    Mean: {col_stats['mean']}")
        print(f"    Std: {col_stats['std']}")

    # All instances
    print("\n[ALL INSTANCES]")
    calculate_cognitive_complexity_statistics(df[complexity_columns[name]], df['target_function'], name)
    cyclomatic_col = complexity_columns[name].replace("Cognitive", "Cyclomatic")
    print_cyclomatic_complexity(df[cyclomatic_col], name)

    # Subset with IsCorrect=True
    df_correct = df[df["ID"].isin(correct_ids)]
    print("\n[ONLY IDs with IsCorrect=True]")
    calculate_cognitive_complexity_statistics(df_correct[complexity_columns[name]], df_correct['target_function'], name)
    print_cyclomatic_complexity(df_correct[cyclomatic_col], name)

    # Difference to ground truth
    diffs = []
    for _, row in df.iterrows():
        id_ = row["ID"]
        func = row["target_function"]
        model_complexity = extract_complexity(row[complexity_columns[name]], func)
        if model_complexity is None:
            continue
        gt_row = gt[gt["ID"] == id_]
        if gt_row.empty:
            continue
        gt_complexity_raw = gt_row["cognitive_complexity"].values[0]
        gt_complexity = extract_complexity(gt_complexity_raw, func)
        if gt_complexity is None:
            continue
        diff = model_complexity - gt_complexity
        diffs.append(diff)

    if diffs:
        diffs = np.array(diffs)
        # print(f"\n[DIFF] Cognitive Complexity difference w.r.t ground truth ({name}):")
        # print(f"  Min: {diffs.min():.4f}")
        # print(f"  Max: {diffs.max():.4f}")
        # print(f"  Mean: {diffs.mean():.4f}")
        # print(f"  Std: {diffs.std():.4f}")
    else:
        print("No matching cognitive complexity data found for comparison.")

    print("=" * 60)

# Ground truth summary
print_cyclomatic_complexity(gt['cyclomatic_complexity'], "ground truth")
calculate_cognitive_complexity_statistics(gt['cognitive_complexity'], gt['target_function'], "ground truth")
