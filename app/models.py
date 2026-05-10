from datetime import datetime

from pydantic import BaseModel, Field


class SettlementRecord(BaseModel):
    record_id: str
    account_id: str
    amount: float = Field(ge=0)
    status: str
    owner_email: str


class ReconciliationRequest(BaseModel):
    dataset_name: str
    generated_at: datetime
    allowed_freshness_minutes: int = Field(gt=0)
    amount_tolerance: float = Field(ge=0)
    source_records: list[SettlementRecord]
    warehouse_records: list[SettlementRecord]


class Finding(BaseModel):
    code: str
    severity: str
    score: int
    summary: str
    evidence: list[str]
    recommended_next_action: str


class ReconciliationReport(BaseModel):
    dataset_name: str
    source_rows: int
    warehouse_rows: int
    overall_score: int
    evaluated_at: datetime
    findings: list[Finding]


class HealthResponse(BaseModel):
    status: str
    service: str
    docs: str
    sample_dataset: str
