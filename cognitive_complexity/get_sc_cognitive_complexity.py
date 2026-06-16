from extract_functions import extract_function
import re


def get_complexity(function):
    """
    Calculates the cognitive complexity of the function, following the SonarQube white paper.
    Increases complexity for 'if', 'for', 'while', 'require', 'assert', 'continue', 'break', 'else if', 'catch',
    the ternary operator, and logical operator changes.
    """
    complexity = 0
    nesting = -1  # Current block nesting depth

    # Remove comments to avoid false positives in if, for, while, require, assert, continue, break, and catch
    function_no_comments = remove_comments(function)

    lines = function_no_comments.splitlines()

    for i, line in enumerate(lines):
        nesting = update_nesting(line, nesting)

        # Increase complexity based on the type of construct found
        complexity += handle_else_if(line, lines, i, nesting)
        complexity += handle_if(line, nesting)
        complexity += handle_ternary_operator(line, nesting)  # New: Handling ternary operators
        complexity += handle_for(line, nesting)
        complexity += handle_while(line, nesting)
        complexity += handle_require(line)
        complexity += handle_assert(line)
        complexity += handle_continue(line)
        complexity += handle_break(line)
        complexity += handle_catch(line)

    return complexity


def remove_comments(function):
    """
    Removes comments from the Solidity function code.
    """
    return re.sub(r'//.*?(\n|$)|/\*.*?\*/', '', function, flags=re.DOTALL)


def update_nesting(line, nesting):
    """
    Updates the nesting level based on the presence of curly braces.
    """
    if '{' in line:
        nesting += 1
    if '}' in line:
        nesting -= 1
    return nesting


def handle_else_if(line, lines, index, nesting):
    """
    Handles the 'else if' and 'else { if' complexity cases.
    """
    if 'else if' in line or ('else' in line and index + 1 < len(lines) and 'if' in lines[index + 1]):
        return 1 if nesting == 1 else 1 + (nesting - 1)
    return 0


def handle_if(line, nesting):
    """
    Handles the 'if' complexity and conditions.
    """
    if 'if' in line and 'else if' not in line:
        complexity = 1 if nesting == 1 else 1 + (nesting - 1)

        # Extract the condition within the parentheses
        condition_start = line.find('(') + 1
        condition_end = line.find(')')
        condition = line[condition_start:condition_end].strip()

        # Increase complexity for logical operators (&&, ||) and negations (!)
        complexity += calculate_condition_complexity(condition)

        return complexity
    return 0


def handle_ternary_operator(line, nesting):
    """
    Handles the ternary operator complexity. Increases by 1 as if it were an 'if', and considers nesting.
    """
    if '?' in line and ':' in line:
        return 1 if nesting == 0 else 1 + (nesting)
    return 0


def handle_for(line, nesting):
    """
    Handles the 'for' loop complexity.
    """
    if 'for' in line:
        return 1 if nesting == 1 else 1 + (nesting - 1)
    return 0


def handle_while(line, nesting):
    """
    Handles the 'while' loop complexity and conditions.
    """
    if 'while' in line:
        complexity = 1 if nesting == 1 else 1 + (nesting - 1)

        # Extract the condition within the parentheses
        condition_start = line.find('(') + 1
        condition_end = line.find(')')
        condition = line[condition_start:condition_end].strip()

        # Increase complexity for logical operators (&&, ||) and negations (!)
        complexity += calculate_condition_complexity(condition)

        return complexity
    return 0


def handle_require(line):
    """
    Handles the 'require' statement complexity and conditions.
    """
    if 'require' in line:
        complexity = 1

        # Extract the condition within the parentheses
        condition_start = line.find('(') + 1
        condition_end = line.rfind(')')  # To handle require with a message
        condition = line[condition_start:condition_end].strip()

        # Increase complexity for logical operators (&&, ||) and negations (!)
        complexity += calculate_condition_complexity(condition)

        return complexity
    return 0


