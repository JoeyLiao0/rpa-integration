import os
import time
import openpyxl
from configLoader import config

TRIGGER_FOLDER_PATH = config.get_trigger_folder_path()
RPA_FILENAME_DICT_PATH = config.get_rpa_filename_excel_path()
RF_DICT = config.get_rpa_filename_mapping()

# read Excel file
def read_excel():
    dict = {}
    wb = openpyxl.load_workbook(RPA_FILENAME_DICT_PATH)
    sheet = wb["Sheet1"]
    for i in range(sheet.min_row + 1, sheet.max_row + 1):
        rpa = sheet.cell(i, 1).value
        filename = sheet.cell(i, 2).value
        dict[rpa] = filename
    print(dict)
    return dict

# create file trigger rpa
def create_file(filename):
    if not os.path.exists(TRIGGER_FOLDER_PATH):
        print("folder is not exist")
    open(TRIGGER_FOLDER_PATH + filename, 'w').close()
    print(f"create file -- {filename}, trigger RPA!")

# wait file delete
def wait_delete_file(filename):
    filename = TRIGGER_FOLDER_PATH + filename
    while os.path.exists(filename):
        time.sleep(10)
        print("wait RPA 10s!")
    print("finish waiting RPA!")