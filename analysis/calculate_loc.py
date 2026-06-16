import pandas as pd
import sys
import os

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

from scripts.metrics import extract_function_of_interest_and_length


def calculate_gt_loc():
    for index, row in gt.iterrows():
        largest_func_content, line_count = extract_function_of_interest_and_length.get_largest_function(row["Contract"])

        # loc = compute_loc(function)
        gt.at[index, 'loc'] = line_count

    gt.to_csv('../data/sample_of_interest.csv', index=False)


def calculate_codellama_loc():
    for index, row in codellama.iterrows():
        generated = str(row["CodeLLamaGenerated"])
        largest_func_content, line_count = extract_function_of_interest_and_length.get_largest_function(generated)

        codellama.at[index, 'CodellamaGeneratedLoc'] = line_count
    codellama.to_csv(codellama_path, index=False)

    for index, row in codellama_improved_comments.iterrows():
        generated = str(row["CodeLLamaGenerated"])
        largest_func_content, line_count = extract_function_of_interest_and_length.get_largest_function(generated)

        codellama_improved_comments.at[index, 'CodellamaGeneratedLoc'] = line_count
        codellama_improved_comments.at[index, 'CodellamaGeneratedFunctionBody'] = largest_func_content
    codellama_improved_comments.to_csv(codellama_improved_comments_path, index=False)


def calculate_deepseek_loc():
    for index, row in deepseek.iterrows():
        generated = row["DeepSeekGenerated"]
        largest_func_content, line_count = extract_function_of_interest_and_length.get_largest_function(generated)


        deepseek.at[index, 'DeepseekGeneratedLoc'] = line_count
        deepseek.at[index, 'DeepseekGeneratedFunctionBody'] = largest_func_content

    deepseek.to_csv(deepseek_path, index=False)

    for index, row in deepseek_improved_comments.iterrows():
        generated = row["DeepSeekGenerated"]
        if "Error: 500" in str(generated):
            line_count=-1
            largest_func_content=""
            deepseek_improved_comments.at[index, 'DeepseekGeneratedLoc'] = line_count
            deepseek_improved_comments.at[index, 'DeepseekGeneratedFunctionBody'] = largest_func_content
            continue

        largest_func_content, line_count = extract_function_of_interest_and_length.get_largest_function(str(generated))
       # print(largest_func_content)

        deepseek_improved_comments.at[index, 'DeepseekGeneratedLoc'] = line_count
        deepseek_improved_comments.at[index, 'DeepseekGeneratedFunctionBody'] = largest_func_content

    deepseek_improved_comments.to_csv(deepseek_improved_comments_path, index=False)


def calculate_gemini_loc():
    for index, row in gemini.iterrows():
        generated = row["GeminiGenerated"]
        largest_func_content, line_count = extract_function_of_interest_and_length.get_largest_function(generated)
       # print(largest_func_content)
        gemini.at[index, 'GeminiGeneratedLoc'] = line_count
        gemini.at[index, 'GeminiGeneratedFunctionBody'] = largest_func_content

    gemini.to_csv(gemini_path, index=False)

    for index, row in gemini_improved_comments.iterrows():
        generated = row["GeminiGenerated"]
        largest_func_content, line_count = extract_function_of_interest_and_length.get_largest_function(generated)
       # print(largest_func_content)

        gemini_improved_comments.at[index, 'GeminiGeneratedLoc'] = line_count
        gemini_improved_comments.at[index, 'GeminiGeneratedFunctionBody'] = largest_func_content

    gemini_improved_comments.to_csv(gemini_improved_comments_path, index=False)

def calculate_chatGPT_loc():
    for index, row in gpt.iterrows():
        generated = row["ChatGPTGenerated"]
        largest_func_content, line_count = extract_function_of_interest_and_length.get_largest_function(generated)
       # print(largest_func_content)
        gpt.at[index, 'ChatGPTGeneratedLoc'] = line_count
        gpt.at[index, 'ChatGPTGeneratedFunctionBody'] = largest_func_content

    gpt.to_csv(gpt_path, index=False)

    for index, row in gpt_improved_comments.iterrows():
        generated = row["ChatGPTGenerated"]
        largest_func_content, line_count = extract_function_of_interest_and_length.get_largest_function(generated)
       # print(largest_func_content)

        gpt_improved_comments.at[index, 'ChatGPTGeneratedLoc'] = line_count
        gpt_improved_comments.at[index, 'ChatGPTGeneratedFunctionBody'] = largest_func_content

    gpt_improved_comments.to_csv(gpt_improved_comments_path, index=False)

gt = pd.read_csv('../data/sample_of_interest.csv')
calculate_gt_loc()

codellama_path = '../scripts/codellama/codellama.csv'
codellama_improved_comments_path = '../scripts/codellama/codellama_with_rag.csv'
codellama = pd.read_csv(codellama_path)
codellama_improved_comments = pd.read_csv(codellama_improved_comments_path)

calculate_codellama_loc()

deepseek_path = '../scripts/deepseek/deepseek.csv'
deepseek_improved_comments_path = '../scripts/deepseek/deepseek_with_rag.csv'
deepseek = pd.read_csv(deepseek_path)
deepseek_improved_comments = pd.read_csv(deepseek_improved_comments_path)

calculate_deepseek_loc()

gemini_path = '../scripts/Gemini/gemini.csv'
gemini_improved_comments_path = '../scripts/Gemini/gemini_with_rag.csv'
gemini = pd.read_csv(gemini_path)
gemini_improved_comments = pd.read_csv(gemini_improved_comments_path)

calculate_gemini_loc()

gpt_path = '../scripts/ChatGPT/chatGPT.csv'
gpt_improved_comments_path = '../scripts/ChatGPT/chatGPT_with_rag.csv'
gpt = pd.read_csv(gpt_path)
gpt_improved_comments = pd.read_csv(gpt_improved_comments_path)

calculate_chatGPT_loc()
