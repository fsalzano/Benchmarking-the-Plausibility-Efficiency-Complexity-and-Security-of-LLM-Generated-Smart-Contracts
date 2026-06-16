import pandas as pd
import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', "scripts"))
sys.path.insert(0, parent_dir)
parent_dir2 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', "scripts", "metrics"))

sys.path.append(parent_dir)
sys.path.append(parent_dir2)


def extract_first_value_if_dict(value):
    if isinstance(value, dict):
        return next(iter(value.values()))  # Get the first value
    return value


# add parents to sys.path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

if parent_dir2 not in sys.path:
    sys.path.insert(0, parent_dir2)

from scripts.metrics import extract_function_of_interest_and_length,  bleu_calculator

gt = pd.read_csv('../data/sample_of_interest.csv')
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

gt_functions = []

deepseek_functions = []
deepseek_improved_functions = []

codellama_functions = []
codellama_improved_functions = []

gemini_functions = []
gemini_improved_functions = []

gpt_functions = []
gpt_improved_functions = []

for index, row in gt.iterrows():
    largest_func_content, line_count = extract_function_of_interest_and_length.get_largest_function(row["Contract"])
    item = {index: largest_func_content}
    gt_functions.append(item)

for index, row in deepseek.iterrows():
    generated = row["DeepSeekGenerated"]
    deepseek_gen_function, line_count = extract_function_of_interest_and_length.get_largest_function(generated)
    item = {index: deepseek_gen_function}
    deepseek_functions.append(item)

for index, row in deepseek_improved_comments.iterrows():
    generated = row["DeepSeekGenerated"]
    deepseek_gen_function, line_count = extract_function_of_interest_and_length.get_largest_function(str(generated))
    item = {index: deepseek_gen_function}

    deepseek_improved_functions.append(item)

for index, row in codellama.iterrows():
    generated = row["CodeLLamaGenerated"]
    codellama_gen_function, line_count = extract_function_of_interest_and_length.get_largest_function(str(generated))
    item = {index: codellama_gen_function}
    codellama_functions.append(item)

for index, row in codellama_improved_comments.iterrows():
    generated = row["CodeLLamaGenerated"]
    codellama_gen_function, line_count = extract_function_of_interest_and_length.get_largest_function(str(generated))
    item = {index: codellama_gen_function}
    codellama_improved_functions.append(item)

for index, row in gemini.iterrows():
    generated = row["GeminiGenerated"]
    gemini_gen_function, line_count = extract_function_of_interest_and_length.get_largest_function(str(generated))
    item = {index: gemini_gen_function}
    gemini_functions.append(item)

for index, row in gemini_improved_comments.iterrows():
    generated = row["GeminiGenerated"]
    gemini_gen_function, line_count = extract_function_of_interest_and_length.get_largest_function(str(generated))
    item = {index: gemini_gen_function}
    gemini_improved_functions.append(item)

for index, row in gpt.iterrows():
    generated = row["ChatGPTGenerated"]
    gpt_gen_function, line_count = extract_function_of_interest_and_length.get_largest_function(str(generated))
    item = {index: gpt_gen_function}
    gpt_functions.append(item)

for index, row in gpt_improved_comments.iterrows():
    generated = row["ChatGPTGenerated"]
    gpt_gen_function, line_count = extract_function_of_interest_and_length.get_largest_function(str(generated))
    item = {index: gpt_gen_function}
    gpt_improved_functions.append(item)

