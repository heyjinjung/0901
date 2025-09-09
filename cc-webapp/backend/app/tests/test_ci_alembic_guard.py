import os
import subprocess


def test_alembic_upgrade_head_guard():
    if os.getenv("CI_ENFORCE_ALEMBIC_UPGRADE", "0") != "1":
        import pytest
        pytest.skip("CI guard disabled")

    # Run alembic upgrade head in a subprocess; expect success.
    # This assumes running inside the backend container.
    proc = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
    assert proc.returncode == 0, f"alembic upgrade head failed: {proc.stderr or proc.stdout}"
