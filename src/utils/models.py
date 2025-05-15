from pydantic import BaseModel, field_validator,ConfigDict
from typing import List
import re


class Header(BaseModel):
    invoice_no: str
    invoice_date: str
    seller: str
    client: str
    seller_tax_id: str
    client_tax_id: str
    iban: str

    @field_validator("invoice_date")
    def validate_date(cls, v):
        if not re.match(r"\d{2}/\d{2}/\d{4}", v):
            raise ValueError("Invalid date format, expected MM/DD/YYYY")
        return v



class Item(BaseModel):
    item_desc: str
    item_qty: str
    item_net_price: str
    item_net_worth: str
    item_vat: str
    item_gross_worth: str

    model_config = ConfigDict(extra="forbid")  # Disallow extra fields


class Summary(BaseModel):
    total_net_worth: str
    total_vat: str
    total_gross_worth: str


class InvoiceParse(BaseModel):
    header: Header
    items: List[Item]
    summary: Summary
