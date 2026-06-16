import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', "cognitive_complexity"))
parent_dir2 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', "scripts", "metrics"))

sys.path.append(parent_dir)
sys.path.append(parent_dir2)

# add parents to sys.path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

if parent_dir2 not in sys.path:
    sys.path.insert(0, parent_dir2)

from cognitive_complexity import get_sc_cognitive_complexity
from scripts.metrics import cyclomatic_complexity, extract_function_of_interest_and_length

import pandas as pd

codellama_path = '../scripts/codellama/codellama.csv'
codellama_improved_comments_path = '../scripts/codellama/codellama_with_rag.csv'
codellama = pd.read_csv(codellama_path)
codellama_improved_comments = pd.read_csv(codellama_improved_comments_path)

deepseek_path = '../scripts/deepseek/deepseek.csv'
deepseek_improved_comments_path = '../scripts/deepseek/deepseek_with_rag.csv'
deepseek = pd.read_csv(deepseek_path)
deepseek_improved_comments = pd.read_csv(deepseek_improved_comments_path)

gemini_path = '../scripts/Gemini/gemini.csv'
gemini_improved_comments_path = '../scripts/Gemini/gemini_with_rag.csv'
gemini = pd.read_csv(gemini_path)
gemini_improved_comments = pd.read_csv(gemini_improved_comments_path)

gpt_path = '../scripts/ChatGPT/chatGPT.csv'
gpt_improved_comments_path = '../scripts/ChatGPT/chatGPT_with_rag.csv'
gpt = pd.read_csv(gpt_path)
gpt_improved_comments = pd.read_csv(gpt_improved_comments_path)


def complexity_codellama():
    for index, row in codellama.iterrows():
        solidity_code = row["CodeLLamaGenerated"]
        if "function" not in str(solidity_code):

            continue
        cognitive_complexities = get_sc_cognitive_complexity.analyze(solidity_code)
        codellama.at[index, 'CodeLLamaCognitiveComplexity'] = cognitive_complexities

        function, line_count = extract_function_of_interest_and_length.get_largest_function(solidity_code)
        cyclomatic_complex = cyclomatic_complexity.calculate_cyclomatic_complexity(function)
        codellama.at[index, 'CodeLLamaCyclomaticComplexity'] = cyclomatic_complex

    codellama.to_csv(codellama_path, index=False)

    for index, row in codellama_improved_comments.iterrows():
        solidity_code = row["CodeLLamaGenerated"]
        cognitive_complexities = get_sc_cognitive_complexity.analyze(solidity_code)
        codellama_improved_comments.at[index, 'CodeLLamaCognitiveComplexity'] = cognitive_complexities
        if "function" not in str(solidity_code):
            continue
        function, line_count = extract_function_of_interest_and_length.get_largest_function(solidity_code)
        cyclomatic_complex = cyclomatic_complexity.calculate_cyclomatic_complexity(function)
        codellama_improved_comments.at[index, 'CodeLLamaCyclomaticComplexity'] = cyclomatic_complex

    codellama_improved_comments.to_csv(codellama_improved_comments_path, index=False)


def complexity_deepseek():
    for index, row in deepseek.iterrows():
        solidity_code = row["DeepSeekGenerated"]
        cognitive_complexities = get_sc_cognitive_complexity.analyze(solidity_code)
        deepseek.at[index, 'DeepseekCognitiveComplexity'] = cognitive_complexities

        function, line_count = extract_function_of_interest_and_length.get_largest_function(solidity_code)
        cyclomatic_complex = cyclomatic_complexity.calculate_cyclomatic_complexity(function)
        deepseek.at[index, 'DeepseekCyclomaticComplexity'] = cyclomatic_complex

    deepseek.to_csv(deepseek_path, index=False)

    for index, row in deepseek_improved_comments.iterrows():
        solidity_code = row["DeepSeekGenerated"]
        cognitive_complexities = get_sc_cognitive_complexity.analyze(solidity_code)
        deepseek_improved_comments.at[index, 'DeepseekCognitiveComplexity'] = cognitive_complexities
        if "function" not in str(solidity_code):
            continue
        function, line_count = extract_function_of_interest_and_length.get_largest_function(solidity_code)
        cyclomatic_complex = cyclomatic_complexity.calculate_cyclomatic_complexity(function)
        deepseek_improved_comments.at[index, 'DeepseekCyclomaticComplexity'] = cyclomatic_complex

    deepseek_improved_comments.to_csv(deepseek_improved_comments_path, index=False)


