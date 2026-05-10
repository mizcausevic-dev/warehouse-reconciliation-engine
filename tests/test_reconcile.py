from app.services.reconcile import build_sample_request, reconcile


def test_sample_request_loads():
    request = build_sample_request()
    assert request.dataset_name == "revops_bookings_settlement"
    assert len(request.source_records) == 9
    assert len(request.warehouse_records) == 9


def test_reconciliation_finds_multiple_issue_families():
    report = reconcile(build_sample_request())
    codes = {finding.code for finding in report.findings}
    assert report.overall_score >= 80
    assert "missing_rows" in codes
    assert "extra_rows" in codes
    assert "freshness_lag" in codes
