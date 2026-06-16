import os
import re
import json
import time
import pandas as pd
from solcx import (
    compile_files,
    install_solc,
    get_installed_solc_versions,
    set_solc_version,
    get_compilable_solc_versions
)
from packaging import version
from dotenv import load_dotenv

load_dotenv()

# List of folders to compile contracts from (gt_contracts removed)
dirs = {
    "chatGPT_path": "chatGPT_contracts",
    "chatGPT_rag_path": "chatGPT_rag_contracts",
    "gemini_path": "gemini_contracts",
    "gemini_rag_path": "gemini_rag_contracts",
    "codellama_path": "codellama_contracts",
    "codellama_rag_path": "codellama_rag_contracts",
    "deepseek_path": "deepseek_coder_contracts",
    "deepseek_rag_path": "deepseek_coder_rag_contracts"
}

compiled_contracts_all = []


# Extract Solidity version from pragma directive
def extract_solidity_version(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.search(r'pragma\s+solidity\s+([^;]+);', line)
            if match:
                return match.group(1).strip()
    return None


# Resolve a compatible solc version based on pragma constraints
def resolve_version_range(version_expr):
    available_versions = sorted(get_compilable_solc_versions())
    expr = version_expr.replace(' ', '')
    constraints = re.findall(r'[\^<>=]*\d+\.\d+(?:\.\d+)?', expr)

    def is_compatible(ver):
        for constraint in constraints:
            if constraint.startswith('^'):
                base = version.parse(constraint[1:])
                upper = version.parse(f"{base.major + 1}.0.0")
                if not (base <= ver < upper):
                    return False
            elif constraint.startswith(">="):
                if ver < version.parse(constraint[2:]):
                    return False
            elif constraint.startswith("<="):
                if ver > version.parse(constraint[2:]):
                    return False
            elif constraint.startswith(">"):
                if ver <= version.parse(constraint[1:]):
                    return False
            elif constraint.startswith("<"):
                if ver >= version.parse(constraint[1:]):
                    return False
            else:
                if ver != version.parse(constraint):
                    return False
        return True

    compatible_versions = [v for v in available_versions if is_compatible(v)]
    return str(compatible_versions[-1]) if compatible_versions else None


# Compile Solidity file with correct compiler version
def compile_contract(file_path, file_label, compiler_version):
    try:
        if compiler_version not in get_installed_solc_versions():
            install_solc(compiler_version)
        set_solc_version(compiler_version)

        contract_dir = os.path.dirname(file_path)  # directory of the .sol file
        node_modules_path = os.path.abspath(os.path.join(contract_dir, "node_modules"))

        contracts = compile_files(
            [file_path],
            output_values=["abi", "bin"],
            allow_paths=[contract_dir, node_modules_path],
            base_path=contract_dir  # very important!
        )

        for contract_name, contract_data in contracts.items():
            compiled_contracts_all.append({
                "filename": file_label,
                "contract": contract_name,
                "abi": json.dumps(contract_data["abi"]),
                "bytecode": contract_data["bin"]
            })

    except Exception as e:
        print(f"[❌] Compilation failed for {file_label} ({compiler_version}): {e}")


# Main loop: compile all .sol files in all directories
def main():
    for label, folder in dirs.items():
        print(f"\n📁 Scanning folder: {folder}")
        folder_path = os.path.abspath(folder)
        if not os.path.exists(folder_path):
            print(f"[⚠️] Folder not found: {folder_path}")
            continue

        for filename in os.listdir(folder_path):
            if filename.endswith(".sol"):
                file_path = os.path.join(folder_path, filename)
                pragma_expr = extract_solidity_version(file_path)
                if not pragma_expr:
                    print(f"[⚠️] No pragma found in {filename}, skipping.")
                    continue
                solc_version = resolve_version_range(pragma_expr)
                if not solc_version:
                    print(f"[⚠️] No compatible version for {filename} ({pragma_expr})")
                    continue

                print(f"🔧 Compiling {filename} with Solidity {solc_version} (pragma: {pragma_expr})")
                compile_contract(file_path, filename, solc_version)

        # Save compiled contracts for this folder
        output_df = pd.DataFrame([
            c for c in compiled_contracts_all if c["filename"] in os.listdir(folder)
        ])
        if not output_df.empty:
            output_csv = os.path.join(folder, f"compiled_{folder}.csv")
            output_df.to_csv(output_csv, index=False)
            print(f"[💾] Saved {len(output_df)} contracts to {output_csv}")


if __name__ == "__main__":
    main()
