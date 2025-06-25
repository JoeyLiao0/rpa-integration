import re
from fileTools import *
from configLoader import config
from bpmApiClient import create_bpm_client

# 全局BMP客户端实例
bpm_client = None

def init_bpm_client():
    """初始化BPM客户端"""
    global bpm_client
    platform = config.get_api_platform()
    bpm_client = create_bpm_client(platform)
    return bpm_client.authenticate()


def get_bpm_client():
    global bpm_client
    if bpm_client is None:
        init_bpm_client()
    return bpm_client


def check_work_item():
    client = get_bpm_client()
    if not client:
        return False

    tasks = client.get_task_list()
    return len(tasks) > 0


def get_work_item_data():
    client = get_bpm_client()
    if not client:
        return {}

    tasks = client.get_task_list()
    if not tasks:
        return {}

    task = tasks[0]
    task_data = client.get_task_data(task.get('id', ''))

    res = {}
    res["taskName"] = task_data.get('name', '')
    res["taskId"] = task_data.get('id', '')
    return res


def trigger_rpa(data):
    taskname = data["taskName"]
    filename = RF_DICT.get(taskname, '')
    if filename:
        create_file(filename)
        wait_delete_file(filename)


def finish_work_item(task_data=None):
    client = get_bpm_client()
    if not client or not task_data:
        return False

    task_id = task_data.get("taskId", "")
    if task_id:
        return client.complete_task(task_id)
    return False


def match_taskname(taskname):
    pattern = re.compile(r'RPA_([a-zA-Z0-9]+)_([a-zA-Z0-9]+)')
    return re.fullmatch(pattern, taskname) != None


def start_IBP(pname):
    client = get_bpm_client()
    if not client:
        return False

    return client.start_process(pname)


def validate_work_item(dict, superman_items):
    client = get_bpm_client()
    if not client:
        return False

    res = False
    tasks = client.get_task_list()

    for task in tasks:
        taskname = task.get('name', '')
        task_id = task.get('id', '')

        if taskname in superman_items:
            start_IBP(superman_items[taskname])
            continue

        if match_taskname(taskname) and taskname not in dict:
            res = True
            dict[taskname] = (task_id, 0)
            print(f"Check in work item {taskname}")

    return res


def get_work_item_data_superman(taskname):
    res = {}
    name_list = taskname.split('_')
    res["userName"] = name_list[1]
    res["taskName"] = name_list[2]
    return res

# 兼容学长代码
def click_work_item():
    pass


def get_taskname():
    client = get_bpm_client()
    if not client:
        return ""

    tasks = client.get_task_list()
    if not tasks:
        return ""

    return tasks[0].get('name', '')


def send_work_item_by_id(task_id):
    client = get_bpm_client()
    if not client:
        return {}

    task_data = client.get_task_data(task_id)
    return task_data


def complete_task_by_id(task_id):
    client = get_bpm_client()
    if not client:
        return False

    return client.complete_task(task_id)