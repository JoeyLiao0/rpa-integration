import sys
sys.path.append('')

from RpaTools import *
from configLoader import config

# config导入
sleep_interval = config.get_sleep_interval()
short_sleep = config.get_short_sleep()

if not init_bpm_client():
    sys.stderr.write("BPM平台认证失败\n")
    sys.exit(1)

need_sleep = False
sleep_cnt = 0
loop_cnt = 0
while True:
    if need_sleep:
        sleep_cnt = sleep_cnt + 1
        time.sleep(sleep_interval)
        print(f"第 {sleep_cnt} 次休眠！")
    else:
        time.sleep(short_sleep)

    need_sleep = True
    if check_work_item():
        print("检测到工作项")
        # click_work_item()
        rpa_data = get_work_item_data() # 获取tasklist中有，且在mapping中的task消息
        if rpa_data == {}:
            print("未发现符合条件的RPA任务")
            continue
        print("获取RPA数据")

        trigger_rpa(rpa_data)
        print("RPA流程完成")

        finish_work_item(rpa_data)
        print("工作项处理完成")

        need_sleep = False
    else:
        print("暂无工作项")

    loop_cnt = loop_cnt + 1
    print(f"第 {loop_cnt} 次轮询！")
