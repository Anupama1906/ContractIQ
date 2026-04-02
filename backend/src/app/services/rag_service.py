import sys
from pathlib import Path

# Structure: backend/src/app/services/rag_service.py
# Needs to go up to find the 'ai' directory
ai_path = str(Path(__file__).resolve().parents[4] / "ai")
if ai_path not in sys.path:
    sys.path.insert(0, ai_path)

from evaluator import evaluate_contract

def evaluate_document_stream(anonymized_text: str):
    """
    Acts as a pass-through for the AI generator to support live streaming.
    """
    # evaluate_contract is already a generator that yields JSON updates
    for step_data in evaluate_contract(anonymized_text):
        yield step_data