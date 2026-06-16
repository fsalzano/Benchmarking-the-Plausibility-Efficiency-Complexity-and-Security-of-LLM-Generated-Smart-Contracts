from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction


def calculate_bleu(reference, candidate):
    """
    Calculates the BLEU score between a reference and a candidate.

    Parameters:
    - reference (str): The reference string (ground truth).
    - candidate (str): The candidate string (generated code).

    Returns:
    - float: The BLEU score.
    """

    def tokenize_function(func):
        return func.replace("(", " ( ").replace(")", " ) ").replace(",", " , ") \
            .replace(":", " : ").replace("{", " { ").replace("}", " } ") \
            .split()

    # Tokenize both reference and candidate
    reference_tokens = [tokenize_function(reference)]  # Reference should be a list of token lists
    candidate_tokens = tokenize_function(candidate)  # Candidate should be a single token list

    # Calculate BLEU score
    smoothing_function = SmoothingFunction().method1
    bleu_score = sentence_bleu(reference_tokens, candidate_tokens, smoothing_function=smoothing_function)

    return bleu_score
