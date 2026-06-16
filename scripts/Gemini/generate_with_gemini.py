import os
import time
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai
import sys

# Load API key
load_dotenv("../../.env")
api_key = os.getenv('GEMINI')
genai.configure(api_key=api_key)

import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',"..",
                                          "rag"))
sys.path.append(parent_dir)

# add parents to sys.path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


from rag import rag

# Gemini model setup
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="You are a Solidity expert. Your task is to generate a Solidity smart contract function "
                       "based on the provided summary and context. Do not add comments in place of logic "
                       "(e.g., avoid '// Additional logic can be added here')."
)


def generate_with_gemini(code_summary, retrieved_code_examples=None, retrieved_comments=None, original_notice=None):
    """Generate a Solidity smart contract function using Gemini with optional RAG context."""

    prompt = f"""Generate a Solidity smart contract function using the summary and context below.

=== Code Summary ===
{code_summary}

=== Example Code (from retrieved context) ===
{retrieved_code_examples or ''}

=== Developer Comments ===
{retrieved_comments or ''}

=== Original Notice ===
{original_notice or ''}

Constraints:
- Solidity Version: ^0.8.0
- Best Practices: Follow Solidity best practices
- Roles/Modifiers: Include as needed
- Input Parameters: Prefer them over state variables, but use state variables if needed
- Libraries: Use SafeMath or similar if applicable (and import them)
- Output: A single complete and functional Solidity function (no explanations or comments)
"""

    try:
        response = model.generate_content(prompt, generation_config=genai.GenerationConfig(temperature=0.1))
        return response.text
    except Exception as e:
        print(f"Error generating Solidity code: {e}")
        return f"An error occurred: {str(e)}"


def clean_output(result):
    if '```' in result:
        start = result.find("```solidity") + 11
        end = result.rfind("```")
        return result[start:end].strip()
    return result.strip()



df = pd.read_csv("../../data/sample_of_interest.csv")

for index, row in df.iterrows():
    summary = row["Comment"]
    start_time = time.time()

    # RAG retrieval
    results = rag.find_similar_notice_matches(summary)
    retrieved_code_examples = "\n\n".join(results['function_code'].dropna().astype(str).tolist())
    retrieved_comments = "\n\n".join(results['notice_comment'].dropna().astype(str).tolist())
    original_notice = summary

    # Generation
    result = generate_with_gemini(summary, retrieved_code_examples, retrieved_comments, original_notice)
    result = clean_output(result)

    end_time = time.time() - start_time
    time.sleep(4)

    df.at[index, "GeminiGenerated"] = result
    df.at[index, "Time"] = end_time

df.to_csv("gemini.csv", index=False)


df2 = pd.read_csv("gemini_with_rag.csv")

for index, row in df2.iterrows():
    print(index)
    summary = row["ImprovedComment"]
    start_time = time.time()

    # RAG retrieval
    print('start rag')
    results = rag.find_similar_notice_matches(summary)
    retrieved_code_examples = "\n\n".join(results['function_code'].dropna().astype(str).tolist())
    retrieved_comments = "\n\n".join(results['notice_comment'].dropna().astype(str).tolist())
    print('end rag')

    original_notice = summary

    # Generation
    print("start generating code")
    result = generate_with_gemini(summary, retrieved_code_examples, retrieved_comments, original_notice)
    result = clean_output(result)
    print("end generating code"
          "")

    end_time = time.time() - start_time
    time.sleep(4)

    df2.at[index, "GeminiGenerated"] = result
    df2.at[index, "Time"] = end_time
    df2.to_csv("gemini_with_rag.csv", index=False)

