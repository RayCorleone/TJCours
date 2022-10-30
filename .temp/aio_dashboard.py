"""
 @Author    Ray
 @Coding    UTF-8
 @Version   v2.0
 @TimeStamp 2022-10-21
 @Function  批量爬取tongji.course课程的录播
 @Comment   根据/dashboard下载
"""


import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


###############################################################
## 0.参数定义
START_DATE  = '2022年10月21日'  # 开始下载日期(大)
STOP_DATE   = '2022年8月25日'   # 结束下载日期(小)
COURS_NAMES = [     # 要下载的课程名列表
    '法语精读(上)',
    # 'Python 数学建模应用实践',
    # '货币金融学',
    '大数据与人工智能',
    # '科学家们的传奇人生',
    # '临床催眠入门',
    '法语视听说(上)',
    # '深度学习'
    ]

TIME_OUT    = 1     # Timeout时间(s)
DELAY_MIN   = 0.1   # 等待时间(s)
FUNC_FLAGS  = 0     # 保留标志位(改名/下载非课表课程/...)
DLINK_FILE  = '.\\dlink.txt'            # 保存直链地址的文件路径
VNAME_FILE  = '.\\vname.txt'            # 保存视频名称和下载名称对应关系的文件路径
CHROME_PATH = '.\\chromedriver.exe'     # 谷歌模拟器的地址


###############################################################
## 0.常量和函数定义
web_url     = 'https://courses.tongji.edu.cn/dashboard'
dlink_file  = open(DLINK_FILE,'w+')
vname_file  = open(VNAME_FILE,'w+')
option      = webdriver.ChromeOptions()
option.add_argument('--log-level=3')
option.add_experimental_option('excludeSwitches',['enable-logging'])
cur_browser = webdriver.Chrome(options=option,executable_path=CHROME_PATH)

def click_elements_pro(xpath, wait=True, timeout=TIME_OUT, browser=cur_browser):
    """
     @Function: 根据xpath定位元素并点击
        a.加入元素存在判断
        b.加入强制等待机制
        c.特殊的加入timeout判断
    """

    # 0.等待加载
    time.sleep(DELAY_MIN)

    # 1.判断元素是否存在(不存在:触发ValueError)
    try:
        browser.find_element(By.XPATH,xpath)
    except:
        raise ValueError(f"No such element with xpath '{xpath}'.")

    # 2.不断点击元素
    start_time = time.time()
    is_clicked = False
    item = browser.find_element(By.XPATH,xpath)
    while is_clicked == False:
        try:
            item.click()
            is_clicked = True
        except:
            # 3.超时判断与强制等待
            if (time.time()-start_time > timeout) and (wait == False):
                print(f"  !TIMEOUT: xpath {xpath}")
                raise TimeoutError("error")
            else:
                continue
    
    # 3.延迟等待
    time.sleep(DELAY_MIN)


###############################################################
## 1.用户手动登录: 
#    用户手动输入用户名和密码, 完全进入云课堂界面后, 控制台输入Y继续
cur_browser.get(url=web_url)
while True:
    wait_for_login = input("-Login?(Y/n):")
    if wait_for_login == 'Y':
        break
    elif wait_for_login == 'n':
        cur_browser.quit()
        break


###############################################################
## 2.保存所有视频链接:
#   1) 获取源代码, 判断今天是不是等于终止下载的日期? 是的话跳到 E
#   2) 获取当前界面有多少个课程按钮, 记录个数 N, 初始化 i = 0
#   3) 判断 i == N ? 是的话跳到 9)
#   4) 定位第 i 个课程, 点击按钮
#   5) 定位播放按钮, 成功的话点击按钮, 失败的话跳到 8)
#   6) 获取视频链接, 输出到控制台/保存到txt/加入迅雷队列
#   7) 定位关闭按钮, 点击按钮
#   8) 定位关闭按钮, 点击按钮, i = i + 1, 跳到 3)
#   9) 定位上一页按钮, 点击按钮
#   E) 结束进程

cur_browser.get(url=web_url)
time.sleep(1)
confrim_btn1_xpath = '//*[@id="app"]/div/div[1]/div[2]/div/div/div'
click_elements_pro(confrim_btn1_xpath)
confrim_btn2_xpath = '//*[@id="app"]/div/div[1]/div[2]/div/div/div'
click_elements_pro(confrim_btn2_xpath)

