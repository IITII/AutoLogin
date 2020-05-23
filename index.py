#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
import getopt
import platform
# 防止编码问题
reload(sys)
sys.setdefaultencoding("utf-8")


SLEEP_TIME = 1
NO_GUI = True


def show_help():
    print(
        'Usage:\n'
        + 'py ' + sys.argv[0] + ' -u <username> -p <password>\n'
        + 'py ' + __file__ + ' --username=<username> --password=<password>\n'
    )


def get_exec_path():
    chrome_version = '83'
    base_path = './drivers/chrome/' + chrome_version + '/'
    path = ''
    os = platform.system()
    if os == 'Windows':
        path = base_path + 'win.exe'
    elif os == 'Linux':
        path = base_path + 'linux'
    elif os == 'Darwin':
        path = base_path + 'mac'
    else:
        print('Unknown System OS...')
        sys.exit(1)
    return path


def get_user_info(argv):
    user_info = []
    try:
        opts, args = getopt.getopt(
            argv, "hu:p:g", ["username=", "password=", "gui"])
    except getopt.GetoptError:
        print('Usage:\n' + sys.argv[0] + '-u <username> -p <password>')
        sys.exit(1)
    for opt, arg in opts:
        if opt == '-h':
            show_help()
            sys.exit(1)
        elif opt in ("-u", "--username"):
            user_info.append(arg)
        elif opt in ("-p", "--password"):
            user_info.append(arg)
        elif opt in ("-g", "--gui"):
            global NO_GUI
            NO_GUI = False
    if len(user_info) != 2:
        show_help()
        sys.exit(1)
    else:
        return user_info


def get_driver():
    global NO_GUI
    # Chrome options
    op = webdriver.ChromeOptions()
    # 关掉浏览器左上角的通知提示
    op.add_argument("--disable-notifications")
    # 关闭'chrome正受到自动测试软件的控制'提示
    # op.add_argument("disable-infobars")
    # See: https://stackoverflow.com/questions/57298901/unable-to-hide-chrome-is-being-controlled-by-automated-software-infobar-within
    if NO_GUI:
        op.add_argument('headless')
    driver = webdriver.Chrome(executable_path=get_exec_path(), options=op)
    return driver


def login_state(driver, login_type):
    tmp = driver.find_elements_by_tag_name('ul')
    if login_type == 1:
        # 判断登录是否出错
        if tmp[0].text.find('错误') != -1:
            if len(tmp) > 1:
                print(tmp[1].text)
            return True
        return False
    elif login_type == 2:
        if tmp[0].text.find('成功') != -1:
            print(tmp[0].text)
            return False
        else:
            for m in tmp:
                for n in m.text.split('\n'):
                    if n.find('成功') != -1 or n.find('错误') != -1:
                        print(n)
            return True
    return False


def login(driver, user_info):
    # 用户名
    # 显式等待
    try:
        username = WebDriverWait(driver, 5, 0.5).until(
            EC.presence_of_element_located((By.ID, "txtuser"))
        )
        username.clear()
        username.send_keys(user_info[0])
    except TimeoutError:
        print('超时...')
        driver.quit()
        sys.exit(1)
    # 密码
    # 隐式等待
    driver.implicitly_wait(10)
    try:
        password = driver.find_element_by_id('txtPwd')
        password.clear()
        password.send_keys(user_info[1])
    except NoSuchElementException as e:
        driver.quit()
        sys.exit(1)
    # 用户类型
    select = Select(driver.find_element_by_id('userType'))
    select.select_by_visible_text('学生用户')
    # 登录
    driver.find_elements_by_tag_name('a')[3].click()


def main():
    user_info = get_user_info(sys.argv[1:])
    base_url = 'http://10.1.88.4'
    driver = get_driver()
    driver.get(base_url)
    login(driver, user_info)
    while login_state(driver, 2):
        print('登录貌似失败了...')
        time.sleep(6)
        while login_state(driver, 1):
            print('有点问题, 等一下, 很快的...')
            time.sleep(6)
            login(driver, user_info)
    print('登录成功')
    driver.quit()


if __name__ == '__main__':
    main()
