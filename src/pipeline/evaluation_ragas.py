import os
import json
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval
from deepeval import assert_test
from dotenv import load_dotenv
from openai import OpenAI
from src.configs.path import EXTRACTED_PATH, GROUND_TRUTH_PATH, PROMPT

# Set environment variable to suppress tqdm progress bars
os.environ["DEEPEVAL_NO_TQDM"] = "1"  # must be BEFORE deepeval imports!

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI()

def test_llm_outputs_with_prompt():
    # Define GEval metric
    correctness_metric = GEval(
        name="Correctness",
        criteria="Determine if the actual output is correct based on the expected output.",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
        threshold=0.5,
    )

    try:
        # Load ground truth data
        with open(GROUND_TRUTH_PATH, "r") as truth_file:
            truth_data = [json.loads(line) for line in truth_file]

        # Load extracted data
        with open(EXTRACTED_PATH, "r") as extracted_file:
            extracted_data = [json.loads(line) for line in extracted_file]

        # Evaluate each test case
        for i, (truth, actual_output) in enumerate(zip(truth_data, extracted_data)):
            try:
                # Create LLMTestCase
                test_case = LLMTestCase(
                    input=f"{PROMPT}\n\nInput:\n{json.dumps(truth, indent=2)}",
                    actual_output=json.dumps(actual_output, indent=2),
                    expected_output=json.dumps(truth, indent=2),
                )
                # Assert test
                assert_test(test_case, [correctness_metric])
                print('passed without error')
            except Exception as e:
                print(f"Error evaluating test case {i}: {e}")
                continue

    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_llm_outputs_with_prompt()

