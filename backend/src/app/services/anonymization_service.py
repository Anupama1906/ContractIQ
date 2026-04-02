import uuid
import sys
from pathlib import Path

# Add ai directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "ai"))

from helper import pdf_to_markdown, anonymizer

def anonymize_document(file_path: str):

    extracted_text = pdf_to_markdown(file_path)
    anonymized_text_and_dictionary_tuple = anonymizer(extracted_text)

    return {
        "raw_text": extracted_text,
        "anonymized_text": anonymized_text_and_dictionary_tuple[0],
        "mapping_dict": anonymized_text_and_dictionary_tuple[1]
    }
