import os
import re
import pandas as pd

def extract_contracts_from_folder(folder_path):
    sol_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".sol"):
                sol_files.append(os.path.join(root, file))
    return sol_files

def extract_functions_with_comments(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # Extract contract name
    contract_match = re.search(r'\bcontract\s+(\w+)', code)
    contract_name = contract_match.group(1) if contract_match else 'Unknown'

    # Improved pattern: tightly couples comment block and function
    pattern = re.compile(
        r'(?:\/\*\*[\s\S]*?\*\/|\/\/\/[^\n]*\n)\s*'  # match comment block (non-capturing)
        r'(function\s+\w+\s*\([^\)]*\)\s*(public|external|internal|private)?[\s\S]*?{[\s\S]*?})',
        re.MULTILINE
    )

    entries = []

    for match in pattern.finditer(code):
        full_match = match.group(0)
        function_code = match.group(1).strip()

        # Extract preceding comment
        comment_match = re.search(r'(\/\*\*[\s\S]*?\*\/|\/\/\/[^\n]*(\n|$))+', full_match)
        comment_block = comment_match.group(0).strip() if comment_match else ''

        # Extract function name
        fn_match = re.search(r'function\s+(\w+)', function_code)
        function_name = fn_match.group(1) if fn_match else 'Unknown'

        # Extract @notice line
        notice_match = re.search(r'@notice\s+(.*)', comment_block)
        notice_comment = notice_match.group(1).strip() if notice_match else ''

        entries.append({
            'contract_name': contract_name,
            'function_name': function_name,
            'full_comment': comment_block,
            'notice_comment': notice_comment,
            'function_code': function_code
        })

    return entries

def create_dataset_from_contracts(folder_path, output_csv='functions_dataset.csv', output_csv_only_with_notices='functions_dataset_only_notices.csv'):
    all_entries = []
    sol_files = extract_contracts_from_folder(folder_path)

    for file_path in sol_files:
        entries = extract_functions_with_comments(file_path)
        all_entries.extend(entries)

    df = pd.DataFrame(all_entries)

    # Remove entries with empty or whitespace-only full_comment
    df['full_comment'] = df['full_comment'].astype(str).str.strip()
    df = df[df['full_comment'] != '']

    # Save all functions that have at least a comment
    df.to_csv(output_csv, index=False)
    print(f"Saved dataset with {len(df)} entries (with any comment) to {output_csv}")

    # Filter only functions with non-empty @notice comments
    df_notice = df[df['notice_comment'].astype(str).str.strip() != '']
    df_notice.to_csv(output_csv_only_with_notices, index=False)
    print(f"Saved dataset with {len(df_notice)} entries (with @notice) to {output_csv_only_with_notices}")

# Example usage
create_dataset_from_contracts('Ethereum_smart_contract_dataset/Ethereum_smart_contract_datast/contract_dataset_ethereum/')
