from app.services.reconcile import build_sample_request, reconcile


def main() -> None:
    report = reconcile(build_sample_request())

    print("Warehouse Reconciliation Engine")
    print("===============================")
    print(f"Dataset: {report.dataset_name}")
    print(f"Source rows: {report.source_rows}")
    print(f"Warehouse rows: {report.warehouse_rows}")
    print(f"Overall score: {report.overall_score}")
    print()

    for finding in report.findings:
        print(f"[{finding.severity.upper()}] {finding.code} (score {finding.score})")
        print(f"Summary: {finding.summary}")
        print("Evidence:")
        for item in finding.evidence:
            print(f"  - {item}")
        print(f"Next action: {finding.recommended_next_action}")
        print()
