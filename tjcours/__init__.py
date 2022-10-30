"""
 @Author    Ray
 @Coding    UTF-8
 @Version   v1.0
 @TimeStamp 2022-10-28
 @Function  打包tjcours
 @Comment   None
"""

from datetime import datetime

from tjcours.configs import *
from tjcours.extention import *


def get_info():
    
    # 0.设置默认值
    info_dic = {
        'start_date': crawler.start_date,
        'stop_date' : crawler.stop_date,
        'cours_list': []
    }

    # 0.获取页面展示的课程信息
    exist_cours_list = crawler.refresh_course()

    # 1.选择爬取模式
    mode = input("$USER: mode? (1-dash,2-myclct,3-new,x-exit):")
    if mode == '1':
        mode = 'dashboard'
    elif mode == '2':
        mode = 'mycollection'
    elif mode == '3':
        mode = 'newcours'
    else:
        mode = 'exit'
        return mode, info_dic
    
    # 2.获取选择的课程
    chosed_cours = [    # 填写选择的课程名
        # '战略管理'
    ]
    info_dic['cours_list'] = chosed_cours

    return mode, info_dic


def create_app():
    logger(f"\n% NEW ROUND START AT {datetime.now()} %")

    # 1.变量初始化
    cur_state = STATE_IDLE

    # 2.循环执行状态机
    while True:
        logger(f'-NEWSTATE: time {datetime.now()}, current state: {cur_state}')

        if cur_state == STATE_IDLE:         # 1)等待跳转
            cur_state = crawler.idle_handeler()

        elif cur_state == STATE_LOGIN:      # 2)用户登录
            cur_state = crawler.login_handeler()
            
        elif cur_state == STATE_INFO:       # 3)获取数据
            mode, info = get_info()
            cur_state =crawler.info_handeler(mode, info)

        elif cur_state == STATE_DASH:       # 4-1)爬取dashboard
            cur_state = crawler.dash_handeler()

        elif cur_state == STATE_MYCLCT:     # 4-2)爬取mycollection
            cur_state = crawler.myclct_handeler()

        elif cur_state == STATE_NEWCOURS:   # 4-3)爬取newcours
            cur_state = crawler.newcours_handeler()

        elif cur_state == STATE_EXIT:       # E)退出程序
            crawler.exit_handeler()
            break

        else:   # F)非法状态, 核心错误, 退出程序
            logger(f'!ERROR: state {cur_state} does not exist!')
            crawler.exit_handeler()
            break
    
    # 3.结束提示
    logger("@Author: Ray Corleone")
    logger("@Github: https://github.com/RayCorleone")
    