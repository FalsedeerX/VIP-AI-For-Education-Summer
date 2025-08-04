# Running Evaluations

## Command

```
python -m instructorchat.evaluation.evaluate [test-file]
```

## Description

Evaluates the current RAG system by asking test questions and scoring the retrieval and responses.

test-file is a JSON file containing an array of objects with "input" and "expected_output"

> **_NOTE_**: You must provide an OpenAI API key for the judge LLM through the OPENAI_API_KEY environmental variable.

Example:
```json
[
    {
        "input": "What color is the sky?",
        "expected_output": "The sky is blue."
    },
    {
        "input": "What is the capital of France?",
        "expected_output": "Paris"
    }
]
```

Test responses are stored in a `responses_[TIMESTAMP].json` file that is updated every 10 responses. The full judging results are stored in `evaluation_results.csv`.

## Flags

--api-key [string]: The API key to use for the LLM being evaluated. Falls back on environmental variable if not set. Note that you must still provide an OpenAI API key for the judge LLM.

--temperature [float]: (default 0.7) The temperature of the LLM being evaluated.

--judge-only: Run judge on already obtained responses. If using this option, test-file should be a responses file instead.

--cache: Whether to use cached responses when judging. Useful if the program crashed during judging.

--throttle [int]: (default 3) Throttle amount for the judging of responses. Decrease this to speed up judging, increase if you're running into rate limit errors.

--concurrent [int]: (default 5) How many test cases to run concurrently during judging. Increase this to speed up judging, decrease if you're running into rate limit errors.

## Metrics

### Final Response

- Answer Relevancy: Measures how relevant the LLM's output was to the question asked. https://deepeval.com/docs/metrics-answer-relevancy for more details.
- Correctness: Measures how well the information provided by the LLM matches up with the expected response.

### Retrieval Only

- Contextual Precision: Measures how good the ranking of contexts in the retrieval context is, i.e., more relevant contexts are ranked higher than more irrelevant ones. https://deepeval.com/docs/metrics-contextual-precision for more details.
- Contextual Recall: Measures how well the retrieval context lines up with the expected output. https://deepeval.com/docs/metrics-contextual-recall for more details.
- Contextual Relevancy: Measures how relevant the retrieval context is to the question asked. https://deepeval.com/docs/metrics-contextual-relevancy for more details.


# Generating Test Cases

## Command

```
python -m instructorchat.evaluation.generate
```

## Description

Generates evaluation test cases from a set of PDFs using vision. For generation through text data only, the code is in `instructorchat/evaluation/generate.py`, but not set up to work through CLI.

You must provide an OpenAI API key through environmental variable only if batch is disabled.

## Flags

--batch: Creates a file for use with the OpenAI batch API. Recommended when generating large test set. Look at `instructorchat/evaluation/upload_generation_tasks.ipynb` for an example of how to upload the file and process the results.

--input-dir [string]: (default "documents") Where to get the documents to generate test cases from, relative to current working directory. Note that the code does not search for documents recursively, so PDFs should not be in subdirectories, unless they are not meant to be part of the generation.

--output-dir [string]: (default "eval_data") Where to place the generated file, relative to the current working directory.
