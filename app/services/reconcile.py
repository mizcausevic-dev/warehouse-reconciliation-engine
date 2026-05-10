import json
from datetime import UTC, datetime
from pathlib import Path

from app.models import Finding, ReconciliationReport, ReconciliationRequest, SettlementRecord

SAMPLE_DATA_PATH = Path("data/sample_settlement.json")


def build_sample_request() -> ReconciliationRequest:
    with SAMPLE_DATA_PATH.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return ReconciliationRequest.model_validate(payload)


def reconcile(request: ReconciliationRequest) -> ReconciliationReport:
    findings: list[Finding] = []

    if missing := missing_rows(request):
        findings.append(missing)

    if extra := extra_rows(request):
        findings.append(extra)

    if amounts := amount_drift(request):
        findings.append(amounts)

    if statuses := status_drift(request):
        findings.append(statuses)

    if freshness := freshness_lag(request):
        findings.append(freshness)

    overall_score = max((finding.score for finding in findings), default=18)

    return ReconciliationReport(
        dataset_name=request.dataset_name,
        source_rows=len(request.source_records),
        warehouse_rows=len(request.warehouse_records),
        overall_score=overall_score,
        evaluated_at=datetime.now(UTC),
        findings=findings,
    )


def _source_map(request: ReconciliationRequest) -> dict[str, SettlementRecord]:
    return {record.record_id: record for record in request.source_records}


def _warehouse_map(request: ReconciliationRequest) -> dict[str, SettlementRecord]:
    return {record.record_id: record for record in request.warehouse_records}


def missing_rows(request: ReconciliationRequest) -> Finding | None:
    source = _source_map(request)
    warehouse = _warehouse_map(request)
    missing = sorted(record_id for record_id in source if record_id not in warehouse)
    if not missing:
        return None

    return Finding(
        code="missing_rows",
        severity="high",
        score=84,
        summary="Source rows are missing from the warehouse snapshot.",
        evidence=[f"missing warehouse records: {', '.join(missing)}"],
        recommended_next_action="Restore ingestion for missing records and block downstream trust until row parity is restored.",
    )


def extra_rows(request: ReconciliationRequest) -> Finding | None:
    source = _source_map(request)
    warehouse = _warehouse_map(request)
    extra = sorted(record_id for record_id in warehouse if record_id not in source)
    if not extra:
        return None

    return Finding(
        code="extra_rows",
        severity="moderate",
        score=72,
        summary="Warehouse rows exist without a matching source-of-truth record.",
        evidence=[f"orphan warehouse records: {', '.join(extra)}"],
        recommended_next_action="Trace replay or stale persistence paths and remove rows that no longer map to valid source records.",
    )


def amount_drift(request: ReconciliationRequest) -> Finding | None:
    source = _source_map(request)
    warehouse = _warehouse_map(request)
    evidence: list[str] = []

    for record_id in sorted(set(source).intersection(warehouse)):
        source_amount = source[record_id].amount
        warehouse_amount = warehouse[record_id].amount
        delta = abs(source_amount - warehouse_amount)
        if delta > request.amount_tolerance:
            evidence.append(
                f"{record_id} source={source_amount:.0f} warehouse={warehouse_amount:.0f} delta={delta:.0f}"
            )

    if not evidence:
        return None

    return Finding(
        code="amount_drift",
        severity="high",
        score=79,
        summary="Warehouse monetary values are outside the accepted tolerance window.",
        evidence=evidence,
        recommended_next_action="Quarantine mismatched rows and confirm the transformation or currency logic before finance reporting uses these totals.",
    )


def status_drift(request: ReconciliationRequest) -> Finding | None:
    source = _source_map(request)
    warehouse = _warehouse_map(request)
    evidence: list[str] = []

    for record_id in sorted(set(source).intersection(warehouse)):
        source_status = source[record_id].status
        warehouse_status = warehouse[record_id].status
        if source_status != warehouse_status:
            evidence.append(
                f"{record_id} source_status={source_status} warehouse_status={warehouse_status}"
            )

    if not evidence:
        return None

    return Finding(
        code="status_drift",
        severity="moderate",
        score=68,
        summary="Warehouse lifecycle state is lagging the source-of-truth system.",
        evidence=evidence,
        recommended_next_action="Refresh state synchronization and prevent downstream workflow automation from trusting outdated statuses.",
    )


def freshness_lag(request: ReconciliationRequest) -> Finding | None:
    age_minutes = int((datetime.now(UTC) - request.generated_at).total_seconds() / 60)
    if age_minutes <= request.allowed_freshness_minutes:
        return None

    return Finding(
        code="freshness_lag",
        severity="critical",
        score=91,
        summary="Warehouse load freshness is outside the allowed sync window.",
        evidence=[
            f"snapshot is {age_minutes} minute(s) old",
            f"allowed sync window is {request.allowed_freshness_minutes} minute(s)",
        ],
        recommended_next_action="Restore the warehouse sync and halt reporting that assumes current-state settlement data.",
    )
