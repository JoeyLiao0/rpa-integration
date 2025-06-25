import sys
sys.path.append('')

from RpaTools import *
from configLoader import config

# config导入
sleep_interval = config.get_sleep_interval()
short_sleep = config.get_short_sleep()

if not init_bpm_client():
    print("Failed to authenticate with BPM platform")
    sys.exit(1)

need_sleep = False
sleep_cnt = 0
loop_cnt = 0
while True:
    if need_sleep:
        sleep_cnt = sleep_cnt + 1
        time.sleep(sleep_interval)
        print(f"sleep {sleep_cnt}!")
    else:
        time.sleep(short_sleep)

    need_sleep = True
    if check_work_item():
        print("have work item")
        time.sleep(1)

        click_work_item()
        print("click work item")
        time.sleep(1)

        rpa_data = get_work_item_data()
        print("get RPA data")
        time.sleep(1)

        trigger_rpa(rpa_data)
        print("RPA process finish")
        time.sleep(1)

        finish_work_item(rpa_data)
        print("finish work item")
        time.sleep(1)
        need_sleep = False
    else:
        print("no work item")

    loop_cnt = loop_cnt + 1
    print(f"loop {loop_cnt}!")