for gt in gt_functions:
    for key, gt_value in gt.items():
        print('executing')
        deepseek_value = extract_first_value_if_dict(deepseek_functions[key])
        codellama_value = extract_first_value_if_dict(codellama_functions[key])
        deepseek_improved_value = extract_first_value_if_dict(deepseek_improved_functions[key])
        codellama_improved_value = extract_first_value_if_dict(codellama_improved_functions[key])
        gemini_value = extract_first_value_if_dict(gemini_functions[key])
        gemini_improved_value = extract_first_value_if_dict(gemini_improved_functions[key])
        gpt_value = extract_first_value_if_dict(gpt_functions[key])
        gpt_improved_value = extract_first_value_if_dict(gpt_improved_functions[key])

        # Calculate the semantic similarity and BLEU for DeepSeek
        #deepseek_semantic_similarity = semantic_similarity.get_similarity(gt_value, deepseek_value)
        deepseek_bleu = bleu_calculator.calculate_bleu(gt_value, str(deepseek_value))

        # Add the similarity and BLEU values to the corresponding row in the DataFrame
        #deepseek.loc[key, 'SemanticSimilarity'] = deepseek_semantic_similarity
        deepseek.loc[key, 'BLEU'] = deepseek_bleu

        # Calculate the semantic similarity and BLEU for DeepSeek Improved

        #deepseek_improved_semantic_similarity = semantic_similarity.get_similarity(gt_value, deepseek_improved_value)
        deepseek_improved_bleu = bleu_calculator.calculate_bleu(gt_value, str(deepseek_improved_value))

        #deepseek_improved_comments.loc[key, 'SemanticSimilarity'] = deepseek_improved_semantic_similarity
        deepseek_improved_comments.loc[key, 'BLEU'] = deepseek_improved_bleu

        # # Calculate the semantic similarity and BLEU for CodeLlama
        #codellama_semantic_similarity = semantic_similarity.get_similarity(gt_value, codellama_value)
        codellama_bleu = bleu_calculator.calculate_bleu(gt_value, str(codellama_value))

        #codellama.loc[key, 'SemanticSimilarity'] = codellama_semantic_similarity
        codellama.loc[key, 'BLEU'] = codellama_bleu

        # # Calculate the semantic similarity and BLEU for CodeLlama Improved
        #codellama_improved_semantic_similarity = semantic_similarity.get_similarity(gt_value, codellama_improved_value)
        codellama_improved_bleu = bleu_calculator.calculate_bleu(gt_value, str(codellama_improved_value))

        #codellama_improved_comments.loc[key, 'SemanticSimilarity'] = codellama_improved_semantic_similarity
        codellama_improved_comments.loc[key, 'BLEU'] = codellama_improved_bleu

        # Calculate the semantic similarity and BLEU for Gemini
        #gemini_semantic_similarity = semantic_similarity.get_similarity(gt_value, gemini_value)
        gemini_bleu = bleu_calculator.calculate_bleu(gt_value, str(gemini_value))
        #gemini.loc[key, 'SemanticSimilarity'] = gemini_semantic_similarity
        gemini.loc[key, 'BLEU'] = gemini_bleu

        # # Calculate the semantic similarity and BLEU for Gemini Improved
        #gemini_improved_semantic_similarity = semantic_similarity.get_similarity(gt_value, gemini_improved_value)
        gemini_improved_bleu = bleu_calculator.calculate_bleu(gt_value, str(gemini_improved_value))

        #gemini_improved_comments.loc[key, 'SemanticSimilarity'] = gemini_improved_semantic_similarity
        gemini_improved_comments.loc[key, 'BLEU'] = gemini_improved_bleu

        # # Calculate the semantic similarity and BLEU for GPT
       # gpt_semantic_similarity = semantic_similarity.get_similarity(gt_value, gpt_value)
        gpt_bleu = bleu_calculator.calculate_bleu(gt_value, str(gpt_value))

        #gpt.loc[key, 'SemanticSimilarity'] = gpt_semantic_similarity
        gpt.loc[key, 'BLEU'] = gpt_bleu

        # Calculate the semantic similarity and BLEU for GPT Improved
        #gpt_improved_semantic_similarity = semantic_similarity.get_similarity(gt_value, gpt_improved_value)
        gpt_improved_bleu = bleu_calculator.calculate_bleu(gt_value, str(gpt_improved_value))

        #gpt_improved_comments.loc[key, 'SemanticSimilarity'] = gpt_improved_semantic_similarity
        gpt_improved_comments.loc[key, 'BLEU'] = gpt_improved_bleu

deepseek.to_csv(deepseek_path, index=False)
deepseek_improved_comments.to_csv(deepseek_improved_comments_path, index=False)
codellama.to_csv(codellama_path, index=False)
codellama_improved_comments.to_csv(codellama_improved_comments_path, index=False)
gemini.to_csv(gemini_path, index=False)
gemini_improved_comments.to_csv(gemini_improved_comments_path, index=False)
gpt.to_csv(gpt_path, index=False)
gpt_improved_comments.to_csv(gpt_improved_comments_path, index=False)
