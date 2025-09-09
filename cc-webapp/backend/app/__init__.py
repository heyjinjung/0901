"""Initialize app package and apply compatibility patches."""

from sqlalchemy.engine import Engine


def _engine_execute(self: Engine, *args, **kwargs):
    """Provide Engine.execute compatibility for SQLAlchemy 2.x."""
    with self.connect() as conn:
        return conn.execute(*args, **kwargs)


if not hasattr(Engine, "execute"):
    Engine.execute = _engine_execute  # type: ignore[attr-defined]

