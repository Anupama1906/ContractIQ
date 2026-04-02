import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "ai"))

from evaluator import evaluate_contract

def evaluate_document(anonymized_text: str):
    # """
    # Mock RAG + Agent evaluation.
    # Replace later with real implementation.
    # """

    # # 🔴 Replace later with real RAG pipeline
    # return {
    #     "report": f"Analysis of document:\n\n{anonymized_text[:200]}...",
    #     "risk_score": 0.75,
    #     "risk_level": "HIGH",
    #     "audit_trail": [
    #         {"step": "AUDITOR", "message": "Detected missing liability clause"},
    #         {"step": "ATTACKER", "message": "Challenged severity"},
    #         {"step": "AUDITOR", "message": "Upgraded to HIGH risk"}
    #     ]
    # }

    evaluation_report = evaluate_contract(anonymized_text)
    
    



