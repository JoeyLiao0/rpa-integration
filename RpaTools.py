import re
from fileTools import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# get dom element
def get_element_by_id(driver, id):
    element = driver.find_element(By.ID, id)
    return element

def get_element_by_name(driver, name):
    element = driver.find_element(By.NAME, name)
    return element

def get_element_by_tag(driver, tag):
    element = driver.find_element(By.TAG_NAME, tag)
    return element

def get_element_by_class(driver, classname):
    element = driver.find_element(By.CLASS_NAME, classname)
    return element

# get dom element(s)
def get_elements_by_tag(driver, tag):
    elements = driver.find_elements(By.TAG_NAME, tag)
    return elements

def get_elements_by_class(driver, classname):
    elements = driver.find_elements(By.CLASS_NAME, classname)
    return elements

# get element attribute
def get_element_attribute(element, attribute):
    value = element.get_attribute(attribute)
    return value

# switch page
def switch_page(driver, index):
    menu_ul = get_element_by_class(driver, "cds--header__menu-bar")
    items_li = menu_ul.find_element(By.TAG_NAME, "li")
    if index >= 2:
        return
    
    target_item = items_li[index]
    target_item.click()
    pass

# open Chrome Page
def open_chrome_page(url):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)

    # need ChromeDriver
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    driver.maximize_window()
    return driver

# login
def login(driver, username, password):
    username_input = get_element_by_name(driver, "username")
    password_input = get_element_by_name(driver, "password")
    buttons = get_elements_by_tag(driver, "button")

    username_input.send_keys(username)
    password_input.send_keys(password)
    for button in buttons:
        # print(getElementAttribute(button, "type"))
        if get_element_attribute(button, "type") == "submit":
            button.click()
            break

# check work item
def check_work_item(driver):
    res = True
    try:
        get_element_by_class(driver, "_listContainer_9v2bx_37")
    except:
        res = False
    return res

# click work item
def click_work_item(driver):
    work_item_element = get_element_by_class(driver, "_container_u7el0_69")
    work_item_element.click()

# get work item data
def get_work_item_data(driver):
    res = {}
    res["taskName"] = get_taskname(driver)
    print(f"taskName is -- {res['taskName']}")
    return res

def get_taskname(driver):
    taskname_span = get_element_by_class(driver, "_taskName_1ewzh_31")
    return taskname_span.text

# trigger RPA
def trigger_rpa(data):
    taskname = data["taskName"]
    filename = RF_DICT[taskname]
    create_file(filename)
    wait_delete_file(filename)

# finish work item
def finish_work_item(driver):
    buttons = get_elements_by_tag(driver, "button")
    for button in buttons:
        # print(getElementAttribute(button, "type"))
        if get_element_attribute(button, "type") == "submit":
            button.click()
            break
    # wait loading complete
    loading_label = get_element_by_class(driver, "cds--inline-loading")
    WebDriverWait(driver, 20, 0.5).until(EC.staleness_of(loading_label))
    print("finish button click!")

# superman
def match_taskname(taskname):
    pattern = re.compile(r'RPA_([a-zA-Z0-9]+)_([a-zA-Z0-9]+)')
    return re.fullmatch(pattern, taskname) != None

def start_IBP(driver, pname):
    # switch Process page
    switch_page(driver, 1)
    time.sleep(1)

    divs = get_elements_by_class(driver, "_content_1ucz1_15")
    for div_element in divs:
        h4_element = div_element.find_element(By.CLASS_NAME, "_title_1ucz1_19")
        text = h4_element.text.strip()
        if text == pname:
            button = div_element.find_element(By.CLASS_NAME, "_button_15o7q_12")
            button.click()
            print(f"IBP -- {pname} start!")
            break
    
    time.sleep(2)
    # switch Tasklist page
    switch_page(driver, 0)
    time.sleep(1)

def validate_work_item(driver, dict, superman_items):
    res = False
    if check_work_item(driver):
        spans = get_elements_by_class(driver, "_name_u7el0_27")
        for span in spans:
            taskname = span.text

            if taskname in superman_items:
                start_IBP(driver, superman_items[taskname])
                continue

            if match_taskname(taskname) and taskname not in dict:
                res = True
                dict[taskname] = (span, 0)
                print(f"Check in work item {taskname}")
    return res

def get_work_item_data_superman(driver, taskname):
    res = {}
    name_list = taskname.split('_')
    res["userName"] = name_list[1]
    res["taskName"] = name_list[2]
    return res
