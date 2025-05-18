import json
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from src.configs.path import GROUND_TRUTH_PATH, EXTRACTED_PATH



def compute_bleu_score(reference, prediction):
    smoothie = SmoothingFunction().method4
    return sentence_bleu([reference.split()], prediction.split(), smoothing_function=smoothie)

def evaluate_all_fields():
    header_fields = [
        "invoice_no", "invoice_date", "seller", "client",
        "seller_tax_id", "client_tax_id", "iban"
    ]
    summary_fields = ["total_net_worth", "total_vat", "total_gross_worth"]

    with open(GROUND_TRUTH_PATH, 'r') as gt_file, open(EXTRACTED_PATH, 'r') as ocr_file:
        for gt_line, ocr_line in zip(gt_file, ocr_file):
            gt_data = json.loads(gt_line)
            ocr_data = json.loads(ocr_line)
            
            image_filename = gt_data["image"]
            print(f"Image: {image_filename}")

            # Check fields in header
            for field in header_fields:
                ref = gt_data.get("ground_truth", {}).get("gt_parse", {}).get("header", {}).get(field, "") or ""
                pred = ocr_data.get("extracted_parse", {}).get("header", {}).get(field, "") or ""
                bleu = compute_bleu_score(ref, pred)
                print(f"Header - {field}: BLEU = {bleu:.4f}")

            # Check fields in summary
            for field in summary_fields:
                ref = gt_data.get("ground_truth", {}).get("gt_parse", {}).get("summary", {}).get(field, "") or ""
                pred = ocr_data.get("extracted_parse", {}).get("summary", {}).get(field, "") or ""
                bleu = compute_bleu_score(ref, pred)
                print(f"Summary - {field}: BLEU = {bleu:.4f}")

            print("-" * 60)

# Run the evaluation
if __name__ == '__main__':
    evaluate_all_fields()