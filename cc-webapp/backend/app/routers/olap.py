from fastapi import APIRouter
from app.core.config import settings
from app.olap.clickhouse_client import ClickHouseClient

router = APIRouter()

@router.get("/api/olap/health")
def olap_health():
    if not settings.CLICKHOUSE_ENABLED:
        return {"enabled": False}
    client = ClickHouseClient()
    try:
        client.init_schema()
        client.execute("SELECT 1")
        return {"enabled": True, "clickhouse": "ok"}
    except Exception as e:
        return {"enabled": True, "clickhouse": f"error: {e}"}