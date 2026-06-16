import pandas as pd
from tqdm import tqdm


def process_df(df, path):
    for index, row in tqdm(df.iterrows(), total=len(df), desc=f"Processing {path}"):
        code = str(row.get("contract_with_constructor", ""))

        code = remove_abstract_and_wrong_imports(code)
        if "FractionJoiner" in code:
            print(code)
        df.at[index, "contract_with_constructor"] = code

    # Final save
    df.to_csv(path, index=False)


def remove_abstract_and_wrong_imports(content):
    content = str(content).replace("abstract contract", "contract")

    if "uint256 public totalSupply;" not in content and "totalSupply" in content:
        content = content.replace(
            'constructor',
            'uint256 public totalSupply;\n\n constructor'
        )

    if "mapping(address => uint256) public balanceOf" not in content and "balanceOf" in content:
        content = content.replace(
            'constructor',
            'mapping(address => uint256) public balanceOf;\n\n constructor'
        )

    content = content.replace(
        'import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/access/Ownable.sol";',
        'import "node_modules/@openzeppelin/contracts/access/Ownable.sol";'
    )
    content = content.replace(
        'import "node_modules/@openzeppelin/contracts/utils/SafeMath.sol";',
        'import "openzeppelin/SafeMath.sol";'
    )

    content = content.replace(
        'import "Ownable.sol";',
        'import "node_modules/@openzeppelin/contracts/access/Ownable.sol";'
    )
    # 4569
    content = content.replace(
        'import "openzeppelin-solidity/contracts/access/Ownable.sol;',
        'import "node_modules/@openzeppelin/contracts/access/Ownable.sol";'
    )

    content = content.replace(
        'import "https://github.com/OpenZeppelin/openzeppelin-solidity/contracts/access/Ownable.sol";',
        'import "node_modules/@openzeppelin/contracts/access/Ownable.sol";'
    )

    content = content.replace(
        'totalSupply = 1;',
        'totalSupply = 1000000000000000000;'
    )

    content = content.replace(
        'balanceOf[msg.sender] = 1;',
        'balanceOf[msg.sender] = 1000;'
    )

    content = content.replace(
        '0x222...',
        '0x2222222222222222222222222222222222222222'
    )

    content = content.replace(
        '0x111...',
        '0x1111111111111111111111111111111111111111'
    )

    content = content.replace(
        '0x333...',
        '0x3333333333333333333333333333333333333333'
    )

    content = content.replace(
        'balances[msg.sender] = 1;',
        'balances[msg.sender] = 1000;'
    )

    content = content.replace(
        'balances[address(0x222...)] = 1;',
        'balances[address(0x2222222222222222222222222222222222222222)] = 1000;'
    )

    content = content.replace(
        'balances[address(0x111...)] = 1;',
        'balances[address(0x1111111111111111111111111111111111111111)] = 1000;'
    )

    content = content.replace(
        'balances[address(0x333...)] = 1;',
        'balances[address(0x3333333333333333333333333333333333333333)] = 1000;'
    )

    content = content.replace(
        'balanceOf[address(0x222...)] = 1;',
        'balanceOf[address(0x2222222222222222222222222222222222222222)] = 1000;'
    )

    content = content.replace(
        'balanceOf[address(0x111...)] = 1;',
        'balanceOf[address(0x1111111111111111111111111111111111111111)] = 1000;'
    )

    content = content.replace(
        'balanceOf[address(0x333...)] = 1;',
        'balanceOf[address(0x3333333333333333333333333333333333333333)] = 1000;'
    )

    content = content.replace(
        'constructor() Ownable(msg.sender) {}',
        '''constructor() Ownable(msg.sender) {
        // Initialize state variables with safe, non-corner-case values
        balanceOf[msg.sender] = 1000; // Set to 1 (never 0)
        totalSupply = 1000000000000000000; // Set to 1 (never 0)
    }'''
    )
    content = content.replace(
        "import '@openzeppelin/contracts/access/Ownable.sol';",
        'import "node_modules/@openzeppelin/contracts/access/Ownable.sol";'
    )
    content = content.replace(
        'import "node_modules/@openzeppelin/contracts/security/Ownable.sol";',
        'import "node_modules/@openzeppelin/contracts/access/Ownable.sol";'
    )

    content = content.replace(
        'import "openzeppelin-solidity/contracts/access/Ownable.sol";',
        'import "node_modules/@openzeppelin/contracts/access/Ownable.sol";'
    )

    content = content.replace(
        'import "https://github.com/OpenZeppelin/openzeppelin-solidity/contracts/access/Ownable.sol";',
        'import "node_modules/@openzeppelin/contracts/access/Ownable.sol";'
    )

    content = content.replace(
        '"@openzeppelin',
        '"node_modules/@openzeppelin'
    )
    content = content.replace(
        'import "./SafeMath.sol";',
        'import "openzeppelin/SafeMath.sol";'
    )
    content = content.replace(
        'import "openzeppelin-solidity/contracts/math/SafeMath.sol";',
        'import "openzeppelin/SafeMath.sol";'
    )

    content = content.replace(
        ', SafeMath {',
        ' {;'
    )

    content = content.replace(
        'import "SafeMath.sol";',
        'import "openzeppelin/SafeMath.sol";'
    )
    content = content.replace(
        'import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/math/SafeMath.sol";',
        'import "openzeppelin/SafeMath.sol";'
    )
    content = content.replace(
        'import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/SafeMath.sol";',
        'import "openzeppelin/SafeMath.sol";'
    )
    content = content.replace(
        "import '@openzeppelin/contracts/utils/math/SafeMath.sol';",
        'import "openzeppelin/SafeMath.sol";'
    )

    if "SafeMath.sol" not in str(content):
        content = content.replace(
            '\ncontract ',
            'import "openzeppelin/SafeMath.sol";\ncontract ')

    return content


# Load CSV and apply transformation
codellama_path = '../scripts/codellama/codellama.csv'
codellama_improved_comments_path = '../scripts/codellama/codellama_with_rag.csv'
codellama = pd.read_csv(codellama_path)
codellama_improved_comments = pd.read_csv(codellama_improved_comments_path)

deepseek_path = '../scripts/deepseek/deepseek.csv'
deepseek_improved_comments_path = '../scripts/deepseek/deepseek_with_rag.csv'
deepseek = pd.read_csv(deepseek_path)
deepseek_improved_comments = pd.read_csv(deepseek_improved_comments_path)

gemini_path = '../scripts/Gemini/gemini.csv'
gemini_improved_comments_path = '../scripts/Gemini/gemini_with_rag.csv'
gemini = pd.read_csv(gemini_path)
gemini_improved_comments = pd.read_csv(gemini_improved_comments_path)

gpt_path = '../scripts/ChatGPT/chatGPT.csv'
gpt_improved_comments_path = '../scripts/ChatGPT/chatGPT_with_rag.csv'
gpt = pd.read_csv(gpt_path)
gpt_improved_comments = pd.read_csv(gpt_improved_comments_path)

gt_path = '../data/sample_of_interest.csv'
gt = pd.read_csv(gt_path)

process_df(gt, gt_path)
process_df(gpt, gpt_path)
process_df(gemini, gemini_path)
process_df(codellama, codellama_path)
process_df(deepseek, deepseek_path)
#
process_df(gpt_improved_comments, gpt_improved_comments_path)
process_df(gemini_improved_comments, gemini_improved_comments_path)

process_df(codellama_improved_comments, codellama_improved_comments_path)
process_df(deepseek_improved_comments, deepseek_improved_comments_path)
