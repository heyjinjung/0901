import logging
from typing import List, Dict, Any
import requests
from app.core.config import settings

log = logging.getLogger(__name__)

class ClickHouseClient:
    def __init__(self):
        self.base = settings.CLICKHOUSE_URL.rstrip("/")
        self.db = settings.CLICKHOUSE_DATABASE
        self.params = {}
        if settings.CLICKHOUSE_USER:
            self.params["user"] = settings.CLICKHOUSE_USER
        if settings.CLICKHOUSE_PASSWORD:
            self.params["password"] = settings.CLICKHOUSE_PASSWORD

    def execute(self, sql: str) -> str:
        r = requests.post(
            f"{self.base}/?database={self.db}",
            params=self.params,
            data=sql.encode("utf-8"),
            timeout=10,
        )
        if not r.ok:
            # Log body for diagnostics and include a short preview of SQL
            preview = sql.replace("\n", " ")
            if len(preview) > 200:
                preview = preview[:200] + "..."
            log.error("ClickHouse HTTP %s: %s | sql: %s", r.status_code, r.text.strip(), preview)
            r.raise_for_status()
        return r.text

    def init_schema(self):
        self.execute(f"CREATE DATABASE IF NOT EXISTS {self.db}")
        self.execute("""
        CREATE TABLE IF NOT EXISTS user_actions (
            user_id Int32,
            action_type LowCardinality(String),
            client_ts DateTime64(3) DEFAULT now(),
            server_ts DateTime64(3) DEFAULT now(),
            context_json String CODEC(ZSTD),
            day Date DEFAULT today()
        ) ENGINE = MergeTree()
        PARTITION BY toYYYYMM(day)
        ORDER BY (day, user_id, action_type)
        """)
        self.execute("""
        CREATE TABLE IF NOT EXISTS rewards (
            user_id Int32,
            reward_type LowCardinality(String),
            reward_value Int64,
            source LowCardinality(String),
            awarded_at DateTime64(3) DEFAULT now(),
            day Date DEFAULT today()
        ) ENGINE = MergeTree()
        PARTITION BY toYYYYMM(day)
        ORDER BY (day, user_id, reward_type)
        """)
        self.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            user_id Int32,
            code LowCardinality(String),
            quantity Int32,
            total_price_cents Int64,
            gems_granted Int32,
            charge_id String,
            purchased_at DateTime64(3) DEFAULT now(),
            day Date DEFAULT today()
        ) ENGINE = MergeTree()
        PARTITION BY toYYYYMM(day)
        ORDER BY (day, user_id, code)
        """)
        # Aggregates: daily revenue/quantity by code
        self.execute("""
        CREATE TABLE IF NOT EXISTS purchases_daily_agg (
            day Date,
            code LowCardinality(String),
            total_revenue_cents Int64,
            total_quantity Int64
        ) ENGINE = SummingMergeTree()
        PARTITION BY toYYYYMM(day)
        ORDER BY (day, code)
        """)
        self.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_purchases_daily_agg
        TO purchases_daily_agg AS
        SELECT day, code,
               sum(total_price_cents) AS total_revenue_cents,
               sum(quantity) AS total_quantity
        FROM purchases
        GROUP BY day, code
        """)

        # A/B flags assignments (optional, for analysis)
        self.execute("""
        CREATE TABLE IF NOT EXISTS ab_flags (
            user_id Int32,
            flag_key LowCardinality(String),
            variant LowCardinality(String),
            assigned_at DateTime64(3) DEFAULT now(),
            day Date DEFAULT today()
        ) ENGINE = MergeTree()
        PARTITION BY toYYYYMM(day)
        ORDER BY (day, flag_key, variant, user_id)
        """)

    def get_buy_funnel(self, days: int = 7) -> List[Dict[str, Any]]:
        # Build a simple funnel from actions and purchases
        sql = f"""
        SELECT stage, cnt FROM (
            SELECT 'open_shop' AS stage, uniqExact(user_id) AS cnt
            FROM user_actions
            WHERE action_type = 'OPEN_SHOP' AND day BETWEEN today()-{days-1} AND today()
        )
        UNION ALL
        SELECT stage, cnt FROM (
            SELECT 'buy_click' AS stage, uniqExact(user_id) AS cnt
            FROM user_actions
            WHERE action_type = 'BUY_CLICK' AND day BETWEEN today()-{days-1} AND today()
        )
        UNION ALL
        SELECT stage, cnt FROM (
            SELECT 'buy_success' AS stage, uniqExact(user_id) AS cnt
            FROM purchases
            WHERE day BETWEEN today()-{days-1} AND today()
        )
        ORDER BY stage
        """
        out = self.execute(sql).strip()
        rows: List[Dict[str, Any]] = []
        if not out:
            return rows
        for line in out.splitlines():
            parts = line.split('\t')
            if len(parts) != 2:
                continue
            stage, cnt = parts[0], parts[1]
            try:
                rows.append({"stage": stage, "count": int(cnt)})
            except ValueError:
                log.warning("Unexpected CH count value: %s", cnt)
        return rows

    def insert_actions(self, rows: List[Dict[str, Any]]):
        if not rows:
            return
        # Rely on ClickHouse defaults for Date/DateTime columns to avoid format issues
        data = "\n".join("\t".join([
            str(int(r.get("user_id") or 0)),
            str(r.get("action_type") or ""),
            str(r.get("context_json") or "{}"),
        ]) for r in rows)
        sql = "INSERT INTO user_actions (user_id, action_type, context_json) FORMAT TSV\n" + data
        self.execute(sql)

    def insert_rewards(self, rows: List[Dict[str, Any]]):
        if not rows:
            return
        # Let ClickHouse set awarded_at/day via defaults
        data = "\n".join("\t".join([
            str(int(r.get("user_id") or 0)),
            str(r.get("reward_type") or ""),
            str(int(r.get("reward_value") or 0)),
            str(r.get("source") or ""),
        ]) for r in rows)
        sql = "INSERT INTO rewards (user_id, reward_type, reward_value, source) FORMAT TSV\n" + data
        self.execute(sql)

    def insert_purchases(self, rows: List[Dict[str, Any]]):
        if not rows:
            return
        # Insert without explicit purchased_at to use DEFAULT now() and computed day
        lines: List[str] = []
        for r in rows:
            user_id = str(int(r.get("user_id") or 0))
            code = str(r.get("code") or "")
            quantity = str(int(r.get("quantity") or 0))
            total_price = str(int(r.get("total_price_cents") or 0))
            gems = str(int(r.get("gems_granted") or 0))
            charge_id = str(r.get("charge_id") or "")
            lines.append("\t".join([user_id, code, quantity, total_price, gems, charge_id]))
        data = "\n".join(lines)
        sql = "INSERT INTO purchases (user_id, code, quantity, total_price_cents, gems_granted, charge_id) FORMAT TSV\n" + data
        self.execute(sql)