def handle_assert(line):
    """
    Handles the 'assert' statement complexity. Increases by 1 for 'assert' and additional complexity for conditions.
    """
    if 'assert' in line:
        complexity = 1  # Base complexity for 'assert'

        # Extract the condition within the parentheses
        condition_start = line.find('(') + 1
        condition_end = line.find(')')
        condition = line[condition_start:condition_end].strip()

        # Increase complexity for logical operators (&&, ||) and negations (!)
        complexity += calculate_condition_complexity(condition)

        return complexity
    return 0


def handle_continue(line):
    """
    Handles the 'continue' statement complexity.
    """
    if 'continue' in line:
        return 1
    return 0


def handle_break(line):
    """
    Handles the 'break' statement complexity.
    """
    if 'break' in line:
        return 1
    return 0


def handle_catch(line):
    """
    Handles the 'catch' block complexity. Always increases by 1, regardless of nesting.
    """
    if 'catch' in line:
        return 1
    return 0


def calculate_condition_complexity(condition):
    """
    Calculates the complexity of logical conditions based on logical operators and negations.
    Increments the complexity for each '&&' and '||', and for negations '!', but skips '!='.
    """
    complexity = 0
    previous_operator = None
    i = 0

    while i < len(condition):
        # Handle logical operators '&&' and '||'
        if condition[i:i + 2] == '&&' or condition[i:i + 2] == '||':
            current_operator = condition[i:i + 2]

            # If it's the first operator, increment complexity
            if previous_operator is None:
                complexity += 1
            # If the operator is different from the previous one, increment complexity
            elif current_operator != previous_operator:
                complexity += 1

            previous_operator = current_operator
            i += 2
        # Handle negation '!' but skip '!='
        elif condition[i] == '!' and (i + 1 >= len(condition) or condition[i + 1] != '='):
            complexity += 1
            i += 1
        else:
            i += 1

    return complexity

def analyze(solidity_code):
    # Extract functions using the imported function
    try:
        extracted_functions = extract_function(solidity_code)

        # Add closing brace that might have been removed by the regex
        extracted_functions = [function + "\n}" if not function.strip().endswith('}') else function for function in
                               extracted_functions]

        # Evaluate only the first extracted function
        index = 1
        results = []

        for function in extracted_functions:
            complexity = get_complexity(function)
            index += 1
            function_name = function.split('function')[1].split('(')[0]

            result = {"function": function_name[1:], "complexity": complexity}
            results.append(result)

        return results
    except:
        result = {"function": "", "complexity": 0}
        return result
if __name__ == "__main__":
    # Solidity code example as a string
    solidity_code = """
    pragma solidity ^0.8.0;

contract MyContract {

    function setValue(uint256 value) public {
        // Do something
        uint256 x = value + 1;

       if (x>0) {
         for (uint i = 0; i < 10; i++) {
            while(x>0){
            x=0;
         }
         }
         } 

        if (!(x > 10 && x < 50 || x == 25)) {  // Multiple conditions with negation
            x = 10;
            if (x == 10) {  // Nested if
                x = 5;
            }
        } else if (x == 20) {  // Else if statement
            x = 15;
        } else {
            if (x == 30) {  // Treated as else if, ignoring nesting of else
                x = 35;
            }
        }

        x = (x > 0) ? 100 : 0;  // Ternary operator example

        for (uint i = 0; i < 10; i++) {
            if (i == 5) {
                break;  // Break statement
            }
            if (i % 2 == 0) {
                continue;  // Continue statement
            }
            x += i;
        }

        while (x < 50 && x != 42) {  // While loop with multiple conditions
            x += 1;
        }

        require(x < 100 && x > 10, "x is out of range");  // Require with multiple conditions

        assert(x != 0);  // Assert statement

        try this.internalFunction() returns (bool success) {
            x = 1;
        } catch {  // Catch block
            x = 0;
        }

        if (x == 5) {
            x = 0;
        }
    }

}

    """
    analyze(solidity_code)

