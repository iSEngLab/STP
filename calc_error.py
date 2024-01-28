"""
There are two main proposed methodologies for calculate the error:
1. Assume that the best model has the golden standard (DeepL).
Based on the golden standard, decide what is the number of errors for every other model.
2. Compare all the translations for all the models.
If all the translations are the same, then the translation is correct, otherwise it is wrong.
"""

import pickle

import torch
import torch.nn.functional as F

from transformers import AutoTokenizer, AutoModel


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[
        0
    ]  # First element of model_output contains all token embeddings
    input_mask_expanded = (
        attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    )
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
        input_mask_expanded.sum(1), min=1e-9
    )


models: list[str] = [
    "google",
    "bing",
    "Helsinki-NLP/opus-mt-en-ro",
    "Helsinki-NLP/opus-tatoeba-en-ro",
    "Helsinki-NLP/opus-mt-tc-big-en-ro",
    "facebook/mbart-large-en-ro",
    "BlackKakapo/opus-mt-en-ro",
]


def calc_error_method_1(
    dataset_name: str,
    file_path: str,
    threshold: float = 0.92,
) -> list[dict]:
    # load deepL model
    with open(f"./{file_path}/target_sentences_deepl_{dataset_name}.pkl", "rb") as f:
        deepl_sentences = pickle.load(f)

    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

    results = []

    for model_ in models:
        differences = []  # list of tuples (sentence, translation, score)
        correct = 0

        model_checkpoint_name = model_.replace("/", "_").replace("-", "_")
        with open(
            f"./{file_path}/target_sentences_{model_checkpoint_name}_{dataset_name}.pkl",
            "rb",
        ) as f:
            model_sentences = pickle.load(f)

        for sentence in deepl_sentences.keys():
            sentences = [deepl_sentences[sentence], model_sentences[sentence]]
            encoded_input = tokenizer(
                sentences,
                padding=True,
                truncation=True,
                return_tensors="pt",
            )

            with torch.no_grad():
                model_output = model(**encoded_input)

            sentence_embeddings = mean_pooling(
                model_output, encoded_input["attention_mask"]
            )
            sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)

            cosine_scores = F.cosine_similarity(
                sentence_embeddings[0].unsqueeze(0),
                sentence_embeddings[1].unsqueeze(0),
            ).item()

            if cosine_scores < threshold:
                differences.append(
                    (
                        deepl_sentences[sentence],
                        model_sentences[sentence],
                        cosine_scores,
                    )
                )
            else:
                correct += 1

            # This method is inefficient, almost all the sentences are different => low scores
            # if deepl_sentences[sentence] == model_sentences[sentence]:
            #     correct += 1
            # else:
            #     differences.append(
            #         (
            #             deepl_sentences[sentence],
            #             model_sentences[sentence],
            #         )
            #     )

        results.append(
            {
                "model": model_,
                "correct": correct,
                "wrong": len(differences),
                "differences": differences,
            }
        )

    return results


models_2: list[str] = [
    "deepl",
    "google",
    "bing",
    # "Helsinki-NLP/opus-mt-en-ro",
    # "Helsinki-NLP/opus-tatoeba-en-ro",
    # "Helsinki-NLP/opus-mt-tc-big-en-ro",
    # "facebook/mbart-large-en-ro",
    # "BlackKakapo/opus-mt-en-ro",
]


def calc_error_method_2(
    dataset_name: str,
    file_path: str,
    threshold: float = 0.92,
) -> tuple[list[dict], int]:
    models_dict = {}
    for model_ in models_2:
        model_checkpoint_name = model_.replace("/", "_").replace("-", "_")
        with open(
            f"./{file_path}/target_sentences_{model_checkpoint_name}_{dataset_name}.pkl",
            "rb",
        ) as f:
            model_sentences = pickle.load(f)
        models_dict[model_] = model_sentences

    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

    results = []
    correct = 0

    source_lang_sentences = models_dict["deepl"].keys()
    for sentence in source_lang_sentences:
        sentences = [models_dict[model_][sentence] for model_ in models_2]

        encoded_input = tokenizer(
            sentences,
            padding=True,
            truncation=True,
            return_tensors="pt",
        )
        with torch.no_grad():
            model_output = model(**encoded_input)

        sentence_embeddings = mean_pooling(
            model_output, encoded_input["attention_mask"]
        )
        sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)

        # calculate similiarity between all the sentences
        cosine_scores = []
        for i in range(len(models_2)):
            for j in range(i + 1, len(models_2)):
                cosine_scores.append(
                    F.cosine_similarity(
                        sentence_embeddings[i].unsqueeze(0),
                        sentence_embeddings[j].unsqueeze(0),
                    ).item()
                )
        # all scores has to be above the threshold
        all_greater = all([score > threshold for score in cosine_scores])

        if all_greater:
            correct += 1
        else:
            res = {model_: models_dict[model_][sentence] for model_ in models_2}
            res["original"] = sentence
            res["score"] = cosine_scores
            results.append(res)

    return results, correct


def calc_correct(
    dataset_name: str,
    file_path: str,
    threshold: float = 0.92,
) -> dict[str, bool]:
    models_dict = {}
    for model_ in models_2:
        model_checkpoint_name = model_.replace("/", "_").replace("-", "_")
        with open(
            f"./{file_path}/target_sentences_{model_checkpoint_name}_{dataset_name}.pkl",
            "rb",
        ) as f:
            model_sentences = pickle.load(f)
        models_dict[model_] = model_sentences

    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

    sentence_map = {}

    source_lang_sentences = models_dict["deepl"].keys()
    for sentence in source_lang_sentences:
        sentences = [models_dict[model_][sentence] for model_ in models_2]

        encoded_input = tokenizer(
            sentences,
            padding=True,
            truncation=True,
            return_tensors="pt",
        )
        with torch.no_grad():
            model_output = model(**encoded_input)

        sentence_embeddings = mean_pooling(
            model_output, encoded_input["attention_mask"]
        )
        sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)

        # calculate similiarity between all the sentences
        cosine_scores = []
        for i in range(len(models_2)):
            for j in range(i + 1, len(models_2)):
                cosine_scores.append(
                    F.cosine_similarity(
                        sentence_embeddings[i].unsqueeze(0),
                        sentence_embeddings[j].unsqueeze(0),
                    ).item()
                )
        # all scores has to be above the threshold
        all_greater = all([score > threshold for score in cosine_scores])

        if all_greater:
            sentence_map[sentence] = True
        else:
            sentence_map[sentence] = False

    return sentence_map
