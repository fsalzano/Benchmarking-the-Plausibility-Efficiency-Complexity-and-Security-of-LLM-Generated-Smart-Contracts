import glob
import os
import pandas as pd
from scipy.stats import fisher_exact

def interpret_odds_ratio(or_val):
    """Interpret Odds Ratio effect size."""
    if or_val == 1:
        return "no effect"
    elif or_val > 1:
        if or_val < 1.5:
            return "small positive association"
        elif or_val < 3.0:
            return "medium positive association"
        else:
            return "large positive association"
    else:  # or_val < 1
        if or_val > 0.67:
            return "small negative association"
        elif or_val > 0.33:
            return "medium negative association"
        else:
            return "large negative association"


def significance_marker(p):
    """Return significance markers."""
    if p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    else:
        return ""


# --------------------------------------------------
# Load CSV files
# --------------------------------------------------

script_dir = os.path.dirname(os.path.abspath(__file__))
csv_files = sorted(glob.glob(os.path.join(script_dir, "*.csv")))

# Store vulnerability distributions for statistical tests
datasets = {}

# --------------------------------------------------
# Parse vulnerability findings
# --------------------------------------------------

for path in csv_files:

    df = pd.read_csv(path, dtype=str)

    if "toolid" not in df.columns or "findings" not in df.columns:
        print(f"{os.path.basename(path)} -> missing columns")
        continue

    tool_lc = df["toolid"].astype(str).str.lower()
    findings_lc = df["findings"].astype(str).str.lower()

    # --------------------------
    # SLITHER DETECTORS
    # --------------------------

    slither_mask = tool_lc.str.contains("slither", na=False)

    reentrancy_mask = slither_mask & findings_lc.str.contains(
        "reentrancy", na=False
    )

    unchecked_mask = slither_mask & findings_lc.str.contains(
        "unchecked", na=False
    )

    lack_of_input_validation_mask = slither_mask & (
        findings_lc.str.contains("arbitrary_send_eth", na=False)
        | findings_lc.str.contains("arbitrary-send-erc20", na=False)
        | findings_lc.str.contains("arbitrary-send-erc20-permit", na=False)
        | findings_lc.str.contains("controlled-array-length", na=False)
        | findings_lc.str.contains("controlled-delegatecall", na=False)
    )

    # Slither randomness detectors
    slither_randomness_mask = slither_mask & (
        findings_lc.str.contains("weak_prng", na=False)
        | findings_lc.str.contains("gelato-unprotected-randomness", na=False)
    )

    # --------------------------
    # SMARTCHECK DOS DETECTORS
    # --------------------------

    smartcheck_mask = tool_lc.str.contains("smartcheck", na=False)

    dos_mask = smartcheck_mask & (
        findings_lc.str.contains("solidity_gas_limit_in_loops", na=False)
        | findings_lc.str.contains("solidity_transfer_in_loop", na=False)
        | findings_lc.str.contains("solidity_extra_gas_in_loops", na=False)
        | findings_lc.str.contains("solidity_var_in_loop_for", na=False)
    )

    # --------------------------
    # SOLHINT RANDOMNESS
    # --------------------------

    solhint_mask = tool_lc.str.contains("solhint", na=False)

    solhint_randomness_mask = solhint_mask & findings_lc.str.contains(
        "not-rely-on-block-hash", na=False
    )

    # --------------------------
    # UNIFIED BAD RANDOMNESS
    # --------------------------

    bad_randomness_mask = slither_randomness_mask | solhint_randomness_mask

    # --------------------------------------------------
    # Vulnerability counts
    # --------------------------------------------------

    reentrancy_count = int(reentrancy_mask.sum())
    unchecked_count = int(unchecked_mask.sum())
    lack_input_count = int(lack_of_input_validation_mask.sum())
    dos_count = int(dos_mask.sum())
    bad_randomness_count = int(bad_randomness_mask.sum())

    print(
        f"{os.path.basename(path)} -> "
        f"reentrancy: {reentrancy_count} | "
        f"unchecked: {unchecked_count} | "
        f"lack_of_input_validation: {lack_input_count} | "
        f"DOS: {dos_count} | "
        f"Bad Randomness: {bad_randomness_count}"
    )

    # --------------------------------------------------
    # Store binary distributions for statistical tests
    # --------------------------------------------------

    datasets[os.path.basename(path)] = pd.DataFrame(
        {
            "reentrancy": reentrancy_mask.astype(int),
            "unchecked": unchecked_mask.astype(int),
            "lack_input_validation": lack_of_input_validation_mask.astype(int),
            "dos": dos_mask.astype(int),
            "bad_randomness": bad_randomness_mask.astype(int),
        }
    )


# --------------------------------------------------
# STATISTICAL ANALYSIS
# --------------------------------------------------

if "sample.csv" not in datasets:

    print("\nGround truth (sample.csv) not found. Statistical test skipped.")

else:

    ground_truth = datasets["sample.csv"]

    print("\n===== STATISTICAL ANALYSIS (vs Ground Truth) =====")

    for name, data in datasets.items():

        if name == "sample.csv":
            continue

        print(f"\n{name}")

        for vuln in ground_truth.columns:

            # 1. Build the 2x2 contingency table
            # Row 1: Current Tool [Vulnerability Present, Vulnerability Absent]
            # Row 2: Ground Truth [Vulnerability Present, Vulnerability Absent]
            tool_pos = data[vuln].sum()
            tool_neg = len(data[vuln]) - tool_pos

            gt_pos = ground_truth[vuln].sum()
            gt_neg = len(ground_truth[vuln]) - gt_pos

            contingency_table = [[tool_pos, tool_neg], [gt_pos, gt_neg]]

            # 2. Run Fisher's Exact Test
            odds_ratio, p = fisher_exact(
                contingency_table, alternative="two-sided"
            )

            magnitude = interpret_odds_ratio(odds_ratio)
            marker = significance_marker(p)

            print(
                f"{vuln} -> "
                f"p={p:.5f}{marker} | "
                f"Odds Ratio={odds_ratio:.3f} ({magnitude})"
            )