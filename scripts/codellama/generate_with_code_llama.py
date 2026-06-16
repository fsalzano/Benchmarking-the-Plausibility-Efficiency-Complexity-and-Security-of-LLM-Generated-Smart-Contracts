import requests
import pandas as pd
import time
import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',"..",
                                          "rag"))
sys.path.append(parent_dir)

# add parents to sys.path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from rag import rag

response_format = '''your response must contains only the formatted function!
'''

def call_api(url, model, code_summary, temperature, is_rag, stream=False, retrieved_code_examples=None,
                            retrieved_comments=None,
                            original_notice=None):
    payload={}
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
                f"{retrieved_code_examples}\n\n"
                "=== Developer Comments ===\n"
                f"{retrieved_comments}\n\n"
                "=== Original Notice ===\n"
                f"{original_notice}\n\n"
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
            "system": "You are a Solidity expert tasked with generating a single Solidity smart contract function. Use only input parameters, not state variables. Do not add comments in place of logic (e.g., avoid // Additional logic can be added here).",
            "prompt": (
                "Generate a Solidity smart contract function based on the provided code summary. The function must:"
                " adhere to Solidity best practices, include all roles or modifiers, and comply with version ^0.8.0."
                " Prefer input parameters over state variables. Wrap in a contract and use libraries like SafeMath if necessary, but ensure the function"
                " is complete, functional, and independent. YOu can add state variable. Do not provide any explanations or comments. Generate only one function."
                " Here is the code summary:\n\n"
                f"{code_summary}"
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
                response = response_data["response"]
                print(index)
                if '```' in response:
                    start = response.find("```solidity") + 11
                    end = response.rfind("```")
                    response = response[start:end].strip()
                return response
            else:
                print("The 'response' property is not present in the response.")
        except ValueError:
            print("Error parsing the response JSON.")
    else:
        print(f"Error: {response.status_code}, {response.text}")


df=pd.read_csv("../../data/sample_of_interest.csv")

df1=pd.read_csv("codellama_with_rag.csv")

for index, row in df.iterrows():
    summary=row["Comment"]
    start_time=time.time()

    result=call_api("http://localhost:11434/api/generate", "codellama:13b",
             summary, 0.4, False, False)
    end_time = time.time() - start_time

    df.at[index, "CodeLLamaGenerated"]=result
    df.at[index, "Time"]=end_time
df.to_csv("codellama.csv", index=False)

for index, row in df1.iterrows():

    notice = row["Comment"]
    start_time = time.time()

    # Step 1: Use the notice as a query for the RAG retrieval
    results = rag.find_similar_notice_matches(notice)

    # Step 2: Extract relevant data from RAG results
    retrieved_code_examples = "\n\n".join(results['function_code'].dropna().astype(str).tolist())
    retrieved_comments = "\n\n".join(results['notice_comment'].dropna().astype(str).tolist())
    original_notice = notice

    # Step 3: Call the API to generate code using retrieved context
    result = call_api(
        url="http://localhost:11434/api/generate",
        model="codellama:13b",
        code_summary=notice,
        temperature=0,
        stream=False,
        is_rag=True,
        retrieved_code_examples=retrieved_code_examples,
        retrieved_comments=retrieved_comments,
        original_notice=original_notice
    )
    # Step 4: Save generated code and execution time into the DataFrame
    end_time = time.time() - start_time

    df1.at[index, "CodeLLamaGenerated"] = result
    df1.at[index, "Time"] = end_time
df1.to_csv("codellama_with_rag.csv", index=False)
