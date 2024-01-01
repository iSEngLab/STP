Machine Translation Testing via Syntactic Tree Pruning
## File Structure

./:STP Source Code

./data/original_sentences: original sentences in the form of txt and excel

./data/evaluated_results: suspected translate errors by each tool after human evaluation

./related-documentation: relationship map used when pruning

./test: test root

## Python Version

- python 3.6

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
  - set overlap in __main__ function: overlap()
  - ErrorType in __main__ function: STPType()
  - IssueCount in __main__ function:Pairs()
  - ErrorCount in __main__ function:Error()

