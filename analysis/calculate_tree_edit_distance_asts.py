import pandas as pd
import sys
import os
import json
import re

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', "scripts"))
sys.path.insert(0, parent_dir)
parent_dir2 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', "scripts", "metrics"))

sys.path.append(parent_dir)
sys.path.append(parent_dir2)

# add parents to sys.path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

if parent_dir2 not in sys.path:
    sys.path.insert(0, parent_dir2)

from scripts.metrics import tree_edit_distance_calculator


def fix_broken_quotes(input_string):
    """
    Fix contractions like it"s to it's.
    This helps make the string valid for JSON parsing.
    """
    # This regex finds words followed by "s (a contraction issue caused by escaping problems)
    return re.sub(r'(\w)"s', r"\1's", input_string)


def clean_decl_entries(input_string):
    """
    1. Replace 'decl' and 'iden' entries where the value is a parser object with an empty string.
    2. Fix broken contractions like it"s -> it's, can"t -> can't, won"t -> won't.

    Example:
    "decl": <solidity_parser...>  ->  "decl": ""
    "iden": <solidity_parser...>  ->  "iden": ""
    "value": "it"s a test"        ->  "value": "it's a test"
    """

    # Patterns for cleaning "decl" and "iden"
    patterns = [
        (r'("decl"\s*:\s*)<[^>]*>', r'\1""'),  # Remove parser object from "decl"
        (r'("iden"\s*:\s*)<[^>]*>', r'\1""')  # Remove parser object from "iden"
    ]

    # Apply decl/iden replacements
    cleaned_string = input_string
    for pattern, replacement in patterns:
        cleaned_string = re.sub(pattern, replacement, cleaned_string)

    # Fix contractions like it"s -> it's, can"t -> can't, etc.
    cleaned_string = re.sub(r'(\w)"(s|t|re|ve|m|ll|d)\b', r"\1'\2", cleaned_string)

    return cleaned_string


def preprocess_ast_string(ast_string):
    """
    Preprocesses the AST string to convert it into valid JSON format.
    - Replaces single quotes with double quotes.
    - Ensures any existing double quotes inside strings are escaped properly.
    """
    if isinstance(ast_string, str):
        # Replace single quotes with double quotes
        ast_string = ast_string.replace("'", '"')
        # Ensure the string is valid JSON by escaping quotes inside strings
        return ast_string
    return ast_string


def clean(ast):
    ast = (str(ast).replace("'", '"').replace("None", '"None"').replace("False", '"False"').replace("True",
                                                                                                    '"True"').replace(
        '""True', "").replace('""False', ""))
    ast = (clean_decl_entries(ast).replace('""None""', '"None"').replace('Invitee"s', 'Invitee\'s')
    .replace('Cannot reclaim tokens from this contract"s address',
             'Cannot reclaim tokens from this contract\'s address').replace('Invalid new owner"s address',
                                                                            'Invalid new owner\'s address').replace(
        'while it"s', 'while it\'s address').replace('loans in "lent"', 'loans in lent').replace(
        'must be in the "ended"', 'must be in the ended'))
    return ast


gt = pd.read_csv("../data/sample_of_interest.csv")
deepseek_path = '../scripts/deepseek/deepseek.csv'
deepseek_improved_comments_path = '../scripts/deepseek/deepseek_with_rag.csv'
deepseek = pd.read_csv(deepseek_path)
deepseek_improved_comments = pd.read_csv(deepseek_improved_comments_path)

codellama_path = '../scripts/codellama/codellama.csv'
codellama_improved_comments_path = '../scripts/codellama/codellama_with_rag.csv'
codellama = pd.read_csv(codellama_path)
codellama_improved_comments = pd.read_csv(codellama_improved_comments_path)

gemini_path = '../scripts/Gemini/gemini.csv'
gemini_improved_comments_path = '../scripts/Gemini/gemini_with_rag.csv'
gemini = pd.read_csv(gemini_path)
gemini_improved_comments = pd.read_csv(gemini_improved_comments_path)

gpt_path = '../scripts/ChatGPT/chatGPT.csv'
gpt_improved_comments_path = '../scripts/ChatGPT/chatGPT_with_rag.csv'
gpt = pd.read_csv(gpt_path)
gpt_improved_comments = pd.read_csv(gpt_improved_comments_path)

datasets = {
    "gt": gt,
    "deepseek": deepseek,
    "deepseek_improved_comments": deepseek_improved_comments,
    "codellama": codellama,
    "codellama_improved_comments": codellama_improved_comments,
    "gemini": gemini,
    "gemini_improved_comments": gemini_improved_comments,
    "gpt": gpt,
    "gpt_improved_comments": gpt_improved_comments
}

