from fastapi import APIRouter

router = APIRouter(prefix="/v1/claims", tags=["claims"])


@router.post("")
def create_claim() -> dict[str, str]:
    return {"status": "accepted"}


@router.post("/{claim_id}/run-ai")
def run_claim_ai(claim_id: str) -> dict[str, str]:
    return {"claim_id": claim_id, "status": "processing"}


@router.post("/{claim_id}/override")
def supervisor_override(claim_id: str) -> dict[str, str]:
    return {"claim_id": claim_id, "status": "override-recorded"}
