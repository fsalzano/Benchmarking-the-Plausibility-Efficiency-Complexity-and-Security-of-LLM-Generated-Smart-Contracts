import pandas as pd
import requests
from tqdm import tqdm


def call_api(url, model, contract_code, temperature, index, example, stream=False):
    payload = {
        "model": model,
        "system": (
            "You are a Solidity expert. Your goal is to rewrite constructors based on specific initialization constraints."
        ),
        "prompt": (
            "Let's think step by step. You are a Solidity expert. Your task is to analyze the provided Solidity contract and do the following: "
            "1. If the contract does not contain a constructor, add one."
            "2. If the contract already contains a constructor, rewrite it and remove abstract from abstract contract (abstract contract -> contract)."
            "3. In the constructor, initialize all instance (state) variables to fixed, safe, non-corner-case values."
            "4. If the contract inherits from any parent contracts such as Ownable, ERC20, or others, "
            "you must properly invoke their constructors using the correct syntax (e.g., Ownable(msg.sender), ERC20(\"TokenName\", \"TKN\"))"
            "Initialization rules:"
            "- uint/uint256: Set to 1 (never 0)"
            "- address: Use these fixed values in order: 0x111..., 0x222..., 0x333..."
            "- bool: Set to true"
            "- string: Set to 'initialized'"
            "- bytes32: Set to bytes32('init')"
            "- For ERC20 or similar constructors requiring arguments, use placeholder values like 'MyToken'"
            "- Avoid setting any value to its zero/default state"
            "- Do not change imports and the rest of the contract logic"
            "Return only the modified contract code without ```solidity or backtick."
            f"Contract:\n{contract_code}"
            f"Don't forget the initialization of Ownable -> constructor() Ownable(msg.sender)!"
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
                if '```solidity' in output:
                    start = output.find("```solidity") + 11
                    end = output.rfind("```")
                    output = output[start:end].strip()
                print(output)
                return output
            else:
                print("The 'response' field is missing in the response JSON.")
        except ValueError:
            print("Error parsing JSON response.")
    else:
        print(f"Error: {response.status_code}, {response.text}")


def call_api_for_constructor_injection(url, model, contract_code, temperature, index, example, stream=False):
    prompt = (
        f"You are a Solidity expert. Let's think step by step. Your task is to analyze the provided Solidity contract and do the following:\n\n"
        f"1. If the contract does not contain a constructor, add one.\n"
        f"2. If the contract already contains a constructor, rewrite it and remove abstract from abstract contract (abstract contract -> contract).\n"
        f"3. In the constructor, initialize all instance (state) variables to fixed, safe, non-corner-case values.\n"
        f"4. If the contract inherits from any parent contracts such as Ownable, Pausable, ERC20, or others, "
        f"you must properly invoke their constructors using the correct syntax (e.g., Ownable(msg.sender), ERC20(\"TokenName\", \"TKN\"))\n\n"
        f"Initialization rules:\n"
        f"- uint/uint256: Set to 1 to the first one, 2 to the second and so on (never 0)\n"
        f"- address: Use these fixed values in order: 0x111..., 0x222..., 0x333... (complete the address instead of puttin ...)\n"
        f"- bool: Set to true\n"
        f"- string: Set to 'initialized'\n"
        f"- bytes32: Set to bytes32('init')\n"
        f"- For ERC20 or similar constructors requiring arguments, use placeholder values like 'MyToken'.\n"
        f"- Avoid setting any value to its zero/default state\n"
        f"- Do not change imports and the rest of the contract logic\n"
        f"Return only the modified contract code without ```solidity or backtick.\n\n"
        f"Contract:\n{contract_code} \n If the contract is Ownable the constructor must include constructor() Ownable(msg.sender)."

    )

    payload = {
        "model": model,
        "system": "You are a Solidity expert. Your goal is to rewrite constructors based on specific initialization constraints. If the contract is Ownable the constructor must include constructor() Ownable(msg.sender).",
        "prompt": prompt,
        "stream": stream,  # Important: disables line-by-line response that may truncate
        "options": {
            "temperature": temperature
        }
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=600)
        if response.status_code == 200:
            json_response = response.json()
            print(json_response.get("response"))
            return json_response.get("response", "")
        else:
            print(f"[{index}] Error: {response.status_code}, {response.text}")
            return ""
    except Exception as e:
        print(f"[{index}] Exception: {e}")
        return ""


EXAMPLE = '''// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import "node_modules/@openzeppelin/contracts/access/Ownable.sol";
import "openzeppelin/SafeMath.sol";

contract PriceSetter is Ownable { 

constructor() Ownable(msg.sender) {
}
    using SafeMath for uint256;
    uint256 public currentPrice;

    function setCurrentPrice(uint256 newPrice) public onlyOwner {
        currentPrice = newPrice;
    }
}'''


def process_df(df, path, ref, model_name="qwen2.5-coder:14b"):
    for index, row in tqdm(df.iterrows(), total=len(df), desc=f"Processing {path}"):
        content= str(row["contract_with_constructor"])
        if len(content) > 20:
            print('hop')
            continue
        code = ''
        if "ground" in ref:
            code = row.get("Contract", "")
        elif "gpt" in ref:
            code = row.get("ChatGPTGenerated", "")
        elif "gemini" in ref:
            code = row.get("GeminiGenerated", "")
        elif "codellama" in ref:
            code = row.get("CodeLLamaGenerated", "")
        elif "deepseek" in ref:
            code = row.get("DeepSeekGenerated", "")

        if not pd.isna(code):
            result = call_api(
                "http://localhost:11434/api/generate",
                model_name,
                code,
                temperature=0,
                index=index,
                example=EXAMPLE
            )
            result = (str(result).replace("abstract constructor", "constructor")
                      .replace('import "@openzeppelin/contracts/access/Ownable.sol";',
                               'import "node_modules/@openzeppelin/contracts/access/Ownable.sol";')
                      .replace('import "@openzeppelin/contracts/utils/math/SafeMath.sol";',
                               'import "openzeppelin/SafeMath.sol";'))

            df.at[index, "contract_with_constructor"] = result



    # Final save
    df.to_csv(path, index=False)


# Load CSV and apply transformation
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

process_df(gt, gt_path, "ground")
process_df(gpt, gpt_path, "gpt")
process_df(gemini, gemini_path, "gemini")
process_df(codellama, codellama_path, "codellama")
process_df(deepseek, deepseek_path, "deepseek")
#
process_df(gpt_improved_comments, gpt_improved_comments_path, "gpt")
process_df(gemini_improved_comments, gemini_improved_comments_path, "gemini")

process_df(codellama_improved_comments, codellama_improved_comments_path, "codellama")
process_df(deepseek_improved_comments, deepseek_improved_comments_path, "deepseek")
