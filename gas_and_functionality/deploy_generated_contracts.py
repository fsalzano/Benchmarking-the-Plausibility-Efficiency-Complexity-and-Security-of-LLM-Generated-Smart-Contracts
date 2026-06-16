import subprocess
import time
import pandas as pd
import json
import ast
from web3 import Web3


def start_ganache(port=8545, balance_eth=1000):
    try:
        command = [
            'ganache',
            '--port', str(port),
            '--defaultBalanceEther', str(balance_eth)
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(4)
        print(f"[🚀] Ganache started on port {port} with {balance_eth} ETH per account")
        return process
    except Exception as e:
        print(f"[❌] Failed to start Ganache: {e}")
        return None


def deploy_contract(web3, abi, bytecode):
    acct = web3.eth.accounts[0]
    web3.eth.default_account = acct
    print(f"[👤] Deployer account: {acct}")
    contract_factory = web3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = contract_factory.constructor().transact({'from': acct})
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"[✅] Contract deployed at {tx_receipt.contractAddress}")
    return tx_receipt.contractAddress


# Ground Truth JSON
json_with_gt_inputs = "gas_report_all_contracts_ground_truth.json"
gt_path = "./gt_contracts/compiled_gt_contracts.csv"

# Carica Ground Truth
gt = pd.read_csv(gt_path)
gt["filename"] = gt["filename"].astype(str)

# Dataset list
datasets = [
    {
        "name": "CodeLlama",
        "compiled_csv": "codellama_contracts/compiled_codellama_contracts.csv",
        "metadata_csv": "../scripts/codellama/codellama.csv",
        "output_json": "comparison_codellama.json"
    },
    {
        "name": "CodeLlama_RAG",
        "compiled_csv": "codellama_rag_contracts/compiled_codellama_rag_contracts.csv",
        "metadata_csv": "../scripts/codellama/codellama_with_rag.csv",
        "output_json": "comparison_codellama_rag.json"
    },
    {
        "name": "DeepSeek",
        "compiled_csv": "deepseek_coder_contracts/compiled_deepseek_coder_contracts.csv",
        "metadata_csv": "../scripts/deepseek/deepseek.csv",
        "output_json": "comparison_deepseek.json"
    },
    {
        "name": "DeepSeek_RAG",
        "compiled_csv": "deepseek_coder_rag_contracts/compiled_deepseek_coder_rag_contracts.csv",
        "metadata_csv": "../scripts/deepseek/deepseek_with_rag.csv",
        "output_json": "comparison_deepseek_rag.json"
    },
    {
        "name": "ChatGPT",
        "compiled_csv": "chatGPT_contracts/compiled_chatGPT_contracts.csv",
        "metadata_csv": "../scripts/ChatGPT/chatGPT.csv",
        "output_json": "comparison_chatgpt.json"
    },
    {
        "name": "ChatGPT_RAG",
        "compiled_csv": "chatGPT_rag_contracts/compiled_chatGPT_rag_contracts.csv",
        "metadata_csv": "../scripts/ChatGPT/chatGPT_with_rag.csv",
        "output_json": "comparison_chatgpt_rag.json"
    },
    {
        "name": "Gemini",
        "compiled_csv": "gemini_contracts/compiled_gemini_contracts.csv",
        "metadata_csv": "../scripts/Gemini/gemini.csv",
        "output_json": "comparison_gemini.json"
    },
    {
        "name": "Gemini_RAG",
        "compiled_csv": "gemini_rag_contracts/compiled_gemini_rag_contracts.csv",
        "metadata_csv": "../scripts/Gemini/gemini_with_rag.csv",
        "output_json": "comparison_gemini_rag.json"
    },
]

