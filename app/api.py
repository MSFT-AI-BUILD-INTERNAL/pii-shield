"""
REST API for PII Shield.

Provides a simple REST API for PII detection and masking.
Requires: fastapi, uvicorn
"""

from typing import List, Optional

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except ImportError:
    raise ImportError(
        "FastAPI is required for the API module. "
        "Install with: pip install fastapi uvicorn"
    )

from core import PIIShield
from core.masker import MaskingStrategy


# Pydantic models for request/response
class DetectRequest(BaseModel):
    """Request model for PII detection."""
    text: str
    language: str = "en"
    entities: Optional[List[str]] = None
    score_threshold: float = 0.5


class DetectedEntity(BaseModel):
    """Model for a detected PII entity."""
    entity_type: str
    text: str
    start: int
    end: int
    score: float


class DetectResponse(BaseModel):
    """Response model for PII detection."""
    entities: List[DetectedEntity]
    count: int


class MaskRequest(BaseModel):
    """Request model for PII masking."""
    text: str
    language: str = "en"
    strategy: str = "replace"
    entities: Optional[List[str]] = None
    score_threshold: float = 0.5


class MaskResponse(BaseModel):
    """Response model for PII masking."""
    original_text: str
    masked_text: str
    entities: List[DetectedEntity]
    entity_count: dict


# Initialize FastAPI app
app = FastAPI(
    title="PII Shield API",
    description="API for PII Detection and Masking using Microsoft Presidio",
    version="0.1.0",
)

# Initialize PII Shield
shield = PIIShield()


def get_strategy(strategy_name: str) -> MaskingStrategy:
    """Convert strategy name to MaskingStrategy enum."""
    strategies = {
        "replace": MaskingStrategy.REPLACE,
        "redact": MaskingStrategy.REDACT,
        "hash": MaskingStrategy.HASH,
        "mask": MaskingStrategy.MASK,
    }
    return strategies.get(strategy_name, MaskingStrategy.REPLACE)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "PII Shield API",
        "version": "0.1.0",
        "endpoints": ["/detect", "/mask", "/entities"],
    }


@app.post("/detect", response_model=DetectResponse)
async def detect_pii(request: DetectRequest):
    """
    Detect PII entities in text.
    
    Args:
        request: DetectRequest with text and options.
    
    Returns:
        DetectResponse with detected entities.
    """
    try:
        results = shield.detect_only(
            text=request.text,
            language=request.language,
            entities=request.entities,
            score_threshold=request.score_threshold,
        )
        
        entities = [
            DetectedEntity(
                entity_type=r.entity_type,
                text=request.text[r.start:r.end],
                start=r.start,
                end=r.end,
                score=r.score,
            )
            for r in results
        ]
        
        return DetectResponse(entities=entities, count=len(entities))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mask", response_model=MaskResponse)
async def mask_pii(request: MaskRequest):
    """
    Detect and mask PII entities in text.
    
    Args:
        request: MaskRequest with text and options.
    
    Returns:
        MaskResponse with masked text and details.
    """
    try:
        strategy = get_strategy(request.strategy)
        
        result = shield.protect(
            text=request.text,
            language=request.language,
            entities=request.entities,
            strategy=strategy,
            score_threshold=request.score_threshold,
        )
        
        entities = [
            DetectedEntity(
                entity_type=e.entity_type,
                text=request.text[e.start:e.end],
                start=e.start,
                end=e.end,
                score=e.score,
            )
            for e in result.detected_entities
        ]
        
        return MaskResponse(
            original_text=result.original_text,
            masked_text=result.masked_text,
            entities=entities,
            entity_count=result.entity_count,
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/entities")
async def get_supported_entities(language: str = "en"):
    """
    Get list of supported PII entity types.
    
    Args:
        language: Language code.
    
    Returns:
        List of supported entity type names.
    """
    try:
        entities = shield.get_supported_entities(language)
        return {"language": language, "entities": entities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the API server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
