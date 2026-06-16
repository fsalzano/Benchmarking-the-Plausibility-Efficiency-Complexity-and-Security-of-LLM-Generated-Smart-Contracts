import pandas as pd
import re
from scripts.metrics import extract_function_of_interest_and_length


def extract_function_name(code):
    match = re.search(r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', str(code))
    return match.group(1) if match else None


codellama_path = '../codellama/codellama.csv'
codellama_improved_comments_path = '../codellama/codellama_with_rag.csv'
codellama = pd.read_csv(codellama_path)
codellama_improved_comments = pd.read_csv(codellama_improved_comments_path)

deepseek_path = '../deepseek/deepseek.csv'
deepseek_improved_comments_path = '../deepseek/deepseek_with_rag.csv'
deepseek = pd.read_csv(deepseek_path)
deepseek_improved_comments = pd.read_csv(deepseek_improved_comments_path)

gemini_path = '../Gemini/gemini.csv'
gemini_improved_comments_path = '../Gemini/gemini_with_rag.csv'
gemini = pd.read_csv(gemini_path)
gemini_improved_comments = pd.read_csv(gemini_improved_comments_path)

gpt_path = '../ChatGPT/chatGPT.csv'
gpt_improved_comments_path = '../ChatGPT/chatGPT_with_rag.csv'
gpt = pd.read_csv(gpt_path)
gpt_improved_comments = pd.read_csv(gpt_improved_comments_path)

gt_path = '../../data/sample_of_interest.csv'
gt = pd.read_csv(gt_path)

for index, row in gt.iterrows():
    solidity_code = row["FormattedCode"]
    if "function" not in str(solidity_code):
        continue

    function, line_count = extract_function_of_interest_and_length.get_largest_function(solidity_code)

    target_function = extract_function_name(function)
    gt.at[index, 'target_function'] = target_function
gt.to_csv(gt_path, index=False)

for index, row in codellama.iterrows():
    solidity_code = row["CodeLLamaGenerated"]
    if "function" not in str(solidity_code):
        continue

    function, line_count = extract_function_of_interest_and_length.get_largest_function(solidity_code)

    target_function = extract_function_name(function)
    codellama.at[index, 'target_function'] = target_function
codellama.to_csv(codellama_path, index=False)

for index, row in codellama_improved_comments.iterrows():
    solidity_code = row["CodeLLamaGenerated"]
    if "function" not in str(solidity_code):
        continue

    function, line_count = extract_function_of_interest_and_length.get_largest_function(solidity_code)

    target_function = extract_function_name(function)
    codellama_improved_comments.at[index, 'target_function'] = target_function
codellama_improved_comments.to_csv(codellama_improved_comments_path, index=False)

for index, row in gpt.iterrows():
    solidity_code = row["ChatGPTGenerated"]
    if "function" not in str(solidity_code):
        continue

    function, line_count = extract_function_of_interest_and_length.get_largest_function(solidity_code)

    target_function = extract_function_name(function)
    gpt.at[index, 'target_function'] = target_function
gpt.to_csv(gpt_path, index=False)

for index, row in gpt_improved_comments.iterrows():
    solidity_code = row["ChatGPTGenerated"]
    if "function" not in str(solidity_code):
        continue

    function, line_count = extract_function_of_interest_and_length.get_largest_function(solidity_code)

    target_function = extract_function_name(function)
    gpt_improved_comments.at[index, 'target_function'] = target_function
gpt_improved_comments.to_csv(gpt_improved_comments_path, index=False)

for index, row in gemini.iterrows():
    solidity_code = row["GeminiGenerated"]
    if "function" not in str(solidity_code):
        continue

    function, line_count = extract_function_of_interest_and_length.get_largest_function(solidity_code)

    target_function = extract_function_name(function)
    gemini.at[index, 'target_function'] = target_function
gemini.to_csv(gemini_path, index=False)

for index, row in gemini_improved_comments.iterrows():
    solidity_code = row["GeminiGenerated"]
    if "function" not in str(solidity_code):
        continue

    function, line_count = extract_function_of_interest_and_length.get_largest_function(solidity_code)

    target_function = extract_function_name(function)
    gemini_improved_comments.at[index, 'target_function'] = target_function
gemini_improved_comments.to_csv(gemini_improved_comments_path, index=False)

for index, row in deepseek.iterrows():
    solidity_code = row["DeepSeekGenerated"]
    if "function" not in str(solidity_code):
        continue

    function, line_count = extract_function_of_interest_and_length.get_largest_function(solidity_code)

    target_function = extract_function_name(function)
    deepseek.at[index, 'target_function'] = target_function
deepseek.to_csv(deepseek_path, index=False)

for index, row in deepseek_improved_comments.iterrows():
    solidity_code = row["DeepSeekGenerated"]
    if "function" not in str(solidity_code):
        continue

    function, line_count = extract_function_of_interest_and_length.get_largest_function(solidity_code)

    target_function = extract_function_name(function)
    deepseek_improved_comments.at[index, 'target_function'] = target_function
deepseek_improved_comments.to_csv(deepseek_improved_comments_path, index=False)
