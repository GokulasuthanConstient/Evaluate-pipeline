import json
import os
import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableMap
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Use OpenAI's GPT-4o-mini model via LangChain
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Keep track of seen invoice numbers
seen_invoice_numbers = set()

# Prompt template
prompt = ChatPromptTemplate.from_template("""
You are a financial validation AI designed to check extracted invoice data against the ground truth.

Evaluate the extracted fields using these rules:

- Is any field missing in the extracted data?
- Are totals and dates (invoice_date, net, VAT, gross) calculated correctly?
- Does the invoice number appear to be a duplicate? (Already seen invoice numbers: {seen_invoices})

Return this format (JSON):

{{
  "status": "Validated" or "Needs Correction",
  "flags": [
    "Missing fields",
    "Errors in totals or date",
    "Duplicate invoice numbers"
  ],
  "notes": "Explain any mismatches briefly"
}}

### Ground Truth:
{ground_truth}

### Extracted:
{extracted}
""")

# Chain setup
chain = prompt | llm

def evaluate_invoice_llm(gt, extracted, image_id):
    invoice_no = extracted.get("header", {}).get("invoice_no", "")
    seen_str = ", ".join(seen_invoice_numbers) or "None"

    response = chain.invoke({
        "ground_truth": json.dumps(gt, indent=2),
        "extracted": json.dumps(extracted, indent=2),
        "seen_invoices": seen_str
    })

    # Track duplicates
    if invoice_no:
        seen_invoice_numbers.add(invoice_no)

    # Clean and parse the response
    raw_text = response.content.strip()

    # Remove markdown-style code blocks (like ```json ... ```)
    cleaned = re.sub(r"```(?:json)?\s*(.*?)\s*```", r"\1", raw_text, flags=re.DOTALL).strip()

    try:
        parsed_result = json.loads(cleaned)
    except json.JSONDecodeError:
        parsed_result = {
            "status": "Needs Correction",
            "flags": ["Invalid LLM response"],
            "notes": raw_text
        }

    return image_id, parsed_result