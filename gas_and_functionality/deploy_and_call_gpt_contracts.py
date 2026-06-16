import subprocess
import time
import pandas as pd
import json
import ast
import random
import string
import re
from itertools import product
from web3 import Web3
from eth_utils import to_checksum_address


def start_ganache(port=8545, balance_eth=1000):
    try:
        command = [
            'ganache',
            '--port', str(port),
            '--defaultBalanceEther', str(balance_eth)
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(3.5)
        print(f"[🚀] Ganache started on port {port} with {balance_eth} ETH per account")

        web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
        acct = web3.eth.accounts[0]
        balance = web3.eth.get_balance(acct)
        print(f"[💰] Account {acct} balance: {web3.from_wei(balance, 'ether')} ETH")

        return process
    except Exception as e:
        print(f"[❌] Failed to start Ganache: {e}")
        return None


def deploy_contract(web3, abi, bytecode):
    try:
        acct = web3.eth.accounts[0]
        web3.eth.default_account = acct
        print(f"[👤] Deployer account: {acct}")
        contract = web3.eth.contract(abi=abi, bytecode=bytecode)
        tx_hash = contract.constructor().transact({'from': acct})
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"[✅] Contract deployed at: {tx_receipt.contractAddress}")
        return tx_receipt.contractAddress, acct
    except Exception as e:
        print(f"[❌] Deployment failed: {e}")
        return None, None


def generate_inputs_for_type(param_type):
    def gen_bytes(n):
        return "0x" + ''.join(random.choice('0123456789abcdef') for _ in range(n * 2))

    def wrap_array(elem_cases):
        return [elem_cases[i % len(elem_cases)] for i in range(random.randint(1, 3))]

    if param_type.endswith("]"):
        base_type = param_type[:param_type.find("[")]
        base_cases = generate_inputs_for_type(base_type)
        return [[], wrap_array(base_cases)]
    if re.match(r"^uint(\d+)?$", param_type):
        max_val = 2 ** (256 - 1) - 1
        return [max_val, 0] + [random.randint(1, 99) for _ in range(10)]
    if re.match(r"^int(\d+)?$", param_type):
        bits = int(re.findall(r"\d+", param_type)[0]) if re.findall(r"\d+", param_type) else 256
        max_val = 2 ** (bits - 1) - 1
        min_val = -2 ** (bits - 1)
        return [0, 1, -1, 50, min_val, max_val] + [random.randint(min_val, max_val) for _ in range(4)]
    if param_type == "bool":
        return [True, False]
    if param_type == "address":
        cases = [
            Web3.to_checksum_address("0xAb5801a7D398351b8bE11C439e05C5b3259aec9B"),
            Web3.to_checksum_address("0x0000000000000000000000000000000000000001")
        ]
        while len(cases) < 10:
            rand = ''.join(random.choices("0123456789abcdef", k=40))
            cases.append(Web3.to_checksum_address("0x" + rand))
        return cases
    if param_type.startswith("bytes") and param_type != "bytes":
        size = int(param_type[5:])
        return ["0x" + "00" * size, "0x" + "ff" * size] + [gen_bytes(size) for _ in range(8)]
    if param_type == "bytes":
        return ["0x", "0x68656c6c6f20776f726c64"] + [gen_bytes(random.randint(1, 32)) for _ in range(8)]
    if param_type == "string":
        return ["", "Hello", "Solidity", "test"] + [''.join(random.choices(string.ascii_letters, k=8)) for _ in range(6)]
    if param_type in ["fixed", "ufixed"]:
        return ["0", "1.0", "3.14"] + [str(round(random.uniform(0, 1000), 5)) for _ in range(7)]
    return [0]


def call_target_function(contract_instance, function_name, web3, sender, verbose=True):
    results = []
    func_abi = next((f for f in contract_instance.abi if f.get("type") == "function" and f["name"] == function_name), None)
    if not func_abi:
        print(f"[⚠️] Function '{function_name}' not found in ABI.")
        return results

    try:
        method = getattr(contract_instance.functions, function_name)
        input_types = [param["type"] for param in func_abi["inputs"]]
        arg_variants = [generate_inputs_for_type(t) for t in input_types]
        arg_sets = list(product(*arg_variants))
        test_inputs = arg_sets[:2] + random.sample(arg_sets, min(10, len(arg_sets)))

        for args in test_inputs:
            entry = {"inputs": args}
            try:
                gas = method(*args).estimate_gas({'from': sender})
                entry["gas"] = gas
                try:
                    result = method(*args).call({'from': sender})
                    entry["output"] = result
                    entry["success"] = True
                except Exception as call_error:
                    entry["output"] = "error"
                    entry["success"] = False
                    entry["error_message"] = str(call_error)
            except Exception as e:
                entry["gas"] = None
                entry["output"] = "error"
                entry["success"] = False
                entry["error_message"] = str(e)

                if verbose:
                    print(f"❌ {function_name}({args}) failed: {e}")
            results.append(entry)
    except Exception as e:
        print(f"[❌] Failed to prepare function {function_name}: {e}")
    return results


def main():
    csv_path = "./chatGPT_contracts/compiled_chatGPT_contracts.csv"
    ground_truth_path = "../scripts/ChatGPT/chatGPT.csv"

    df = pd.read_csv(csv_path)
    df = df[df["abi"].notnull() & df["bytecode"].notnull()]
    if df.empty:
        print("[⚠️] No valid contracts found.")
        return

    ground_truth = pd.read_csv(ground_truth_path)
    ground_truth["ID"] = ground_truth["ID"].astype(str)
    id_to_target = dict(zip(ground_truth["ID"], ground_truth["target_function"]))

    all_reports = []

    for idx, row in df.iterrows():
        abi_str = row['abi']
        if not abi_str or len(abi_str.strip()) == 0:
            continue
        try:
            abi = json.loads(abi_str)
        except json.JSONDecodeError:
            try:
                abi = ast.literal_eval(abi_str)
            except:
                continue

        bytecode = row['bytecode']
        contract_name = str(row.get("full_name", f"Contract_{idx}"))
        if "safemath" in str(contract_name).lower():
            continue

        print(f"\n📦 Processing: {contract_name}")

        target_function = None
        contract_id = None
        if contract_name[0].isdigit():
            contract_id = contract_name.split(".")[0]
            target_function = id_to_target.get(contract_id)
            print(f"🎯 Target function for ID {contract_id}: {target_function}")

        ganache_proc = start_ganache()
        if ganache_proc is None:
            continue

        try:
            web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
            if not web3.is_connected():
                continue

            contract_address, deployer = deploy_contract(web3, abi, bytecode)
            if not contract_address:
                continue

            web3.eth.default_account = deployer
            contract_instance = web3.eth.contract(address=contract_address, abi=abi)

            gas_data = {}
            if target_function:
                print(f"▶️ Calling function: {target_function}")
                gas_data[target_function] = {
                    "samples": call_target_function(contract_instance, target_function, web3, sender=deployer)
                }

            report = {
                "contract_name": contract_name,
                "contract_id": contract_id,
                "target_function": target_function,
                "function_gas": gas_data
            }

            # Try serializing report first
            try:
                test_json = json.dumps(report, indent=2)
                all_reports.append(report)
                with open("gas_report_all_contracts_gpt.json", "w") as f:
                    json.dump(all_reports, f, indent=2)
                print(f"[💾] Report saved for {contract_name}")
            except Exception as e:
                print(f"[⚠️] Skipped appending report due to serialization error: {e}")

        finally:
            ganache_proc.terminate()
            print("[🛑] Ganache stopped")


if __name__ == "__main__":
    main()
