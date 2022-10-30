"""
 @Author    Ray
 @Coding    UTF-8
 @Version   v1.0
 @TimeStamp 2022-10-28
 @Function  重要组件对象
 @Comment   None
"""


# logger对象
from tjcours.configs import LOG_FILE, PRINT_LOG
f_log = open(LOG_FILE,'a')
def logger(log, end='\n'):
    if PRINT_LOG:
        print(log, end = end)
        
    f_log.write(log)
    f_log.write(end)
    f_log.flush()

# 数据库对象
from tjcours.mydb import Mydb
db = Mydb()

# 爬虫对象
from tjcours.crawler import Crawler
crawler = Crawler()

