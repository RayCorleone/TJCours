"""
 @Author    Ray
 @Coding    UTF-8
 @Version   v2.0
 @TimeStamp 2022-10-23
 @Function  批量爬取tongji.course课程的录播
 @Comment   根据/collection下载
            1)看看能不能锁定模拟器不被点击
            2)添加数据库文件, 避免重复爬取, 可以累积爬取(P.S.直链会失效)
            3)相同的文件名可能有多个不同直链：根据 大小-日期-course_id区别
"""

from random import randint
import time
from bs4 import BeautifulSoup
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from tjcours.configs import *
from tjcours.extention import db, logger
from tjcours.model import Teacher,Course,TeacherToCourse,Video


class Crawler:

    def __init__(self):
        """
         @ INIT 启动模拟器, 初始化变量
        """
        option = webdriver.ChromeOptions()
        option.add_argument('--log-level=3')
        option.add_experimental_option('excludeSwitches',['enable-logging'])

        # 模拟器
        self.chrome = webdriver.Chrome(options=option,executable_path=CHROME_PATH)
        self.mouse = ActionChains(self.chrome)
        # 保存链接文件
        self.dlink_file = open(DLINK_FILE,'w+',buffering=BUFFER_SIZE)
        # 保存名字文件
        self.vname_file = open(VNAME_FILE,'w+',buffering=BUFFER_SIZE)
        # 爬取-URL(默认Dashboard)
        self.crawl_url = DASHBOARD_URL
        # 爬取-开始日期(默认2022-08-29)
        self.start_date = START_DATE
        # 爬取-结束日期(默认当天日期)
        self.stop_date = date.today()
        # 爬取-课程列表(默认空)
        self.cours_list = []
        # 爬取-视频最小大小(MB为单位, 默认20)
        self.fsize_min = FSIZE_MIN


    def visit_site(self, url):
        """
         @ FUNC 访问指定URL地址
        """
        self.chrome.get(url = url)
        time.sleep(LOAD_TIME)


    def get_chrome_url(self):
        """
         @ FUNC 获取当前页面URL地址
        """
        return self.chrome.current_url


    def get_page_source(self):
        """
         @ FUNC 获取页面源代码
            a.加入稳定计数, 避免页面未完全刷新导致出错
        """
        stable_cnt = 0
        page_source = ''
        while True:
            time.sleep(PAGE_FGAP)
            cur_page_source = self.chrome.page_source
            if page_source != cur_page_source:
                page_source = cur_page_source
                stable_cnt = 0
            else:
                stable_cnt = stable_cnt + 1
                if stable_cnt > STABLE_MIN:
                    break
        return page_source


    def click_elements_pro(self, xpath, wait=True, timeout=TIME_OUT):
        """
         @ FUNC 根据xpath定位元素并点击
            a.加入元素存在判断
            b.加入强制等待机制
            c.特殊的加入timeout判断
            d.加入鼠标移动模拟
        """

        # 0.等待加载
        time.sleep(DELAY_MIN)

        # 1.判断元素是否存在(不存在:触发ValueError)
        try:
            self.chrome.find_element(By.XPATH,xpath)
        except:
            raise ValueError(f"!ValueERROR: No such element with xpath '{xpath}'.")

        # 2.不断点击元素
        start_time = time.time()
        is_clicked = False
        item = self.chrome.find_element(By.XPATH, xpath)
        while is_clicked == False:
            try:
                try:    #模拟移动鼠标(部分元素需要动鼠标才出现)
                    self.mouse.move_by_offset(randint(-20,20),randint(-20,20))
                    self.mouse.perform()
                except:
                    pass
                item.click()
                is_clicked = True
            except:
                # 3.超时判断与强制等待
                if (time.time()-start_time > timeout) and (wait == False):
                    raise TimeoutError(f"!TimeoutERROR: xpath {xpath} timeout.")
                else:
                    continue
        
        # 3.延迟等待
        time.sleep(DELAY_MIN)


    # TODO 根据界面->返回界面课程信息列表
    def refresh_course(self):
        """
         @ FUNC 获取当前界面的课程列表
        """

        return []


    def exit_handeler(self):
        """
         @ STATE 退出程序
        """
        self.chrome.quit()
        self.dlink_file.close()
        self.vname_file.close()


    def idle_handeler(self):
        """
         @ STATE 根据登录状态确定下一个状态(INFO/LOGIN)
        """
        # 跳转至默认界面
        self.visit_site(COURSE_URL)

        # 判断是否已登录
        if self.get_chrome_url() == LOGIN_URL:
            return STATE_LOGIN
        else:
            return STATE_INFO


    def login_handeler(self):
        """
         @ STATE 手动登录账号, 确认登录后跳至IDLE
        """
        # 1.访问网站
        self.visit_site(LOGIN_URL)
        
        # 2.用户登录
        waiting = input("$USER: Login? (press Enter to continue)...")

        return STATE_IDLE


    def info_handeler(self, mode, info):
        """
         @ STATE 输入数据, 访问成功后跳至下一状态(DASH/MYCLCT/NEWCOURS/EXIT)
        """
        # 1.记录数据
        self.start_date = info['start_date']
        self.stop_date  = info['stop_date']
        self.cours_list = info['cours_list']
        
        # 2.根据模式确认跳转状态
        next_state = STATE_IDLE
        if mode == 'dashboard':
            self.crawl_url = DASHBOARD_URL
            next_state = STATE_DASH
        elif mode == 'mycollection':
            self.crawl_url = COLLECTION_URL
            next_state = STATE_MYCLCT
        elif mode == 'newcours':
            self.crawl_url = COLLECTION_URL
            next_state = STATE_NEWCOURS
        elif mode == 'exit':
            return STATE_EXIT
        
        # 3.访问爬取页面
        self.visit_site(self.crawl_url)
        if self.get_chrome_url() == self.crawl_url:
            # 点击弹窗
            click_cnt = 0
            for i in range(9,0,-1):
                try:
                    confrim_btn_xpath = '/html/body/div['+str(i)+']/div/div[3]/span/button'
                    self.click_elements_pro(confrim_btn_xpath,wait=False)
                    click_cnt = click_cnt + 1
                except ValueError:
                    continue
            if click_cnt < 2:
                input(f"$USER: Close PopupWindows? (press Enter to continue)...")

            # 返回状态
            return next_state
        else:
            return STATE_IDLE   # 访问失败


    def dash_handeler(self):
        """
         @ STATE 根据dashboard下载课程视频
            1) 获取源代码, 判断今天是不是等于终止下载的日期? 是的话跳到 E
            2) 获取当前界面有多少个课程按钮, 记录个数 N, 初始化 i = 0
            3) 判断 i == N ? 是的话跳到 9)
            4) 定位第 i 个课程, 点击按钮
            5) 定位播放按钮, 成功的话点击按钮, 失败的话跳到 8)
            6) 获取视频链接, 输出到控制台/保存到txt/加入迅雷队列
            7) 定位关闭按钮, 点击按钮
            8) 定位关闭按钮, 点击按钮, i = i + 1, 跳到 3)
            9) 定位上一页按钮, 点击按钮
            E) 结束进程
        """
        
        total_cnt = 0
        while True:
            cur_html = self.get_page_source()
            cur_soup = BeautifulSoup(cur_html, "html.parser")
            cur_date_str = cur_soup.find("h2").text.replace('年','-').replace('月','-').replace('日','-')
            cur_year  = int(cur_date_str.split('-')[0])
            cur_month = int(cur_date_str.split('-')[1])
            cur_day   = int(cur_date_str.split('-')[2])
            cur_date  = date(cur_year,cur_month,cur_day)

            # 0.页面日期>结束日期: 点击上一页
            if cur_date > self.stop_date:
                last_page_btn_xpath = '//*[@id="app"]/div/div[2]/section/div/div[2]/section/div[1]/div[1]/div[1]/div/button[1]/span'
                self.click_elements_pro(last_page_btn_xpath)
                continue

            # 0.页面日期<开始日期: 结束爬取
            if cur_date < self.start_date:
                logger(f" -total number of fetched videos: {total_cnt}")
                break

            # 1.获取当前界面有多少个课程按钮, 记录课名和个数N
            start_time = time.time()
            while True:
                cur_courses = []
                cur_html = self.get_page_source()
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
            logger(f" -{cur_date.isoformat()} has {cur_cours_num} courses, ",end='')

            # 2.循环N次, 获取课程链接
            clips_cnt = 0
            for index in range(1,cur_cours_num+1):
                if (len(self.cours_list)!=0) and (cur_courses_name[index-1] not in self.cours_list):
                    continue

                # a.定位第i个课程, 点击按钮
                cur_cours_btn_xpath = '//*[@id="app"]/div/div[2]/section/div/div[2]/section/div[1]/div[2]/div/table/tbody/tr/td/div/div/div[3]/table/tbody/tr/td[2]/div/div[2]/a['+str(index)+']'
                self.click_elements_pro(cur_cours_btn_xpath)

                # b.定位录像栏目, 点击按钮
                recording_tab_xpath = '//*[@id="tab-recordings"]'
                self.click_elements_pro(recording_tab_xpath)
                
                # c.尝试点击多个播放按键, 点击成功就进入, 不成功就跳过
                v_index = 1
                while True:
                    try:
                        play_btn_xpath = '//*[@id="pane-recordings"]/div[2]/div[3]/table/tbody/tr['+str(v_index)+']/td[1]/div/button'
                        self.click_elements_pro(play_btn_xpath)

                        # d-1.获取视频链接, 保存到txt
                        while True:
                            try:
                                cur_video_html = self.get_page_source()
                                cur_video_soup = BeautifulSoup(cur_video_html, "html.parser")
                                cur_video_src = cur_video_soup.find("video").get('src')
                                break
                            except:
                                continue
                        self.dlink_file.write(cur_video_src)
                        self.dlink_file.write('\n')
                        old_video_name = cur_video_src.split("/")[-1].split('?')[0]
                        new_video_name = cur_courses_name[index-1]+'_'+cur_date.isoformat()+'_'+str(v_index)
                        vname_line = old_video_name+"|"+new_video_name+"\n"
                        self.vname_file.write(vname_line)

                        # d-2.定位关闭按钮, 点击按钮
                        close_btn1_xpath = '//*[@id="app"]/div/div[2]/section/div/div[2]/section/div[2]/div/div[2]/div[2]/div[1]/div/div/i'
                        self.click_elements_pro(close_btn1_xpath)

                        v_index = v_index + 1
                        clips_cnt = clips_cnt + 1

                    except ValueError:
                        break

                # e.定位关闭按钮, 点击按钮
                close_btn2_xpath = '//*[@id="app"]/div/div[2]/section/div/div[2]/section/div[2]/div/div[3]/div/button[2]'
                self.click_elements_pro(close_btn2_xpath)
            logger(f"{clips_cnt} clips downloaded")

            # 3.定位上一页按钮, 点击按钮
            last_page_btn_xpath = '//*[@id="app"]/div/div[2]/section/div/div[2]/section/div[1]/div[1]/div[1]/div/button[1]/span'
            self.click_elements_pro(last_page_btn_xpath)

        return STATE_IDLE


    def myclct_handeler(self):
        """
         @ STATE 根据collection下载收藏的课程视频
            0) 定位第一页位置, 点击按钮至第一页
            1) while is_next_page:
                A.读取源代码, 获得页面有n个课程, 判断是否有下一页(is_next_page)
                B.for循环n次:
                    a.定位i课程播放键, 并点击
                    b.读取源代码, 获得页面有m个视频, 按序记录视频是否下载(根据时间判断)
                    c.依次点击要下载的m'个播放按键, 点击成功就进入, 不成功就跳过
                        d-1.获取视频链接, 保存到txt
                        d-2.定位关闭按钮, 点击按钮
                    e.定位关闭按钮, 点击按钮
                C.有下一页的话, 点击下一页按键
        """
        
        # 定位第一页位置, 点击按钮至第一页
        first_page_xpath = '//*[@id="app"]/div/div[2]/section/div/div[2]/section/section/div[3]/div[2]/div/ul/li[1]'
        self.click_elements_pro(first_page_xpath)

        # While循环
        cur_courses = []        # 当页课程item
        cur_courses_num = 0     # 当页课程数量
        cur_courses_info = []   # 当页课程信息字典表
        is_next_page = True # 是否有下一页
        while is_next_page:
            # 0-1.数据清空
            cur_courses.clear()
            cur_courses_num = 0
            cur_courses_info.clear()
            cur_html = ''

            # 0-2.获取soup
            cur_html = self.get_page_source()
            cur_soup = BeautifulSoup(cur_html, "html.parser")
            
            # 1-1.判断是否有下一页
            for item in cur_soup.find_all("button"):
                i_class = item.get("class")
                if i_class and ('btn-next' in i_class) and (item.get("disabled")=='disabled'):
                    is_next_page = False

            # 1-2.获得页面有n个课程
            start_time = time.time()
            while True:
                cours_table = cur_soup.find("div",class_='el-table__body-wrapper')
                for item in cours_table.find_all('tr',class_='el-table__row'):
                    cur_courses.append(item)
                cur_courses_num = len(cur_courses)

                if (cur_courses_num > 0) or (time.time()-start_time > TIME_OUT):
                    logger(f" -PAGE: current page has {cur_courses_num} courses.")
                    # for course in cur_courses:
                    #     print(course.find('td', class_='el-table_1_column_3').find('b').text)
                    # a = input('$USER: check?(press Enter to continue...)')
                    break

            # 1-3.获得课程的基本信息
            for course in cur_courses:
                # a.保存课名/课号
                item = course.find('td', class_='el-table_1_column_3')
                c_num = item.find('b').text
                c_name = str(item).split('<br/>')[-1].replace('</div>','').replace('</td>','')
                cur_courses_info.append({'name':c_name, 'number':c_num})
                
                # b.修改数据库(课程/老师/对应表)
                if db.query(Course).filter_by(number=c_num).first() is None:
                    db_course = Course(number=c_num, name=c_name, term=1, department=course.find('td', class_='el-table_1_column_5').text)
                    db.session.add(db_course)             

                t_nums = course.find('td',class_='el-table_1_column_4').find('b').text.split(',')
                t_names = str(course.find('td',class_='el-table_1_column_4')).split('<br/>')[-1].replace('</div>','').replace('</td>','').split(',')
                for i in range(0,len(t_nums)):
                    if db.query(Teacher).filter_by(number=t_nums[i]).first() is None:
                        db_teacher = Teacher(number=t_nums[i],name=t_names[i])
                        db.session.add(db_teacher)

                for t_num in t_nums:
                    t_id = db.query(Teacher).filter_by(number=t_num).first().id
                    c_id = db.query(Course).filter_by(number=c_num).first().id
                    db_ttc = TeacherToCourse(course_id=c_id, teacher_id=t_id)
                    if db_ttc.not_exist():
                        db.session.add(db_ttc)
                db.session.commit()

            # 2.循环n次, 分别获取课程的视频链接
            for index in range(1,cur_courses_num + 1):
                if (len(self.cours_list)!=0) and (cur_courses_info[index-1]['name'] not in self.cours_list):
                    continue

                course_id = db.query(Course).filter_by(number=cur_courses_info[index-1]['number']).first().id
                course_name = cur_courses_info[index-1]['name']
                course_number = cur_courses_info[index-1]['number']

                # a.定位i课程播放键, 点击按钮
                cur_cours_btn_xpath = ' //*[@id="app"]/div/div[2]/section/div/div[2]/section/section/div[2]/div[3]/table/tbody/tr['+str(index)+']/td[8]/div/button[2]'
                self.click_elements_pro(cur_cours_btn_xpath)

                # b-1.读取源代码, 获得页面m个视频信息
                cur_html = self.get_page_source()
                cur_soup = BeautifulSoup(cur_html, "html.parser")
                cur_clips_list = cur_soup.find_all('td',class_='el-table_2_column_9')
                cur_clips_size = cur_soup.find_all('td',class_='el-table_2_column_11')
                cur_clips_num = len(cur_clips_list)
                db_clips_num = db.query(Video).filter_by(course_id=course_id,expired=False).count()
                logger(f" -{course_number} {course_name} has {cur_clips_num} clips({db_clips_num} in DB), ",end='')

                # b-2.判断数据库中是否已经存完课程数据
                if cur_clips_num == db_clips_num:
                    logger(f"done.")
                    close_btn2_xpath = '//*[@id="app"]/div/div[2]/section/div/div[2]/section/div[2]/div/div[3]/div/button'
                    self.click_elements_pro(close_btn2_xpath)
                    continue
                elif db_clips_num > cur_clips_num:
                    logger(f"not possible.")
                    close_btn2_xpath = '//*[@id="app"]/div/div[2]/section/div/div[2]/section/div[2]/div/div[3]/div/button'
                    self.click_elements_pro(close_btn2_xpath)
                    continue

                # b-3.按序记录视频信息(之后根据时间/大小判断是否下载)
                cur_clips_info = []
                for i in range(0, cur_clips_num):
                    t_date = cur_clips_list[i].text.split(' ')[0].split('-')
                    cur_date = date(int(t_date[0]),int(t_date[1]),int(t_date[2]))
                    cur_size = int(cur_clips_size[i].text.replace('B','').replace('M','000000').replace('K','000').replace('G','000000000'))/1000000
                    cur_clips_info.append({'date':cur_date,'size':cur_size})
                                    
                # c.依次点击要下载的m'个播放按键, 点击成功就进入, 不成功就跳过
                clips_downloaded_cnt = 0
                session_list = []
                for v_index in range(1, cur_clips_num + 1):
                    # x.不在指定日期内无需下载
                    cur_date = cur_clips_info[v_index-1]['date']
                    if (cur_date < self.start_date) or (cur_date > self.stop_date):
                        continue

                    # x.文件大小不符合要求的无需下载
                    cur_size = cur_clips_info[v_index-1]['size']
                    if (cur_size < self.fsize_min):
                        continue

                    # x.在数据库中有记录(已下载)的无需下载
                    if db.query(Video).filter_by(course_id=course_id,v_date=cur_date,size=cur_size,downloaded=True).first() is not None:
                        continue
                    
                    # x.在数据库中有记录(未过期)的无需下载
                    if db.query(Video).filter_by(course_id=course_id,v_date=cur_date,size=cur_size,expired=False).first() is not None:
                        continue
                    
                    # 尝试点击播放按钮, 失败则跳过
                    try:
                        play_btn_xpath = '  //*[@id="app"]/div/div[2]/section/div/div[2]/section/div[2]/div/div[2]/div/div/div[3]/table/tbody/tr['+str(v_index)+']/td[4]/div/button'
                        self.click_elements_pro(play_btn_xpath)
                    except ValueError:
                        continue

                    # d-1.获取视频链接
                    while True:
                        try:
                            cur_video_html = self.get_page_source()
                            cur_video_soup = BeautifulSoup(cur_video_html, "html.parser")
                            cur_video_src = cur_video_soup.find("video").get('src')
                            break
                        except:
                            continue

                    # d-2.更新数据库(只add不commit)
                    dump_into_txt = False
                    old_name = cur_video_src.split("/")[-1].split('?')[0].replace('.mp4','')
                    new_name = course_number+'-'+course_name+'_'+cur_date.isoformat()   #+'_'+str(v_index)+'.mp4'
                    db_video = Video(v_date=cur_date, size=cur_size, old_name=old_name, new_name=new_name, dirc_link=cur_video_src,course_id=course_id)
                    if db_video.can_update():
                        # db.session.add(db_video)
                        session_list.append(db_video)
                        dump_into_txt = True

                    # d-3.把新获取的链接保存到txt(便于下载)
                    if dump_into_txt == True:
                        self.dlink_file.write(cur_video_src)
                        self.dlink_file.write('\n')
                        vname_line = old_name+"|"+new_name+"\n"
                        self.vname_file.write(vname_line)

                    # d-4.定位关闭按钮, 点击按钮
                    close_btn1_xpath = '//*[@id="app"]/div/div[2]/section/div/div[2]/section/div[2]/div/div[2]/div[2]/div[1]/div/div/i'
                    self.click_elements_pro(close_btn1_xpath)

                    v_index = v_index + 1
                    clips_downloaded_cnt = clips_downloaded_cnt + 1
                
                # P.S.一门课所有视频都爬完再commit
                db.session.add_all(session_list)
                db.session.commit()

                # e.定位关闭按钮, 点击按钮
                close_btn2_xpath = '//*[@id="app"]/div/div[2]/section/div/div[2]/section/div[2]/div/div[3]/div/button'
                self.click_elements_pro(close_btn2_xpath)
                logger(f"{clips_downloaded_cnt} clips newly downloaded")

            # 3.定位下一页按钮, 点击按钮
            if is_next_page:
                next_page_btn_xpath = ' //*[@id="app"]/div/div[2]/section/div/div[2]/section/section/div[3]/div[2]/div/button[2]'
                self.click_elements_pro(next_page_btn_xpath)

        return STATE_IDLE
    

    def newcours_handeler(self):
        """
         @ STATE 根据collection下载课程视频(未收藏)
        """

        logger(' -still developing...')

        return STATE_IDLE
