GROUND_TRUTH_PATH = (
    r"D:\Evaluate-pipeline\src\downloaded_dataset\ground_truth_14052025.jsonl"
)
EXTRACTED_PATH = (r"D:\Evaluate-pipeline\src\downloaded_dataset\extracted_data.jsonl")

PROMPT = """
You are an AI assistant tasked with extracting structured information from invoice text.
Given the following content, extract the required fields and format them according to the provided schema.

if the key doesn't have any values add "N/A"

Content:
{content}

Schema:
{schema}

Please ensure the output strictly adheres to the schema format.
"""