def complexity_gemini():
    for index, row in gemini.iterrows():
        solidity_code = row["GeminiGenerated"]
        cognitive_complexities = get_sc_cognitive_complexity.analyze(solidity_code)
        gemini.at[index, 'GeminiCognitiveComplexity'] = cognitive_complexities

        function, line_count = extract_function_of_interest_and_length.get_largest_function(solidity_code)
        cyclomatic_complex = cyclomatic_complexity.calculate_cyclomatic_complexity(function)
        gemini.at[index, 'GeminiCyclomaticComplexity'] = cyclomatic_complex

    gemini.to_csv(gemini_path, index=False)

    for index, row in gemini_improved_comments.iterrows():
        solidity_code = row["GeminiGenerated"]
        cognitive_complexities = get_sc_cognitive_complexity.analyze(solidity_code)
        print(cognitive_complexities)
        gemini_improved_comments.at[index, 'GeminiCognitiveComplexity'] = str(cognitive_complexities)

        function, line_count = extract_function_of_interest_and_length.get_largest_function(solidity_code)
        cyclomatic_complex = cyclomatic_complexity.calculate_cyclomatic_complexity(function)
        gemini_improved_comments.at[index, 'GeminiCyclomaticComplexity'] = cyclomatic_complex

    gemini_improved_comments.to_csv(gemini_improved_comments_path, index=False)

def complexity_chatGPT():
    for index, row in gpt.iterrows():
        solidity_code = str(row["ChatGPTGenerated"])
        cognitive_complexities = get_sc_cognitive_complexity.analyze(solidity_code)
        gpt.at[index, 'GPTCognitiveComplexity'] = cognitive_complexities

        function, line_count = extract_function_of_interest_and_length.get_largest_function(solidity_code)
        cyclomatic_complex = cyclomatic_complexity.calculate_cyclomatic_complexity(function)
        gpt.at[index, 'GPTCyclomaticComplexity'] = cyclomatic_complex

    gpt.to_csv(gpt_path, index=False)

    for index, row in gpt_improved_comments.iterrows():
        solidity_code = str(row["ChatGPTGenerated"])
        cognitive_complexities = get_sc_cognitive_complexity.analyze(solidity_code)
        gpt_improved_comments.at[index, 'GPTCognitiveComplexity'] = cognitive_complexities

        function, line_count = extract_function_of_interest_and_length.get_largest_function(solidity_code)
        cyclomatic_complex = cyclomatic_complexity.calculate_cyclomatic_complexity(function)
        gpt_improved_comments.at[index, 'GPTCyclomaticComplexity'] = cyclomatic_complex

    gpt_improved_comments.to_csv(gpt_improved_comments_path, index=False)

def complexity_gt():
    for index, row in gt.iterrows():
        solidity_code = row["Contract"]
        cognitive_complexities = get_sc_cognitive_complexity.analyze(solidity_code)
        gt.at[index, 'CognitiveComplexity'] = cognitive_complexities

        function, line_count = extract_function_of_interest_and_length.get_largest_function(solidity_code)
        cyclomatic_complex = cyclomatic_complexity.calculate_cyclomatic_complexity(function)
        gt.at[index, 'CyclomaticComplexity'] = cyclomatic_complex

    gt.to_csv("../data/sample_of_interest.csv", index=False)


gt = pd.read_csv("../data/sample_of_interest.csv")

complexity_gt()
complexity_codellama()
complexity_deepseek()
complexity_chatGPT()
complexity_gemini()
