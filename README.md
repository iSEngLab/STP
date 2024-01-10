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
python3.11 -m venv venv-stp

source venv-stp/bin/activate
python -m pip install --upgrade pip
pip install --force-reinstall -r requirements.txt
```

2. Add dev tools

```sh
pre-commit install
```

# To install google-cloud-cli

```sh
sudo tee -a /etc/yum.repos.d/google-cloud-sdk.repo << EOM
[google-cloud-cli]
name=Google Cloud CLI
baseurl=https://packages.cloud.google.com/yum/repos/cloud-sdk-el9-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=0
gpgkey=https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
EOM
```

```sh
sudo dnf install google-cloud-cli
```

# Obtain API KEY

## for google

A Google Cloud account is required.
Link for re: https://cloud.google.com/translate/docs/reference/rest

```sh
gcloud init
```

```sh
gcloud auth application-default print-access-token
```

## for Microsoft

An Azure account is required. Need to add a `free` service for cognitive services: Translator. Then go to KEYS and take the key from there. (2M chars of any combination of standard translation and custom training free per month)
Link for re: https://learn.microsoft.com/en-us/azure/ai-services/translator/

## for DeepL

An DeepL account is required. Add free plan (500k characters / month)
Link for re: https://www.deepl.com/docs-api

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
