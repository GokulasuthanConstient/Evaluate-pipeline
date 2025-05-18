
from langchain.schema import Document
import json
from pymongo import MongoClient


client = MongoClient("mongodb://localhost:27017/")
db = client["Learning"]
collection = db["A4_finance"]

docs = []
for doc in collection.find():
    # Convert extracted_parse object to JSON string
    extracted_parse_obj = doc.get("extracted_parse", {})
    text_content = json.dumps(extracted_parse_obj, indent=2)

    metadata = {
        "id": str(doc.get("_id")),
        "image": doc.get("image", None),
        # add any other metadata fields you want here
    }

    docs.append(Document(page_content=text_content, metadata=metadata))

print(f"Loaded {len(docs)} documents")
print(docs[0].page_content)  # prints first document's content as JSON string