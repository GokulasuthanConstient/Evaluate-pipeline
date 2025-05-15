import json
import os
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ValidationError, field_validator, model_validator

# --- Validators ---
def non_empty_string(value: str, field_name: str) -> str:
    if not value.strip():
        raise ValueError(f"Field '{field_name}' cannot be empty or whitespace")
    return value

# --- Models ---
class ItemRow(BaseModel):
    item_desc: str
    item_qty: str
    item_net_price: str
    item_net_worth: str
    item_vat: str
    item_gross_worth: str

    @field_validator('*')
    @classmethod
    def validate_non_empty(cls, value, info):
        return non_empty_string(value, info.field_name)


class Summary(BaseModel):
    total_net_worth: Optional[str]
    total_vat: Optional[str]
    total_gross_worth: Optional[str]

    @field_validator('total_net_worth', 'total_vat', 'total_gross_worth')
    @classmethod
    def validate_optional_str(cls, value):
        if value and not value.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return value


class Header(BaseModel):
    invoice_no: str
    invoice_date: str
    seller: str
    client: str
    seller_tax_id: str
    client_tax_id: str
    iban: str

    @field_validator('*')
    @classmethod
    def validate_non_empty(cls, value, info):
        return non_empty_string(value, info.field_name)

    @field_validator('invoice_date')
    @classmethod
    def validate_invoice_date(cls, v):
        try:
            datetime.strptime(v, "%m/%d/%Y")
        except ValueError:
            raise ValueError(f"Invalid date format for invoice_date: {v}. Must be MM/DD/YYYY")
        return v


class Position(BaseModel):
    page: int
    x: Optional[int] = None
    y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    table_region: Optional[dict] = None

    @field_validator('page')
    @classmethod
    def page_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Page number must be greater than 0")
        return v


class ExtractedField(BaseModel):
    label: str
    value: str
    position: Position

    @field_validator('label')
    @classmethod
    def label_cannot_be_empty(cls, v):
        return non_empty_string(v, 'label')

    @field_validator('value')
    @classmethod
    def validate_value(cls, v):
        if not v.strip():
            raise ValueError("Value cannot be empty or whitespace string")
        return v


class InvoiceExtraction(BaseModel):
    image: str
    ground_truth: dict
    extracted_parse: dict

    @model_validator(mode='after')
    def check_extracted_data(self):
        extracted_data = self.extracted_parse
        ground_truth = self.ground_truth

        if not extracted_data or not ground_truth:
            raise ValueError("Missing extracted or ground truth data.")

        extracted_header = extracted_data.get('gt_parse', {}).get('header', {})
        ground_truth_header = ground_truth.get('gt_parse', {}).get('header', {})

        for key, extracted_value in extracted_header.items():
            ground_truth_value = ground_truth_header.get(key)
            if extracted_value.strip() != ground_truth_value.strip():
                raise ValueError(f"Mismatch in field '{key}'. Extracted: {extracted_value}, Ground Truth: {ground_truth_value}")

        return self


def validate_invoices(ground_truth_file_path: str, extracted_file_path: str):
    with open(ground_truth_file_path, 'r', encoding='utf-8') as gt_file:
        ground_truth_lines = gt_file.readlines()

    with open(extracted_file_path, 'r', encoding='utf-8') as ext_file:
        extracted_lines = ext_file.readlines()

    if len(ground_truth_lines) != len(extracted_lines):
        print("❌ Mismatch in number of lines between ground truth and extracted files.")
        return

    for idx, (gt_line, ext_line) in enumerate(zip(ground_truth_lines, extracted_lines)):
        try:
            ground_truth_data = json.loads(gt_line)
            extracted_data = json.loads(ext_line)

            extracted_data['ground_truth'] = ground_truth_data.get("ground_truth")

            InvoiceExtraction.model_validate(extracted_data)
            print(f"✅ Line {idx + 1} is valid and matches the ground truth.")
        except ValidationError as e:
            print(f"❌ Validation failed for line {idx + 1}: {e.json(indent=2)}")
        except Exception as ex:
            print(f"❌ Error parsing line {idx + 1}: {ex}")


if __name__ == "__main__":
    validate_invoices(
        r"D:\Evaluate-pipeline\src\downloaded_dataset\ground_truth_14052025.jsonl",
        r"D:\Evaluate-pipeline\src\downloaded_dataset\extracted_data.jsonl"
    )
    

