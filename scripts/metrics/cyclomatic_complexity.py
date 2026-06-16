def calculate_cyclomatic_complexity(function_code):
    """
    Calculates the cyclomatic complexity of a given function (e.g., Solidity or similar code).

    Args:
        function_code (str): The function code as a string.

    Returns:
        int: The cyclomatic complexity of the function.
    """
    # List of keywords that increase cyclomatic complexity
    control_keywords = [
        'if', 'else if', 'for', 'while', 'do', 'case', 'require', 'assert',
        '&&', '||', 'catch', 'try'
    ]

    complexity = 1  # Base complexity is always 1 (one single path)
    try:
    # Split the code into lines and analyze each line
        for line in function_code.splitlines():
            line = line.strip()  # Remove leading and trailing spaces
            if line.startswith('//') or line == '':  # Ignore comments and empty lines
                continue

            # Increment complexity for each relevant keyword in the line
            for keyword in control_keywords:
                # Count the number of occurrences of each keyword
                complexity += line.count(keyword)

        return complexity
    except Exception:
        return 0


