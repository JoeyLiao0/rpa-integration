import sys
sys.path.append('')

from RpaTools import *

# open taskList
url = "http://localhost:8080/tasklist"
driver = open_chrome_page(url)
driver.implicitly_wait(10)

login(driver, "demo", "demo")
driver.implicitly_wait(10)

need_sleep = False
sleep_cnt = 0
loop_cnt = 0
while True:
    if need_sleep:
        sleep_cnt = sleep_cnt + 1
        time.sleep(60)
        print(f"sleep {sleep_cnt}!")
    else:
        time.sleep(2)

    need_sleep = True
    if check_work_item(driver):
        print("have work item")
        time.sleep(1)

        click_work_item(driver)
        print("click work item")
        time.sleep(1)

        rpa_data = get_work_item_data(driver)
        print("get RPA data")
        time.sleep(1)

        trigger_rpa(rpa_data)
        print("RPA process finish")
        time.sleep(1)

        finish_work_item(driver)
        print("finish work item")
        time.sleep(1)
        need_sleep = False
    else:
        print("no work item")

    loop_cnt = loop_cnt + 1
    print(f"loop {loop_cnt}!")
