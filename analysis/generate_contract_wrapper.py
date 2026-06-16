import requests
import pandas as pd


# Function to call the API with a parameterized payload and URL
def call_api(url, model, function, temperature, stream=False):
    payload = {
        "model": model,
        "system": "You are a Solidity expert. Generate a Solidity wrapper function based on the input provided.",
        "prompt": (
            f"Generate a Solidity wrapper for the following function:\n{function}\n"
            f"Requirements:\n"
            f" Insert // SPDX-License-Identifier: GPL-3.0"
            f"- Use 'pragma solidity 0.8.0'.\n"
            f"- Import 'node_modules/@openzeppelin/contracts/access/Ownable.sol' and 'openzeppelin/SafeMath.sol'.\n"
            f"- Include necessary state variables.\n"
            f"- Output only the complete Solidity code. Do not add comments or text outside the code.\n"
            f"- Do not generate additional functions beyond the given snippet, even if external calls are present."
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
                print(response)
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


df = pd.read_csv("../data/sample_of_interest.csv")
for index, row in df.iterrows():
    func = row["FormattedCode"]

    result = call_api("http://localhost:11434/api/generate", "deepseek-coder-v2",
                      func, 0.4, False)
    df.at[index, "Contract"] = result

df.to_csv("sample_of_interest.csv")
