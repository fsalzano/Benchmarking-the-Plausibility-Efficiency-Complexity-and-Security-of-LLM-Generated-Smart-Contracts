
def extract_function(solidity_code):

    functions = []
    lines = solidity_code.splitlines()
    inside_function = False
    function_code = ""
    open_braces = 0

    for line in lines:
        line = line.strip()
        if line.startswith("function"):
            inside_function = True
            function_code = line
            open_braces = line.count("{") - line.count("}")
        elif inside_function:
            function_code += "\n" + line
            open_braces += line.count("{") - line.count("}")
            if open_braces == 0:
                functions.append(function_code)
                inside_function = False
                function_code = ""

    return functions

if __name__ == "__main__":
    # Esempio di codice Solidity come stringa
    solidity_code = """
    pragma solidity ^0.8.0;

    contract MyContract {

        function setValue(uint256 value) public {
            // Do something
            uint256 x = value + 1;
            if (x > 10) {
                x = 10;
            }
            for (uint i = 0; i < 10; i++) {
                x += i;
            }
            if (x == 5) {
                x = 0;
            }
            
            
        }

        function getValue() public view returns (uint256) {
            return 42;
        }

        function internalFunction() internal pure returns (bool) {
            return true;
        }

        function payableFunction() public payable {
            // Accept ether
        }
    }
    """

    extracted_functions = extract_function(solidity_code)

