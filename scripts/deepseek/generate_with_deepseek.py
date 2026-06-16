import requests
import pandas as pd
import time
import os
import sys

response_format = '''your response must contains only the formatted function!
'''

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', "..",
                                          "rag"))
sys.path.append(parent_dir)

# add parents to sys.path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from rag import rag


def call_api(url, model, code_summary, temperature, is_rag=False, stream=False,
             retrieved_code_examples=None, retrieved_comments=None, original_notice=None):
    if is_rag:
        payload = {
            "model": model,
            "system": (
                "You are a Solidity expert tasked with generating a single Solidity smart contract function. "
                "The function must be complete, functional, and independent. "
                "Use only input parameters where possible, but you may define state variables if strictly necessary. "
                "Avoid placeholder comments (e.g., do not write '// Additional logic here'). "
                "Do not include explanations or multiple functions. Only output the Solidity code of a single function, wrapped in a contract if needed."
            ),
            "prompt": (
                "Generate a Solidity smart contract function based on the following summary, example code snippets, and associated comments.\n\n"
                "=== Code Summary ===\n"
                f"{code_summary}\n\n"
                "=== Example Code (from retrieved context) ===\n"
                f"{retrieved_code_examples or ''}\n\n"
                "=== Developer Comments ===\n"
                f"{retrieved_comments or ''}\n\n"
                "=== Original Notice ===\n"
                f"{original_notice or ''}\n\n"
                "Follow Solidity best practices, use modifiers and roles as needed, and comply with version ^0.8.0."
            ),
            "stream": stream,
            "options": {
                "temperature": temperature
            }
        }
    else:
        payload = {
            "model": model,
            "system": (
                "You are a Solidity expert tasked with generating a single Solidity smart contract function. "
                "Prefer input parameters, not state variables. Do not add comments in place of logic (e.g., avoid '// Additional logic can be added here')."
            ),
            "prompt": (
                "Generate a Solidity smart contract function based on the provided code summary. The function must: "
                "adhere to Solidity best practices, include all roles or modifiers, and comply with version ^0.8.0. "
                "Prefer input parameters over state variables. Use libraries like SafeMath if necessary, but ensure the function "
                "is complete, functional, and independent. You can add state variables. Do not provide any explanations or comments. "
                "Generate only one function.\n\n"
                f"Here is the code summary:\n\n{code_summary}"
            ),
            "stream": stream,
            "options": {
                "temperature": temperature
            }
        }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        try:
            response_data = response.json()
            if "response" in response_data:
                output = response_data["response"]
                if '```' in output:
                    start = output.find("```solidity") + 11
                    end = output.rfind("```")
                    output = output[start:end].strip()
                return output
            else:
                print("The 'response' field is missing in the response JSON.")
        except ValueError:
            print("Error parsing JSON response.")
    else:
        print(f"Error: {response.status_code}, {response.text}")


df = pd.read_csv("../../data/sample_of_interest.csv")
for index, row in df.iterrows():
    summary = row["Comment"]
    start_time = time.time()

    result = call_api("http://localhost:11434/api/generate", "deepseek-coder-v2",
                      summary, 0.4, False)
    end_time = time.time() - start_time

    df.at[index, "DeepSeekGenerated"] = result
    df.at[index, "Time"] = end_time
df.to_csv("deepseek.csv", index=False)

df2 = pd.read_csv("../../data/data_with_improved_comments.csv")

for index, row in df2.iterrows():
    print(index)
    summary = row["ImprovedComment"]
    start_time = time.time()

    # Step 1: Use the summary as query for RAG
    results = rag.find_similar_notice_matches(summary)

    # Step 2: Extract RAG context
    retrieved_code_examples = "\n\n".join(results['function_code'].dropna().astype(str).tolist())
    retrieved_comments = "\n\n".join(results['notice_comment'].dropna().astype(str).tolist())
    original_notice = summary

    # Step 3: Call the API with RAG context
    result = call_api(
        url="http://localhost:11434/api/generate",
        model="deepseek-coder-v2",
        code_summary=summary,
        temperature=0.4,
        stream=False,
        is_rag=True,
        retrieved_code_examples=retrieved_code_examples,
        retrieved_comments=retrieved_comments,
        original_notice=original_notice
    )

    # Step 4: Save results
    end_time = time.time() - start_time
    df2.at[index, "DeepSeekGenerated"] = result
    df2.at[index, "Time"] = end_time

df2.to_csv("deepseek_with_rag.csv", index=False)
