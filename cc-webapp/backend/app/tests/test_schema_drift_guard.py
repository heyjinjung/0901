import pytest
from app.utils.schema_drift_guard import check_schema_drift


@pytest.mark.migration
def test_no_critical_schema_drift_after_upgrade():
    """Alembic upgrade 후 치명적 드리프트가 없어야 한다.

    실패 시 보고서/오류 정보를 출력하여 디버깅 용이성 향상.
    """
    critical, report = check_schema_drift(return_report=True)

    # 오류 자체를 우선 표시
    assert "error" not in report, f"Schema drift guard error: {report.get('error')}"
    assert critical is False, f"Critical schema drift detected. Report={report}"
