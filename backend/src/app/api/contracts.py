import os
import uuid
import json
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.anonymization_service import anonymize_document
from app.services.rag_service import evaluate_document_stream

router = APIRouter()

UPLOAD_DIR = "storage/uploads"
PROCESSED_DIR = "storage/processed"

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)


@router.post("/anonymize")
async def anonymize_contract(file: UploadFile = File(...)):
    try:
        # Generate unique ID
        document_id = str(uuid.uuid4())

        if not file.filename:
            raise HTTPException(status_code=400, detail="File name is missing")

        # Save uploaded file
        file_extension = file.filename.split(".")[-1]
        file_path = os.path.join(UPLOAD_DIR, f"{document_id}.{file_extension}")

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Call anonymization service
        result = anonymize_document(file_path)

        # Save processed output (important for next step)
        processed_data = {
            "document_id": document_id,
            "file_path": file_path,
            "raw_text": result["raw_text"],
            "anonymized_text": result["anonymized_text"],
            "mapping_dict": result["mapping_dict"],
            "status": "ANONYMIZED"
        }

        processed_file_path = os.path.join(PROCESSED_DIR, f"{document_id}.json")

        with open(processed_file_path, "w") as f:
            json.dump(processed_data, f, indent=4)

        # Return response to frontend
        return {
            "document_id": document_id,
            "raw_text": result["raw_text"],
            "anonymized_text": result["anonymized_text"],
            "mapping_dict": result["mapping_dict"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

## evaluation endpoint
class EvaluateRequest(BaseModel):
    document_id: str


@router.post("/evaluate")
async def evaluate_contract(request: EvaluateRequest):
    try:
        document_id = request.document_id
        processed_file_path = os.path.join(PROCESSED_DIR, f"{document_id}.json")

        # Verify document exists
        if not os.path.exists(processed_file_path):
            raise HTTPException(status_code=404, detail="Document not found")

        with open(processed_file_path, "r") as f:
            data = json.load(f)

        # Check state
        if data.get("status") != "ANONYMIZED":
            raise HTTPException(
                status_code=400,
                detail="Document not ready for evaluation"
            )

        anonymized_text = data["anonymized_text"]

        # Streaming generator to pipe updates from ai/evaluator.py to the frontend
        def event_generator():
            # Iterate through the generator yielded by the service
            for step_data in evaluate_document_stream(anonymized_text):
                # Update status locally if the final agent finishes
                if step_data["agent"] == "evaluate":
                    data["status"] = "EVALUATED"
                    data["report"] = step_data.get("final_report")
                    data["risk_score"] = step_data.get("risk_score")
                    
                    with open(processed_file_path, "w") as f:
                        json.dump(data, f, indent=4)

                # Yield as Newline-Delimited JSON (NDJSON)
                yield json.dumps(step_data) + "\n"

        return StreamingResponse(event_generator(), media_type="application/x-ndjson")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))