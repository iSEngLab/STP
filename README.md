Machine Translation Testing via Syntactic Tree Pruning

## File Structure

./:STP Source Code

./data/original_sentences: original sentences in the form of txt and excel

./data/evaluated_results: suspected translate errors by each tool after human evaluation

./related-documentation: relationship map used when pruning

./test: test root

## Python Version

- python 3.12

1. Set environment

```sh
rm -rf venv-stp
python3.12 -m venv venv-stp

source venv-stp/bin/activate
python -m pip install --upgrade pip
pip install --force-reinstall -r requirements.txt
```

2. Add dev tools

```sh
pre-commit install
```

## Install Requested Python Packages

- pip install -r requirements.txt

## Install models

- Stanford Corenlp

## Testing step

- Download Stanford Corenlp service(Windows/Linux/MacOS)
  - https://stanfordnlp.github.io/CoreNLP/index.html
- Detect translation errors:

  - Set dataset, api_key in main.py
  - run main.py

- Data process
  - After detecting translation errors
  - run all_output.py
- RQ Codes：
  - edit main function,and run result/all_output
  - set overlap in **main** function: overlap()
  - ErrorType in **main** function: STPType()
  - IssueCount in **main** function:Pairs()
  - ErrorCount in **main** function:Error()

```

```
