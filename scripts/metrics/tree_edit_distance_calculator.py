import zss


class ASTNode:
    def __init__(self, label, children=None):
        """
        Generic node to represent the AST in a tree structure.
        :param label: Label of the node (e.g., 'FunctionDefinition', 'Identifier', etc.).
        :param children: List of child nodes.
        """
        self.label = label
        self.children = children or []

    def get_children(self):
        return self.children

    def __repr__(self):
        return f"ASTNode({self.label})"


def json_to_ast_node(json_obj):
    """
    Converts a JSON object into an ASTNode recursively.
    :param json_obj: JSON object representing the AST.
    :return: Root node of the AST (type ASTNode).
    """
    # Get the type of the node as its label
    label = json_obj.get('type', 'Unknown')

    # Convert children recursively
    children = []
    for key, value in json_obj.items():
        if isinstance(value, dict):
            # Single value, convert it into a node
            children.append(json_to_ast_node(value))
        elif isinstance(value, list):
            # List of nodes, convert them all
            for child in value:
                if isinstance(child, dict):
                    children.append(json_to_ast_node(child))

    return ASTNode(label, children)


def calculate_ted(json1, json2):
    """
    Calculates the Tree Edit Distance between two ASTs represented as JSON.
    :param json1: First JSON object representing the AST.
    :param json2: Second JSON object representing the AST.
    :return: Tree Edit Distance.
    """
    # Convert JSONs into AST trees
    tree1 = json_to_ast_node(json1)
    tree2 = json_to_ast_node(json2)

    # Cost function to compare nodes
    def node_distance(node1, node2):
        return 0 if node1.label == node2.label else 1

    # Calculate TED using zss
    ted = zss.simple_distance(
        tree1,
        tree2,
        get_children=lambda n: n.get_children(),
    )

    return ted


