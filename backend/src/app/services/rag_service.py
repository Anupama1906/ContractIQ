import sys
from pathlib import Path

# Ensure the 'ai' directory is in the path
# Structure: backend/src/app/services/rag_service.py (5 levels to root)
ai_path = str(Path(__file__).resolve().parents[4] / "ai")
if ai_path not in sys.path:
    sys.path.insert(0, ai_path)

from evaluator import evaluate_contract

def evaluate_document(anonymized_text: str):
    """
    Consumes the generator from the AI evaluator and returns the final 
    processed dictionary required by the API.
    """
    # evaluate_contract is a generator that yields state dictionaries
    generator = evaluate_contract(anonymized_text)
    
    final_state = None
    
    # Iterate to the end of the stream to get the final result
    for state in generator:
        final_state = state

    if not final_state:
        raise Exception("Evaluation failed: No results were yielded by the AI service.")

    # Map the internal AI state keys to the keys expected by contracts.py
    return {
        "report": final_state.get("risk_analyzed_report", "No report generated"),
        "risk_score": final_state.get("risk_score", 0.0),
        "risk_level": final_state.get("risk_level", "UNKNOWN")
    }