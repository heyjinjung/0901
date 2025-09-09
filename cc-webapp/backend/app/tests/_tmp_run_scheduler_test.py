import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

flag = {'fired': False}

def _set_flag(flag):
    flag['fired'] = True

scheduler = BackgroundScheduler()
run_time = datetime.now() + timedelta(seconds=1)
scheduler.add_job(_set_flag, 'date', run_date=run_time, args=[flag])
scheduler.start()
start = time.time()
while time.time() - start < 5 and not flag['fired']:
    time.sleep(0.1)
scheduler.shutdown(wait=False)
print('Fired=', flag['fired'])
