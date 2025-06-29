import os
import time
import openpyxl
import sys
from configLoader import config

from uipathClient import get_uipath_orchestrator

RF_DICT = config.get_rpa_filename_mapping()


def trigger_rpa_job(filename):
    """
    使用 UiPath REST API 触发 RPA 流程
    """
    print(f"尝试触发 RPA 流程: {filename}")

    try:
        # 获取 UiPath 实例
        uipath = get_uipath_orchestrator()

        # 启动 UiPath 作业
        job_key = uipath.start_job(filename)
        print(f"RPA 流程触发成功! Job Key: {job_key}")

        # 缓存 job_key，后续查询状态要用
        uipath.cache_job_key(filename, job_key)
        return job_key
    except Exception as e:
        sys.stderr.write(f"触发 RPA 流程失败: {str(e)}")
        return None


def wait_rpa_job_completion(filename):
    """
    轮询 RPA 流程状态，等待其完成
    通过获取所有作业列表然后筛选特定job_key的方式来查询状态
    """
    print(f"等待 RPA 流程完成: {filename}")

    try:
        # 获取 UiPath 实例
        uipath = get_uipath_orchestrator()

        # 轮询参数
        max_attempts = config.get_uipath_max_attempts()
        poll_interval = config.get_uipath_poll_interval()

        # 获取缓存的 job_key
        job_key = uipath.get_job_key(filename)
        if not job_key:
            sys.stderr.write(f"未找到 {filename} 对应的作业 Key")
            return False

        for attempt in range(1, max_attempts + 1):
            print(f"轮询 RPA 状态 ({attempt}/{max_attempts})...")

            try:
                job_details = uipath.get_job_details_from_all_jobs(job_key)
                if not job_details:
                    print(f"未在作业列表中找到 job_key: {job_key}")
                    time.sleep(poll_interval)
                    continue

                state = job_details.get("State", "Unknown")
                print(f"作业状态: {state}")

                if state == "Successful":
                    print("RPA 流程成功完成!")
                    return True
                elif state in ["Faulted", "Stopped"]:
                    error_info = job_details.get("Info", "无错误信息")
                    sys.stderr.write(f"RPA 流程失败! 状态: {state}, 错误信息: {error_info}")
                    return False
                else:
                    print(f"作业仍在进行中... ('{state}')")

            except Exception as e:
                sys.stderr.write(f"轮询作业状态失败: {str(e)}")

            # 等待下一次轮询
            if attempt < max_attempts:
                time.sleep(poll_interval)

        sys.stderr.write(f"RPA 流程超时! 超过最大尝试次数: {max_attempts}")
        return False
    except Exception as e:
        sys.stderr.write(f"等待 RPA 完成时发生错误: {str(e)}")
        return False