for dataset in datasets:
    print("\n" + "=" * 60)
    print(f"📦 Processing dataset: {dataset['name']}")
    print("=" * 60)

    # Load CSVs
    df = pd.read_csv(dataset["compiled_csv"])
    meta = pd.read_csv(dataset["metadata_csv"])

    df["contract"] = df["contract"].astype(str)
    df["bytecode"] = df["bytecode"].astype(str)
    df["abi"] = df["abi"].astype(str)
    meta["ID"] = meta["ID"].astype(str)
    meta["target_function"] = meta["target_function"].astype(str)

    filtered_df = df[df["contract"].str[0].str.isdigit()]

    results_summary = {}

    for idx, row in filtered_df.iterrows():
        contract_name = row["contract"]
        abi = row["abi"]
        bytecode = row["bytecode"]

        contract_id = contract_name.split(".")[0]

        if contract_id not in gt["filename"].values:
            print(f"Contract ID {contract_id} not in gt, skipping.\n")
            continue

        meta_row = meta[meta["ID"] == contract_id]
        if meta_row.empty:
            print(f"[⚠️] Contract ID {contract_id} not in metadata, skipping.\n")
            continue

        target_function = meta_row["target_function"].values[0]
        print(f"\n🎯 Target Function: {target_function}")

        ganache_proc = start_ganache()
        if ganache_proc is None:
            print("[❌] Skipping this contract due to Ganache startup failure.\n")
            continue

        try:
            web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
            if not web3.is_connected():
                print("[❌] Web3 connection failed, skipping.\n")
                continue

            try:
                parsed_abi = json.loads(abi)
            except json.JSONDecodeError:
                parsed_abi = ast.literal_eval(abi)
            try:
                contract_address = deploy_contract(web3, parsed_abi, bytecode)
            except:
                continue
            print(f"[✅] Deployed contract {contract_name} at {contract_address}")

            contract_instance = web3.eth.contract(address=contract_address, abi=parsed_abi)

            with open(json_with_gt_inputs) as f:
                gt_inputs_data = json.load(f)

            gt_entry = next(
                (item for item in gt_inputs_data if item.get("contract_id") == contract_id),
                None
            )

            if not gt_entry:
                print(f"[⚠️] Contract ID {contract_id} not found in {json_with_gt_inputs}, skipping.\n")
                continue

            all_samples = []
            for func_name, func_data in gt_entry.get("function_gas", {}).items():
                samples = func_data.get("samples", [])
                for s in samples:
                    all_samples.append(s)

            if not all_samples:
                print("[⚠️] No input samples found, skipping.\n")
                continue

            count_identical = 0
            count_different = 0
            total_gas = 0

            for s in all_samples:

                inputs = s["inputs"]
                expected_output = s.get("output")

                print(f"\n▶️ Calling {target_function}({inputs})")

                try:
                    method = getattr(contract_instance.functions, target_function)
                except:
                    print(f"[⚠️] Target function '{target_function}' not in ABI.")
                    continue

                try:
                    gas = method(*inputs).estimate_gas({'from': web3.eth.default_account})
                    result = method(*inputs).call({'from': web3.eth.default_account})
                    print(f"[✅] Output: {result}")
                    print(f"[⛽] Gas: {gas}")
                    total_gas += gas

                    if result == expected_output:
                        count_identical += 1
                        print("✅✅✅ Yessssss, outputs match!")
                    else:
                        count_different += 1
                        print(f"❌ Mismatch:\nGenerated: {result}\nExpected: {expected_output}")

                except Exception as e:
                    count_different += 1
                    print(f"[❌] Exception: {e}")

            results_summary[contract_id] = {
                "identical_outputs": count_identical,
                "different_outputs": count_different,
                "total_samples": len(all_samples),
                "total_gas": total_gas
            }

        finally:
            ganache_proc.terminate()
            print("[🛑] Ganache stopped.\n")

    # Save JSON per dataset
    with open(dataset["output_json"], "w") as f:
        json.dump(results_summary, f, indent=2)
        print(f"✅ Results saved to {dataset['output_json']}")
