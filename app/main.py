from pathlib import Path

from fastapi import FastAPI

from app.models import HealthResponse, ReconciliationRequest
from app.services.reconcile import build_sample_request, reconcile

app = FastAPI(
    title="Warehouse Reconciliation Engine",
    version="0.1.0",
    description="Warehouse trust backend for source-to-warehouse reconciliation, drift scoring, and settlement review.",
)


@app.get("/", response_model=HealthResponse)
def root() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="warehouse-reconciliation-engine",
        docs="/docs",
        sample_dataset=str(Path("data/sample_settlement.json")),
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="warehouse-reconciliation-engine",
        docs="/docs",
        sample_dataset=str(Path("data/sample_settlement.json")),
    )


@app.get("/api/sample")
def sample_reconciliation():
    return reconcile(build_sample_request())


@app.post("/api/reconcile")
def reconcile_dataset(request: ReconciliationRequest):
    return reconcile(request)
