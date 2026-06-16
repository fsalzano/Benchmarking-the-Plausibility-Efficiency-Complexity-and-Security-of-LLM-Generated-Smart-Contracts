# Import necessary libraries
import solidity_parser.parser as sp
import json
import pandas as pd

# Function to extract the AST of the Solidity function with the largest number of statements
def get_function_with_largest_body(solidity_code):
    """
    Extracts the AST of the Solidity function with the largest body,
    excluding constructors.

    Parameters:
    - solidity_code (str): The Solidity source code.

    Returns:
    - str: The JSON-formatted string of the AST node of the function
           with the largest body (excluding constructors).
    """
    try:
        # Parse the Solidity code to get the AST
        ast = sp.parse(solidity_code)
    except:
        # Return empty dict if parsing fails
        return {}

    # Initialize variables to keep track of the largest function
    largest_function = None
    max_statements = 0

    # Traverse the AST to find ContractDefinitions and their FunctionDefinitions
    for node in ast.get('children', []):
        if node and node.get('type') == 'ContractDefinition':
            for subnode in node.get('subNodes', []):
                if subnode.get('type') == 'FunctionDefinition':
                    # Skip constructors
                    if subnode.get('isConstructor', False):
                        continue

                    # Count the number of statements in the function body
                    try:
                        body_statements = len(subnode.get('body', {}).get('statements', []))
                    except:
                        body_statements = 0

                    # Update the largest function if current one has more statements
                    if body_statements > max_statements:
                        max_statements = body_statements
                        largest_function = subnode

    # If no valid function found, return empty dict
    if not largest_function:
        return {}

    # Convert to string, clean it up, and return
    largest_function = str(largest_function).replace(
        "'decl': <solidity_parser.solidity_antlr4.SolidityParser.SolidityParser.VariableDeclarationContextobjectat0x71d1809159e0>",
        ''
    )
    return largest_function.replace('\'', "\"")


# Ensures Solidity code is wrapped in a contract structure if missing
def wrap(code):
    if "pragma solidity " not in code:
        return "pragma solidity ^0.8.0; \n \ncontract MyContract {\n" + code + "\n }"
    return code

# Load the ground truth and model-generated Solidity datasets
gt = pd.read_csv("../../data/sample_of_interest.csv")
codellama = pd.read_csv("../codellama/codellama.csv")
deepseek = pd.read_csv("../deepseek/deepseek.csv")
gemini = pd.read_csv("../Gemini/gemini.csv")
chatGPT = pd.read_csv("../ChatGPT/chatGPT.csv")

# Load versions of the model outputs with improved comments
codellama_with_improved_comments = pd.read_csv("../codellama/codellama_with_rag.csv")
deepseek_with_improved_comments = pd.read_csv("../deepseek/deepseek_with_rag.csv")
gemini_with_improved_comments = pd.read_csv("../Gemini/gemini_with_rag.csv")
chatGPT_with_improved_comments = pd.read_csv("../ChatGPT/chatGPT_with_rag.csv")

# Process the ground truth data: extract the AST of the largest function and store it
for index, row in gt.iterrows():
    ast = get_function_with_largest_body(str(row['Contract']))
    gt.at[index, 'ast'] = ast
gt.to_csv("../../data/sample_of_interest.csv", index=False)

# Process CodeLlama outputs
for index, row in codellama.iterrows():
    ast = get_function_with_largest_body(wrap(str(row['CodeLLamaGenerated'])))
    codellama.at[index, 'ast'] = ast
codellama.to_csv("../codellama/codellama.csv", index=False)

# Process DeepSeek outputs
for index, row in deepseek.iterrows():
    ast = get_function_with_largest_body(row['DeepSeekGenerated'])
    deepseek.at[index, 'ast'] = ast
deepseek.to_csv("../deepseek/deepseek.csv", index=False)

# Process Gemini outputs
for index, row in gemini.iterrows():
    ast = get_function_with_largest_body(row['GeminiGenerated'])
    gemini.at[index, 'ast'] = ast
gemini.to_csv("../Gemini/gemini.csv", index=False)

# Process ChatGPT outputs
for index, row in chatGPT.iterrows():
    ast = get_function_with_largest_body(row['ChatGPTGenerated'])
    chatGPT.at[index, 'ast'] = ast
chatGPT.to_csv("../ChatGPT/chatGPT.csv", index=False)

# Process CodeLlama outputs with improved comments
for index, row in codellama_with_improved_comments.iterrows():
    ast = get_function_with_largest_body(row['CodeLLamaGenerated'])
    codellama_with_improved_comments.at[index, 'ast'] = ast
codellama_with_improved_comments.to_csv("../codellama/codellama_with_rag.csv", index=False)

# Process DeepSeek outputs with improved comments
for index, row in deepseek_with_improved_comments.iterrows():
    ast = get_function_with_largest_body(row['DeepSeekGenerated'])
    deepseek_with_improved_comments.at[index, 'ast'] = ast
deepseek_with_improved_comments.to_csv("../deepseek/deepseek_with_rag.csv", index=False)

# Process Gemini outputs with improved comments
for index, row in gemini_with_improved_comments.iterrows():
    ast = get_function_with_largest_body(row['GeminiGenerated'])
    gemini_with_improved_comments.at[index, 'ast'] = ast
gemini_with_improved_comments.to_csv("../Gemini/gemini_with_rag.csv", index=False)

# Process ChatGPT outputs with improved comments
for index, row in chatGPT_with_improved_comments.iterrows():
    ast = get_function_with_largest_body(row['ChatGPTGenerated'])
    chatGPT_with_improved_comments.at[index, 'ast'] = ast
chatGPT_with_improved_comments.to_csv("../ChatGPT/chatGPT_with_rag.csv", index=False)
