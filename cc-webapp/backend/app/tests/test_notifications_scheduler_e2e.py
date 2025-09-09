import time
import threading
from datetime import datetime, timedelta

import pytest
from apscheduler.schedulers.background import BackgroundScheduler

# Lightweight E2E simulation: schedule a job to set a flag and verify it runs

def _set_flag(flag):
    flag['fired'] = True


def test_apscheduler_runs_job(tmp_path):
    flag = {'fired': False}
    scheduler = BackgroundScheduler()
    run_time = datetime.now() + timedelta(seconds=1)
    scheduler.add_job(_set_flag, 'date', run_date=run_time, args=[flag])
    scheduler.start()

    # wait up to 5s for job
    timeout = 5
    start = time.time()
    while time.time() - start < timeout and not flag['fired']:
        time.sleep(0.1)

    scheduler.shutdown(wait=False)
    assert flag['fired'] is True
