import json
from dotenv import load_dotenv
from openai import OpenAI
from src.configs.path import GROUND_TRUTH_PATH, EXTRACTED_PATH

# Load the .env file
load_dotenv()
client = OpenAI()


def load_jsonl(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def build_validation_prompt(extracted, ground_truth, seen_invoices):
    invoice_no = extracted.get("header", {}).get("invoice_no", "")
    is_duplicate = invoice_no in seen_invoices
    if invoice_no:
        seen_invoices.add(invoice_no)

    prompt = f"""
You are a validation assistant. Compare the extracted invoice data with the ground truth.
Check the following strictly:
⚬ Missing fields (in header, items, or summary)
⚬ Errors in totals or date
⚬ Duplicate invoice numbers

Respond with one of:
- Validated
- Needs Correction\n⚬ [list each issue on a separate line]

Only respond in that format. No extra explanation.

Extracted:
{json.dumps(extracted, indent=2)}

Ground Truth:
{json.dumps(ground_truth, indent=2)}

Duplicate Invoice: {"Yes" if is_duplicate else "No"}
"""
    return prompt


def validate_all_invoices(extracted_path, ground_truth_path):
    seen_invoices = set()
    results = []

    extracted_data = load_jsonl(extracted_path)
    ground_truth_data = load_jsonl(ground_truth_path)
    gt_lookup = {d["image"]: d["ground_truth"]["gt_parse"] for d in ground_truth_data}

    for entry in extracted_data:
        filename = entry.get("image")
        extracted = entry.get("extracted_parse", {})

        if filename not in gt_lookup:
            print(f"⚠️ Skipping: Ground truth missing for {filename}")
            continue

        ground_truth = gt_lookup[filename]
        prompt = build_validation_prompt(extracted, ground_truth, seen_invoices)

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a strict invoice validation assistant.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
            )
            result = response.choices[0].message.content.strip()
            print(f"\n🧾 {filename}:\n{result}")
            results.append({"file": filename, "result": result})
        except Exception as e:
            print(f"❌ Error validating {filename}: {e}")
            results.append({"file": filename, "result": "Error"})

    output_file = "invoice_validation_results.jsonl"
    with open(output_file, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    print(f"\n✅ Validation complete. Results saved to {output_file}")


if __name__ == "__main__":
    validate_all_invoices(EXTRACTED_PATH, GROUND_TRUTH_PATH)
