import json
import os

# List of JSON paths (add or remove as needed)
json_files = [
    "correctness_summaries/comparison_chatgpt.json",
    "correctness_summaries/comparison_codellama_rag.json",
    "correctness_summaries/comparison_gemini_rag.json",
    "correctness_summaries/comparison_gemini.json",
    "correctness_summaries/comparison_deepseek.json",
    "correctness_summaries/comparison_deepseek_rag.json",
    "correctness_summaries/comparison_codellama.json",
    "correctness_summaries/comparison_chatgpt_rag.json"
]

# Ensure the output folder exists
output_dir = "correctness_summaries"
os.makedirs(output_dir, exist_ok=True)

for json_path in json_files:
    if not os.path.exists(json_path):
        print(f"[⚠️] File not found: {json_path}, skipping.\n")
        continue

    print(f"\n📂 Processing file: {json_path}")

    with open(json_path) as f:
        data = json.load(f)

    total_functions = 0
    total_correct_outputs = 0
    total_incorrect_outputs = 0
    perfectly_correct_instances = 0
    contracts_summary = []

    for contract_id, results in data.items():
        ident = results["identical_outputs"]
        diff = results["different_outputs"]
        total = results["total_samples"]

        total_functions += 1
        total_correct_outputs += ident
        total_incorrect_outputs += diff

        correctness_rate = ident / total if total > 0 else 0

        if ident == total:
            perfectly_correct_instances += 1

        contracts_summary.append({
            "contract_id": contract_id,
            "identical_outputs": ident,
            "different_outputs": diff,
            "total_samples": total,
            "correctness_rate": correctness_rate
        })

    # Compute overall metrics
    total_samples = total_correct_outputs + total_incorrect_outputs
    overall_accuracy = total_correct_outputs / total_samples if total_samples > 0 else 0
    percent_perfectly_correct = perfectly_correct_instances / total_functions if total_functions > 0 else 0

    # Print detailed results
    print("\n✅ Overall Correctness Summary:")
    print(f"   Total contracts evaluated: {total_functions}")
    print(f"   Total samples: {total_samples}")
    print(f"   Total correct outputs: {total_correct_outputs}")
    print(f"   Total incorrect outputs: {total_incorrect_outputs}")
    print(f"   Overall accuracy: {overall_accuracy*100:.2f}%")
    print(f"   Contracts with 100% accuracy: {perfectly_correct_instances} ({percent_perfectly_correct*100:.2f}%)")

    # Prepare the summary dictionary
    summary_output = {
        "total_functions": total_functions,
        "total_samples": total_samples,
        "total_correct_outputs": total_correct_outputs,
        "total_incorrect_outputs": total_incorrect_outputs,
        "overall_accuracy": overall_accuracy,
        "percent_perfectly_correct_contracts": percent_perfectly_correct,
        "perfectly_correct_contracts": perfectly_correct_instances,
        "per_contract": contracts_summary
    }

    # Write summary to file
    basename = os.path.basename(json_path).replace(".json", "")
    output_path = os.path.join(output_dir, f"{basename}_summary.json")

    with open(output_path, "w") as out_f:
        json.dump(summary_output, out_f, indent=2)

    print(f"\n💾 Saved summary to {output_path}")