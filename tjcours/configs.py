"""
 @Author    Ray
 @Coding    UTF-8
 @Version   v0.0
 @TimeStamp 2022-10-29
 @Function  参数文件
 @Comment   None
"""

from datetime import date

# 1.路径常量
LOG_FILE        = '.\\file\\log.txt'        # 保存运行log记录
DLINK_FILE      = '.\\file\\i_link.txt'      # 保存直链地址的文件路径
VNAME_FILE      = '.\\file\\i_name.txt'      # 保存视频名称和下载名称对应关系的文件路径
CHROME_PATH     = '.\\chromedriver.exe'     # 谷歌模拟器的路径
DATABASE_PATH   = 'sqlite:///.\\data.db?check_same_thread=False'    # 数据库设置

COURSE_URL      = 'https://courses.tongji.edu.cn'
LOGIN_URL       = 'https://courses.tongji.edu.cn/sign-in'
DASHBOARD_URL   = 'https://courses.tongji.edu.cn/dashboard'
COLLECTION_URL  = 'https://courses.tongji.edu.cn/collection'


# 2.状态常量:(IDLE->登录/输入->四个状态->IDLE)
STATE_IDLE      = 'idle'        # 判断等待
STATE_LOGIN     = 'login'       # 登录
STATE_INFO      = 'getinfo'     # 输入提取内容
STATE_DASH      = 'dashboard'   # 爬取dashboard
STATE_MYCLCT    = 'collection'  # 爬取collection(已收藏)
STATE_NEWCOURS  = 'newcourse'   # 爬取collection(未收藏)
STATE_EXIT      = 'exit'        # 关闭模拟器

# 3.时间常量
TIME_OUT    = 1     # Timeout时间(s)
DELAY_MIN   = 0.12  # 等待时间(s)
PAGE_FGAP   = 0.1   # 多次源码的间隔时间(s)
LOAD_TIME   = 0.5   # 网络加载时间(s)
START_DATE  = date(2022,8,29)   # 课程起始时间

# 4.其他常量
BUFFER_SIZE = 10    # 读写缓存区大小
STABLE_MIN  = 2     # 页面源码稳定的最小次数(总时间:STABLE_MIN*PAGE_FGAP)
FSIZE_MIN   = 20    # 文件最小大小(MB)
PRINT_LOG   = True  # 是否在命令行输出log