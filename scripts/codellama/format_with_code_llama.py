import requests
import pandas as pd

response_format = '''your response must contains only the formatted function!
'''


# Function to call the API with a parameterized payload and URL
def call_api(url, model, prompt, temperature, index, stream=False):
    payload = {
        "model": model,
        "prompt": prompt + response_format,
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
                print(response)
                if '```' in response:
                    start = response.find("```") + 3
                    end = response.rfind("```")
                    response = response[start:end].strip()
                return response

            else:
                print("The 'response' property is not present in the response.")
        except ValueError:
            print("Error parsing the response JSON.")
    else:
        print(f"Error: {response.status_code}, {response.text}")


example_function = """
function announceFork(string name, string url, uint256 blockNumber) public only(ROLE_PLATFORM_OPERATOR_REPRESENTATIVE) {
    require(blockNumber == 0 || blockNumber > block.number);
    _nextForkName = name;
    _nextForkUrl = url;
    _nextForkBlockNumber = blockNumber;
    LogForkAnnounced(_nextForkName, _nextForkUrl, _nextForkBlockNumber);
}
"""

df = pd.read_csv('../../data/sample_of_interest.csv')
for index, row in df.iterrows():
    function = row['Function']
    id = row["ID"]
    prompt = (
        "Your task is to format a Solidity function. Ensure proper indentation, consistent use of spaces, "
        "and alignment for better readability. DO NOT modify the functionality or logic of the function in any way. "
        "DO NOT add, remove, or change any code, such as adding `require` statements, `memory`, or any other elements. "
        "Simply adjust the formatting for clarity. "
        "Here is the function you must format:\n\n"
        f"{function}\n\n"
        "To assist you, I have provided an example of correctly formatted output:\n\n"
        f"{example_function}\n\n"
        "Use the example to understand the formatting style only. Remember, your output must match the functionality of the input function exactly, "
        "with no additional or removed code. Return only the formatted function as the output."
    )

    result = call_api("http://localhost:11434/api/generate", "codellama", prompt, 0.4, index, False)
    df.at[index, 'FormattedCode'] = result
    df.to_csv('../sample_of_interest.csv', index=False)
