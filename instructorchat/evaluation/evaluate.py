from typing import List, Dict, Optional
from datetime import datetime
import json
import argparse
import os
import trio

from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric, GEval, ContextualPrecisionMetric, ContextualRecallMetric, ContextualRelevancyMetric
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from instructorchat.serve.inference import ChatIO, chat_loop
from instructorchat.serve.cli import SimpleChatIO

import pandas as pd

async def get_responses(
    model_path: str,
    temperature: float,
    chatio: ChatIO, #chatio is a chosen I/O handlings, while ChatIO (abstract) defines how every type of I/O handlings should look like.
    api_key: Optional[str] = None,
    input_file: str = "tests.json",
    save_responses_freq: Optional[int] = 10,
    responses_file_prefix: str = "responses"
) -> str:
    if not input_file.endswith(".json"):
        raise ValueError("'input_file' must be a JSON file.")

    with open(input_file, "r") as f:
        test_cases: List[Dict[str, str]] = json.load(f)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    responses_file = f"{responses_file_prefix}_{timestamp}.json"

    responses = []

    async for response in chat_loop(model_path, temperature, chatio, api_key, test_cases):
        responses.append(response)

        if (save_responses_freq is not None) and ((response["idx"] + 1) % save_responses_freq == 0):
            with open(responses_file, "w") as f:
                json.dump(responses, f, indent=4)

    with open(responses_file, "w") as f:
        json.dump(responses, f, indent=4)

    return responses_file

def run_evaluations(
    responses_file: str
):
    with open(responses_file, 'r') as f:
        test_cases = json.load(f)

    test_cases = [
        LLMTestCase(
            input=tc["input"],
            actual_output=tc["actual_output"],
            expected_output=tc["expected_output"],
            context=tc["context"] if "context" in tc else None,
            retrieval_context=tc["retrieval_context"]
        ) for tc in test_cases
    ]

    metrics = [
        AnswerRelevancyMetric(threshold=0.7, model="gpt-4.1-mini"),
        GEval(
            name="Correctness",
            evaluation_steps=[
                "If 'actual output' sufficiently answer the 'query' then it's a good output. 'Actual output' doesn't need to strictly repeat the information from 'expected output'"
                "Only use 'expected output' to check if the facts in 'actual output' contradicts any facts in 'expected output'",
                "If there is information in 'expected output' that isn't mentioned in the 'actual output', check it's relevant to the query to evaluate that information",
                "do not penalize the omission of insignificant words and relevant information",
                "actual output's having different writing style and grammar from the expected output's is OK"
            ],
            #criteria="Determine if the 'actual output' is factually correct based on the 'expected output'. Do not penalize for different format, structure, wording or unnecessary information as long as the fact provided is correct"
            model="gpt-4.1-mini",
            evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
            threshold=0.7
        ),
        ContextualPrecisionMetric(threshold=0.7, model="gpt-4.1-mini"),
        ContextualRecallMetric(threshold=0.7, model="gpt-4.1-mini"),
        ContextualRelevancyMetric(threshold=0.7, model="gpt-4.1-mini"),
    ]

    # Run evaluations
    test_result = evaluate(test_cases, metrics=metrics).test_results

    data = []
    for result in test_result:
        if result.metrics_data is None:
            print("Metric data is 'None' which is not expected.")
            continue

        for metric_data in result.metrics_data:
            data.append({
                "test_case": result.input,
                "actual_output": result.actual_output,
                "expected_output": result.expected_output,
                "retrieval_context": result.retrieval_context,
                "metric_name": metric_data.name,
                "score": metric_data.score,
                "reason": metric_data.reason,
            })

    df = pd.DataFrame(data)

    # Calculate and print average score per metric
    average_scores = df.groupby("metric_name")["score"].mean()
    print("\nAverage Scores per Metric:")
    print(average_scores)

    output_csv_file = "evaluation_results.csv"
    df.to_csv(output_csv_file, index=False)
    print(f"Results saved to {output_csv_file}")
    print("\nEvaluation Complete!")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str) # Specify test cases or responses file
    parser.add_argument("--api-key", type=str, help="OpenAI API key")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--judge-only", type=str, default=argparse.SUPPRESS) # Evaluate existing responses file
    args = parser.parse_args()

    # Use API key from environment variable if not provided
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key must be provided either through --api-key or OPENAI_API_KEY environment variable")

    chatio = SimpleChatIO()

    if "judge_only" not in args:
        responses_file = trio.run(get_responses, "gpt-4o-mini", args.temperature, chatio, api_key, args.input_file)
    else:
        responses_file = args.input_file

    run_evaluations(responses_file)

if __name__ == "__main__":
    main()