start_flag = False
while True:
    cur_html = cur_browser.page_source
    cur_soup = BeautifulSoup(cur_html, "html.parser")
    cur_date = cur_soup.find("h2").text

    # 0) 先调整到开始日期
    if start_flag == False:
        if cur_date == START_DATE:
            start_flag = True
        else:
            last_page_btn_xpath = '//*[@id="app"]/div/div[2]/section/div/div[2]/section/div[1]/div[1]/div[1]/div/button[1]/span'
            click_elements_pro(last_page_btn_xpath)
            continue

    # 1) 获取源代码, 判断今天是不是等于终止下载的日期? 是的话退出循环
    if cur_date == STOP_DATE:
        break

    # 2) 获取当前界面有多少个课程按钮, 记录课名和个数 N
    start_time = time.time()
    while True:
        cur_courses = []
        cur_html = cur_browser.page_source
        cur_soup = BeautifulSoup(cur_html, "html.parser")

        for item in cur_soup.find_all("a"):
            i_class = item.get("class")
            if i_class and ('fc-time-grid-event' in i_class):
                cur_courses.append(item)
        cur_cours_num = len(cur_courses)

        if (cur_cours_num > 0) or (time.time()-start_time > TIME_OUT):
            break
    
    cur_courses_name = []
    for course in cur_courses:
        for item in course.find_all('div'):
            i_class = item.get("class")
            if i_class and ('fc-title' in i_class):
                course_name = item.text.split(' |')[0]
                cur_courses_name.append(course_name)
    print(f"-NOTICE: {cur_date} 共有 {cur_cours_num} 个课程")

    # 3) 循环 N 次, 获取课程链接
    for index in range(1,cur_cours_num+1):
        if (len(COURS_NAMES)!=0) and (cur_courses_name[index-1] not in COURS_NAMES):
            continue

        print(f" -searching for course {index}...")

        # 4) 定位第 i 个课程, 点击按钮
        cur_cours_btn_xpath = '//*[@id="app"]/div/div[2]/section/div/div[2]/section/div[1]/div[2]/div/table/tbody/tr/td/div/div/div[3]/table/tbody/tr/td[2]/div/div[2]/a['+str(index)+']'
        click_elements_pro(cur_cours_btn_xpath)

        # 5) 定位录像栏目, 点击按钮
        recording_tab_xpath = '//*[@id="tab-recordings"]'
        click_elements_pro(recording_tab_xpath)
        
        # 5*) 尝试点击多个播放按键, 点击成功就进入, 不成功就跳过
        v_index = 1
        while True:
            try:
                play_btn_xpath = '//*[@id="pane-recordings"]/div[2]/div[3]/table/tbody/tr['+str(v_index)+']/td[1]/div/button'
                click_elements_pro(play_btn_xpath)

                # 6) 获取视频链接, 保存到txt
                while True:
                    try:
                        cur_video_html = cur_browser.page_source
                        cur_video_soup = BeautifulSoup(cur_video_html, "html.parser")
                        cur_video_src = cur_video_soup.find("video").get('src')
                        break
                    except:
                        continue
                dlink_file.write(cur_video_src)
                dlink_file.write('\n')
                old_video_name = cur_video_src.split("/")[-1].split('?')[0]
                new_video_name = cur_courses_name[index-1]+'-'+cur_date+'-'+str(v_index)
                vname_line = old_video_name+"|"+new_video_name+"\n"
                vname_file.write(vname_line)

                # 7) 定位关闭按钮, 点击按钮
                close_btn1_xpath = '//*[@id="app"]/div/div[2]/section/div/div[2]/section/div[2]/div/div[2]/div[2]/div[1]/div/div/i'
                click_elements_pro(close_btn1_xpath)

                v_index = v_index + 1
            except ValueError:
                print(f"  -find {v_index-1} clip(s) for course {index}")
                break

        # 8) 定位关闭按钮, 点击按钮
        close_btn2_xpath = '//*[@id="app"]/div/div[2]/section/div/div[2]/section/div[2]/div/div[3]/div/button[2]'
        click_elements_pro(close_btn2_xpath)


    # 9) 定位上一页按钮, 点击按钮
    last_page_btn_xpath = '//*[@id="app"]/div/div[2]/section/div/div[2]/section/div[1]/div[1]/div[1]/div/button[1]/span'
    click_elements_pro(last_page_btn_xpath)


## E.退出程序
while True:
    wait_for_exit = input("-Exit?(Y/n):")
    if wait_for_exit == 'Y':
        cur_browser.quit()
        break
