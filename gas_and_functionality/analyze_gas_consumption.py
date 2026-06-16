import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# === Generated JSON paths ===
generated_json_paths = {
    "ChatGPT-4o Baseline": "functional_correctness_results/comparison_chatgpt.json",
    "ChatGPT-4o RAG": "functional_correctness_results/comparison_chatgpt_rag.json",
    "CodeLlama Baseline": "functional_correctness_results/comparison_codellama.json",
    "CodeLlama RAG": "functional_correctness_results/comparison_codellama_rag.json",
    "DeepSeek Baseline": "functional_correctness_results/comparison_deepseek.json",
    "DeepSeek RAG": "functional_correctness_results/comparison_deepseek_rag.json",
    "Gemini Baseline": "functional_correctness_results/comparison_gemini.json",
    "Gemini RAG": "functional_correctness_results/comparison_gemini_rag.json",
}

gas_data = []

# === Parse each JSON file ===
for label, path in generated_json_paths.items():
    try:
        with open(path) as f:
            comparison_data = json.load(f)

        model, version = label.split(" ", 1)

        for func_id, info in comparison_data.items():
            total_gas = info.get("total_gas", 0)
            total_samples = info.get("total_samples", 0)

            if total_gas > 0 and total_samples > 0:
                mean_gas = total_gas / total_samples
                gas_data.append({
                    "Model": model,
                    "Mode": version,
                    "Gas": mean_gas
                })

    except Exception as e:
        print(f"[❌] Failed to process {label}: {e}")

# === Convert to DataFrame ===
df_gas = pd.DataFrame(gas_data)

# === Output path ===
output_dir = "../analysis/BOXPLOT"
os.makedirs(output_dir, exist_ok=True)

# === Plot gas boxplot ===
if not df_gas.empty:
    plt.figure(figsize=(9, 5))
    sns.boxplot(
        data=df_gas,
        x="Model",
        y="Gas",
        hue="Mode",
        dodge=0.4,
        width=0.7,
        linewidth=1
    )

    # Move legend above the plot, horizontal and compact
    plt.legend(
        title="",
        loc="upper center",
        bbox_to_anchor=(0.5, 1.25),
        ncol=2,
        frameon=False
    )

    plt.title("Gas Usage by Model")
    plt.xlabel("Model")
    plt.ylabel("Gas")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "gas_boxplot.png"))
    plt.close()
    print("✅ Saved: gas_boxplot.png")
else:
    print("⚠️ No gas data to plot.")
