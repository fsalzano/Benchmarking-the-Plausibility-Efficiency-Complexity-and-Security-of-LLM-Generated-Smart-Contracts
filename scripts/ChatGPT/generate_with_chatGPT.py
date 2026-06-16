import pandas as pd
import os
import requests
import time

from dotenv import load_dotenv
import os

load_dotenv("../../.env")
import sys

# Load API key
load_dotenv("../../.env")
openai_api_key = os.getenv('CHATGPT')

# Add RAG path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', "..",
                                          "rag"))
sys.path.append(parent_dir)

# add parents to sys.path
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from rag import rag

api_key = os.getenv('CHATGPT')

openai_api_key = api_key


def call_api_rag(code_summary):
    """Extended version with RAG context, adapted for better prompting behavior."""

    results = rag.find_similar_notice_matches(code_summary)

    retrieved_code_examples = "\n\n".join(results['function_code'].dropna().astype(str).tolist())
    retrieved_comments = "\n\n".join(results['notice_comment'].dropna().astype(str).tolist())

    # Compose dynamic prompt
    sections = [f"Here is the code summary:\n\n{code_summary}"]

    if retrieved_code_examples:
        sections.append(f"Retrieved code snippets:\n\n{retrieved_code_examples}")
    if retrieved_comments:
        sections.append(f"Developer comments:\n\n{retrieved_comments}")

    full_prompt = (
        "Generate a Solidity smart contract function based on the provided information.\n"
        "The function must strictly adhere to Solidity best practices and be complete, functional, and independent.\n"
        "Use input parameters whenever possible, but include state variables if necessary.\n"
        "Apply appropriate modifiers and roles where needed.\n"
        "Handle all security considerations properly using constructs like `require`.\n"
        "Do not include explanations, comments, or more than one function — return only the Solidity code.\n\n"
        + "\n\n".join(sections)
    )

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }

    data = {
        "model": "gpt-4o-2024-08-06",
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a Solidity expert tasked with generating a fully implemented, single Solidity "
                    "smart contract function. "
                    "The function must be complete, functional, and adhere to Solidity best practices, "
                    "following version ^0.8.0. "
                    "Do not use placeholders or incomplete logic. "
                    "Do not add any comments or explanations. "
                    "Use only input parameters where possible, but define state variables if absolutely needed. "
                    "Ensure proper use of access modifiers, visibility, and security checks like `require`."
                )
            },
            {
                "role": "user",
                "content": full_prompt
            }
        ]
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)

    try:
        content = response.json()['choices'][0]['message']['content']
        if '```' in content:
            start = content.find("```solidity") + 11
            end = content.rfind("```")
            content = content[start:end].strip()
        return content
    except KeyError:
        print(response.json())
        return ""

def call_api(code_summary):
    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }

    data = {
        "model": "gpt-4o-2024-08-06",
        "messages": [
            {
                "role": "system",
                "content": "You are a Solidity expert tasked with generating a fully implemented, single Solidity "
                           "smart contract function."
                           "The function must be complete, functional, and adhere to Solidity best practices, "
                           "following version ^0.8.0."
                           "Do not use placeholders or incomplete logic. Avoid adding comments in place of code ("
                           "e.g., avoid // Additional logic can be added here)."
                           "The function must use only input parameters whenever possible, but state variables are "
                           "allowed if necessary."
                           "Ensure correct use of access modifiers, visibility specifiers, and necessary security "
                           "checks (such as require statements)."
                           "Use SafeMath or built-in Solidity arithmetic safeguards if needed. Generate only the "
                           "function, without any additional explanation or comments."

            },
            {
                "role": "user",
                "content": "Generate a Solidity smart contract function based on the provided code summary."
                           "The function must strictly adhere to Solidity best practices and be complete, functional, "
                           "and independent."
                           " Ensure that it includes appropriate roles or modifiers where applicable."
                           "Use only input parameters instead of state variables when possible, but include state "
                           "variables if necessary."
                           " The function should be self-contained and correctly handle security considerations."
                           " Do not add any explanations or comments—return only the Solidity function."
                           "\n\nHere is the code summary:\n\n"
                           f"{code_summary}"

            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    try:
        generated_function = response.json()['choices'][0]['message']['content']
        if '```' in generated_function:
            start = generated_function.find("```solidity") + 11
            end = generated_function.rfind("```")
            generated_function = generated_function[start:end].strip()
        print(generated_function)

        return generated_function
    except KeyError as e:
        print(response.json())


df = pd.read_csv("chatGPT.csv")

for index, row in df.iterrows():
    summary = row["Comment"]
    start_time = time.time()

    result = call_api(summary)
    end_time = time.time() - start_time

    df.at[index, "ChatGPTGenerated"] = result
    df.at[index, "Time"] = end_time

    df.to_csv("chatGPT.csv", index=False)


df1 = pd.read_csv("chatGPT_with_rag.csv")

# Then: iterate over the rows using RAG version
for index, row in df1.iterrows():
    print(index)

    if row["SemanticSimilarity"] > 0.5:
        continue
    summary = row["Comment"]
    start_time = time.time()

    result = call_api_rag(summary)
    end_time = time.time() - start_time

    df1.at[index, "ChatGPTGenerated"] = result
    df1.at[index, "Time"] = end_time
    df1.to_csv("chatGPT_with_rag.csv", index=False)

