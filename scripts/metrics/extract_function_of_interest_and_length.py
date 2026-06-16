def get_largest_function(code):
    """
    Extracts all functions from the Solidity code, excluding functions
    in interfaces (functions without a body), and returns the content
    of the function with the greatest number of lines.

    Args:
        code (str): The Solidity source code as a string.

    Returns:
        tuple: A tuple containing the content of the largest function (str)
               and the number of lines in its content (int). Returns (None, 0)
               if no functions are found.
    """
    functions = []
    function_start = code.find("function")  # Start searching for "function"

    while function_start != -1:
        brace_count = 0
        func_body = []
        in_function = False
        i = function_start

        # Check if the function is part of an interface (no opening brace `{`)
        # This is done by checking if `{` appears before `;`
        open_brace_pos = code.find("{", function_start)
        semicolon_pos = code.find(";", function_start)
        if semicolon_pos != -1 and (open_brace_pos == -1 or semicolon_pos < open_brace_pos):
            # Skip this function and continue searching
            function_start = code.find("function", semicolon_pos)
            continue

        # Iterate from the function keyword forward
        while i < len(code):
            char = code[i]
            func_body.append(char)

            if char == '{':
                brace_count += 1
                in_function = True
            elif char == '}':
                brace_count -= 1

            # If we've closed all braces, the function ends
            if in_function and brace_count == 0:
                break
            i += 1

        # Add the function to the list
        func_body_str = ''.join(func_body).strip()
        num_lines = func_body_str.count('\n') + 1
        functions.append((func_body_str, num_lines))

        # Find the next "function" keyword
        function_start = code.find("function", i)

    # Find the function with the greatest number of lines
    if functions:
        largest_function = max(functions, key=lambda x: x[1])
        return largest_function  # Returns the full content and line count of the largest function

    return None, 0


