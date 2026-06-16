import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
import ast

# === Define explicit CSV paths ===
csv_files = {
    "ChatGPT-4o Baseline": "../scripts/ChatGPT/chatGPT.csv",
    "ChatGPT-4o RAG": "../scripts/ChatGPT/chatGPT_with_rag.csv",
    "CodeLlama Baseline": "../scripts/codellama/codellama.csv",
    "CodeLlama RAG": "../scripts/codellama/codellama_with_rag.csv",
    "DeepSeek Baseline": "../scripts/deepseek/deepseek.csv",
    "DeepSeek RAG": "../scripts/deepseek/deepseek_with_rag.csv",
    "Gemini Baseline": "../scripts/Gemini/gemini.csv",
    "Gemini RAG": "../scripts/Gemini/gemini_with_rag.csv",
}

# === Metrics to extract ===
similarity_metrics = ["SemanticSimilarity", "BLEU", "TED"]
complexity_mapping = {
    "ChatGPT-4o": ("GPTCognitiveComplexity", "GPTCyclomaticComplexity"),
    "CodeLlama": ("CodeLLamaCognitiveComplexity", "CodeLLamaCyclomaticComplexity"),
    "DeepSeek": ("DeepseekCognitiveComplexity", "DeepseekCyclomaticComplexity"),
    "Gemini": ("GeminiCognitiveComplexity", "GeminiCyclomaticComplexity")
}

similarity_data = []
complexity_data = []

# === Function to extract cognitive complexity for a specific function ===
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

# === Load and process each CSV ===
for label, path in csv_files.items():
    try:
        df = pd.read_csv(path)
        model, version = label.split(" ", 1)

        # Handle similarity metrics
        for metric in similarity_metrics:
            df[metric] = pd.to_numeric(df.get(metric, pd.Series(dtype='float')), errors="coerce")

        df_sim = df[["SemanticSimilarity", "BLEU", "TED"]].copy()
        df_sim["Model"] = model
        df_sim["Mode"] = version
        similarity_data.append(df_sim)

        # Handle complexity metrics
        cog_col, cyc_col = complexity_mapping[model]
        if cog_col in df.columns and cyc_col in df.columns:
            df[cyc_col] = pd.to_numeric(df[cyc_col], errors="coerce")

            cognitive_values = df.apply(
                lambda row: extract_complexity(row.get(cog_col), row.get("target_function")), axis=1
            )

            df_cplx = pd.DataFrame({
                "Model": model,
                "Mode": version,
                "Cognitive Complexity": cognitive_values,
                "Cyclomatic Complexity": df[cyc_col]
            })
            complexity_data.append(df_cplx)
        else:
            print(f"[⚠️] Missing complexity columns for {label}: {cog_col}, {cyc_col}")

    except Exception as e:
        print(f"[❌] Failed to process {label}: {e}")

# === Combine all data ===
similarity_df = pd.concat(similarity_data, ignore_index=True)
complexity_df = pd.concat(complexity_data, ignore_index=True)

# === Output directory ===
output_dir = "BOXPLOT"
os.makedirs(output_dir, exist_ok=True)

# === Plot similarity metrics ===
for metric in similarity_metrics:
    plt.figure(figsize=(9, 5))
    sns.boxplot(
        data=similarity_df,
        x="Model",
        y=metric,
        hue="Mode",
        dodge=0.4,
        width=0.7,
        linewidth=1
    )
    plt.legend(
        title="",
        loc="upper center",
        bbox_to_anchor=(0.5, 1.25),
        ncol=2,
        frameon=False
    )
    plt.title(f"{metric} by Model", fontsize=11)
    plt.xlabel("Model")
    plt.ylabel(metric)
    plt.tight_layout(pad=1.0)
    plt.savefig(os.path.join(output_dir, f"{metric.lower()}_boxplot.png"))
    plt.close()

# === Plot complexity metrics ===
for metric in ["Cognitive Complexity", "Cyclomatic Complexity"]:
    plt.figure(figsize=(9, 5))
    sns.boxplot(
        data=complexity_df,
        x="Model",
        y=metric,
        hue="Mode",
        dodge=0.4,
        width=0.7,
        linewidth=1
    )
    plt.legend(
        title="",
        loc="upper center",
        bbox_to_anchor=(0.5, 1.25),
        ncol=2,
        frameon=False
    )
    plt.title(f"{metric} by Model", fontsize=11)
    plt.xlabel("Model")
    plt.ylabel(metric)
    plt.tight_layout(pad=1.0)
    plt.savefig(os.path.join(output_dir, f"{metric.lower().replace(' ', '_')}_boxplot.png"))
    plt.close()

print("✅ All similarity and complexity boxplots saved to:", output_dir)