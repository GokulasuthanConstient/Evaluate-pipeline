import os
import json
from src.utils.load_data import load_extracted_jsonl, load_jsonl
from src.components.Evaluation_LLM import evaluate_invoice_llm

GROUND_TRUTH_PATH = "D:\Evaluate-pipeline\src\downloaded_dataset\ground_truth_14052025.jsonl"
EXTRACTED_PATH = "D:\\Evaluate-pipeline\\src\\downloaded_dataset\\extracted_data.jsonl"

def llm_main():
    # Load data
    gt_data = load_jsonl(GROUND_TRUTH_PATH)
    ext_data = load_extracted_jsonl(EXTRACTED_PATH)

    results = []

    # Process all images
    for image_id in sorted(gt_data):
        gt = gt_data.get(image_id, {})
        extracted = ext_data.get(image_id, {})

        if not extracted:
            continue

        # evaluate_invoice_llm returns: (image_id, result_dict)
        image_id, result_dict = evaluate_invoice_llm(gt, extracted, image_id)
        results.append((image_id, result_dict))

    # Print all results
    for image_id, result_dict in results:
        print(f"\nImage: {image_id}")
        print(f"Status: {result_dict.get('status', 'N/A')}")
        print(f"Flags: {result_dict.get('flags', [])}")
        print(f"Notes: {result_dict.get('notes', '')}")

if __name__ == "__main__":
    llm_main()




