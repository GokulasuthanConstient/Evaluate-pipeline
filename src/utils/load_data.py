import os
import json


def load_extracted_jsonl(file_path):
    """
    Reads a .jsonl file where each line is a separate JSON object.
    Returns a dictionary mapping image_id to extracted_parse data.
    """
    data = {}
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():  # Skip empty lines
                content = json.loads(line)
                image_id = content.get('image')
                extracted = content.get('extracted_parse')
                if image_id and extracted:
                    data[image_id] = extracted
    return data



def load_jsonl(file_path):
    """
    Reads a .jsonl file where each line is a separate JSON object.
    Returns a dictionary mapping image_id to ground truth data.
    """
    data = {}
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():  # Skip empty lines
                content = json.loads(line)
                image_id = content.get('image')
                gt = content.get('ground_truth', {}).get('gt_parse')
                if image_id and gt:
                    data[image_id] = gt
    return data


if __name__ == '__main__':
    json_data = load_jsonl(r'D:\Ragas\dataset\downloaded dataset\downloaded_dataset\ground_truth.jsonl')