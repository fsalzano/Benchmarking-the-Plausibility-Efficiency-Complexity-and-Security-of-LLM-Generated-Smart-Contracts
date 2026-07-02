# Benchmarking-the-Plausibility-Efficiency-Complexity-and-Security-of-LLM-Generated-Smart-Contracts

This repository contains the code and data for a comprehensive evaluation of Large Language Models (LLMs) for Solidity code generation.

## ⚙️ Setup

Follow these steps to set up your development environment.

1. Create a virtual environment:

   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:

   Windows:

   ```bash
   venv\Scripts\activate
   ```

   macOS/Linux:

   ```bash
   source venv/bin/activate
   ```

3. Install dependencies:

   Make sure your virtual environment is active, then run:

   ```bash
   pip install -r requirements.txt
   ```

# A Comprehensive Evaluation of LLMs for Generating Solidity

This repository contains the code and data for a comprehensive evaluation of Large Language Models (LLMs) for Solidity code generation.


## 📁 Folder Structure

The project structure is organized as follows:

* analysis/

* cognitive_complexity/

* data/

* gas_and_functionality/

* preprocess/

* rag/

* scripts/

* security_assestment/


### analysis/

This folder contains code to get similarity metrics (such as BLEU and TED) and complexity to answer Research Questions (RQ) 1 and 4.

### cognitive_complexity/

This folder contains the code to calculate cognitive complexity.

### data/

This folder contains the ground truth data, and a CSV file `sample_of_interest.csv` with metrics related to the ground truth function, for instance, complexities.

### gas_and_functionality/

This folder contains data, code, and results related to gas consumption and functional correctness assessment. It also includes the `gt_contracts` subfolder, which contains contracts from the ground truth that can be compiled. To insert data into the model folders, i.e, chatGPT_contracts, use the `write_contracts.py` script.

### preprocess

This folder contains scripts used in the pre-processing phase and to extract a random sample.

### rag

This folder contains the code used to perform retrieval-augmented generation.

### scripts

* ChatGPT: This folder contains code to generate samples with ChatGPT and data related to the generated code with and without rag.
* Gemini: This folder contains code to generate samples with Gemini and data related to the generated code with and without rag.
* codellama: This folder contains code to generate samples with codellama and data related to the generated code with and without rag.
* constructor_injection: This folder contains code to inject constructors with qwen-coder-v2
* deepseek: This folder contains code to generate samples with deepseek-coder-v2 and data related to the generated code with and without rag.
* metrics: This folder contains code to obtain base metrics, for instance, semantic similarity, bleu, TED. Use the included requirements.txt to obtain dependencies for SmarEmbed.

### security_assestment

This folder contains code and data used to assess the security of the analyzed smart contracts.