# Fill 'ast' column with '{}' if NaN or empty
for name, df in datasets.items():
    if 'ast' in df.columns:
        df['ast'] = df['ast'].fillna('{}')  # Replace NaN
        df['ast'] = df['ast'].replace('', '{}')  # Replace empty strings
    else:
        print(f"Warning: Dataset '{name}' does not have 'ast' column.")

for index, row in gt.iterrows():
    try:
        # Preprocess and parse AST strings
        gt_ast = preprocess_ast_string(row["ast"])
        codellama_ast = preprocess_ast_string(codellama.loc[index, "ast"])
        deepseek_ast = preprocess_ast_string(deepseek.loc[index, "ast"])
        chatGPT_ast = preprocess_ast_string(gpt.loc[index, "ast"])
        gemini_ast = preprocess_ast_string(gemini.loc[index, "ast"])

        codellama_improved_comments_ast = preprocess_ast_string(codellama_improved_comments.loc[index, "ast"])
        deepseek_improved_comments_ast = preprocess_ast_string(deepseek_improved_comments.loc[index, "ast"])
        chatGPT_improved_comments_ast = preprocess_ast_string(gpt_improved_comments.loc[index, "ast"])
        gemini_improved_comments_ast = preprocess_ast_string(gemini_improved_comments.loc[index, "ast"])

        gt_ast = clean(gt_ast)
        deepseek_ast = clean(deepseek_ast)
        codellama_ast = clean(codellama_ast)
        chatGPT_ast = clean(chatGPT_ast)
        gemini_ast = clean(gemini_ast)

        deepseek_improved_comments_ast = clean(deepseek_improved_comments_ast)
        codellama_improved_comments_ast = clean(codellama_improved_comments_ast)
        chatGPT_improved_comments_ast = clean(chatGPT_improved_comments_ast)
        gemini_improved_comments_ast = clean(gemini_improved_comments_ast)
        if "function()externalpayable" in gt_ast or '"When "_preventLocking" is true,' in gt_ast:
            continue
        gt_ast = json.loads(gt_ast)
        deepseek_ast = json.loads(deepseek_ast)
        codellama_ast = json.loads(codellama_ast)
        chatGPT_ast = json.loads(chatGPT_ast)
        gemini_ast = json.loads(gemini_ast)
        deepseek_improved_comments_ast=deepseek_improved_comments_ast.replace(' "to" pledge', ' to pledge').replace('"from" pledge', 'from pledge')
        try:
            deepseek_improved_comments_ast = json.loads(deepseek_improved_comments_ast)
        except:
            print(deepseek_improved_comments_ast)


        codellama_improved_comments_ast = json.loads(codellama_improved_comments_ast)
        chatGPT_improved_comments_ast = json.loads(chatGPT_improved_comments_ast)
        gemini_improved_comments_ast = json.loads(gemini_improved_comments_ast)

        deepseek_ted = tree_edit_distance_calculator.calculate_ted(gt_ast, deepseek_ast)
        codellama_ted = tree_edit_distance_calculator.calculate_ted(gt_ast, codellama_ast)
        chatGPT_ted = tree_edit_distance_calculator.calculate_ted(gt_ast, chatGPT_ast)
        gemini_ted = tree_edit_distance_calculator.calculate_ted(gt_ast, gemini_ast)

        deepseek_improved_ted = tree_edit_distance_calculator.calculate_ted(gt_ast, deepseek_improved_comments_ast)
        codellama_improved_ted = tree_edit_distance_calculator.calculate_ted(gt_ast, codellama_improved_comments_ast)
        chatGPT_improved_ted = tree_edit_distance_calculator.calculate_ted(gt_ast, chatGPT_improved_comments_ast)
        gemini_improved_ted = tree_edit_distance_calculator.calculate_ted(gt_ast, gemini_improved_comments_ast)

        codellama.at[index, "TED"] = codellama_ted
        deepseek.at[index, "TED"] = deepseek_ted
        gemini.at[index, "TED"] = gemini_ted
        gpt.at[index, "TED"] = chatGPT_ted

        codellama_improved_comments.at[index, "TED"] = codellama_improved_ted
        deepseek_improved_comments.at[index, "TED"] = deepseek_improved_ted
        gemini_improved_comments.at[index, "TED"] = gemini_improved_ted
        gpt_improved_comments.at[index, "TED"] = chatGPT_improved_ted

    except KeyError as e:
        print(f"Missing column error at index {index}: {e}")

codellama.to_csv(codellama_path, index=False)
deepseek.to_csv(deepseek_path, index=False)
gemini.to_csv(gemini_path, index=False)
gpt.to_csv(gpt_path, index=False)

codellama_improved_comments.to_csv(codellama_improved_comments_path, index=False)
deepseek_improved_comments.to_csv(deepseek_improved_comments_path, index=False)
gemini_improved_comments.to_csv(gemini_improved_comments_path, index=False)
gpt_improved_comments.to_csv(gpt_improved_comments_path, index=False)
