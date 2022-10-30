"""
 @Author    Ray
 @Coding    UTF-8
 @Version   v0.0
 @TimeStamp 2022-10-28
 @Function  数据库管理工具
 @Comment   1)更新过期链接
            2)批量导出链接和重命名文件
            3)数据库的重置与建立
            4)过滤错误数据
"""

import os

from tjcours.extention import db
from tjcours.model import *

DB_LINK_FILE    = '.\\file\\db_link.txt'    # 保存直链地址的文件路径
DB_NAME_FILE    = '.\\file\\db_name.txt'    # 保存视频名称和下载名称对应关系的文件路径

# 数据库重置后重新建立
def db_reset():
    # db.drop_all()
    # db.create_all()
    pass

# 清理无效video数据
def db_clear():
    course_cnt = db.query(Course).count()
    for i in range(1, course_cnt + 1):
        # 0.课程对应的视频表
        c_videos = db.query(Course).filter_by(id=i).first().videos
        # 1.数据初始化
        is_diff = False
        if len(c_videos) != 0:
            pre_meeting = c_videos[0].old_name.split('-')[2]
            now_meeting = ''
        # 2.逐个筛选
        for video in c_videos:
            now_meeting = video.old_name.split('-')[2]
            if now_meeting != pre_meeting:
                is_diff = True
                break
        # 3.有不同的:删除课程所有视频
        if is_diff:
            print(f'-course {i} is impossible, ',end='')
            d_cnt = 0
            for video in c_videos:
                d_video = db.query(Video).filter_by(id=video.id).first()
                if d_video is not None:
                    db.session.delete(d_video)
                    d_cnt += 1
            db.session.commit()
            print(f'{d_cnt} videos deleted.')

# 批量添加ccolumn数据
def db_change_column():
    videos = db.query(Video).all()
    cnt=0
    for video in videos:
        if cnt%20==0:
            print(f'-{cnt} videos changed.')
            db.session.commit()
        video.expired = True
        cnt += 1
    db.session.commit()

# 批量导出URL和Name_list
def db_dumpfile():
    # 保存链接文件
    link_file = open(DB_LINK_FILE,'w+')
    # 保存名字文件
    name_file = open(DB_NAME_FILE,'a')
    
    videos = db.query(Video).all()
    dump_cnt = 0
    for video in videos:
        if dump_cnt % 20 == 0:
            print(f"-{dump_cnt} links dumped.")
            db.session.commit()
        if video.downloaded == False:
            link_file.write(video.dirc_link)
            link_file.write('\n')
            name_line = video.old_name+"|"+video.new_name+"\n"
            name_file.write(name_line)
            video.dumped = True
            dump_cnt += 1
    db.session.commit()
    link_file.close()
    name_file.close()

# 标记已经下载的视频
def db_mark_downloaded():

    folder_path = 'E:\\video\\temp'
    folder = os.listdir(folder_path)
    cnt = 0
    for video in folder:
        if cnt % 20 == 0:
            print(f"-{cnt} video marked.")
            db.session.commit()
        db_video = db.query(Video).filter_by(old_name=video).first()
        if db_video is not None:
            db_video.downloaded = True
            cnt = cnt + 1
    db.session.commit()    

# 修改影片名字
def db_rename():

    ## 1.读取db_name.txt文件
    name_file = open(DB_NAME_FILE,'r')
    name_dic = {}
    for line in name_file.readlines():
        name = line.split('|')
        name_dic[name[0]] = name[1].replace('\n','')


    ## 2.替换文件名
    folder_path = 'E:\\video'
    folder = os.listdir(folder_path)

    for video in folder:
        if video in name_dic.keys():
            old_path = os.path.join(folder_path, video)
            new_path = os.path.join(folder_path, name_dic[video])
            os.rename(old_path,new_path)
            print(f'-{video} renamed as {name_dic[video]}')
        else:
            print(f'-{video} not exist in {DB_NAME_FILE}')

# 修改影片名字2
def db_rename2():

    ## 1.读取db_name.txt文件
    name_file = open(DB_NAME_FILE,'r')
    name_dic = {}
    for line in name_file.readlines():
        name = line.split('|')
        old_n = name[0].replace('.mp4','')
        new_n = name[1].replace('\n','').replace('.mp4','')
        name_dic[old_n] = new_n
    # print(name_dic)


    ## 2.替换文件名
    folder_path = 'E:\\video\\temp'
    folder = os.listdir(folder_path)

    for video in folder:
        pre_name = video.split('(')[0].replace(' ','').replace('.mp4','')
        tail_num = '(' + video.split('(')[1]
        if pre_name in name_dic.keys():
            old_path = os.path.join(folder_path, video)
            new_name = name_dic[pre_name]+tail_num
            new_path = os.path.join(folder_path, new_name)
            try:
                os.rename(old_path,new_path)
            except:
                pass
            print(f'-{video} renamed as {new_name}')
        else:
            print(f'-{video} not exist in {DB_NAME_FILE}')

# 删除无效数据(过期且未下载):
def db_clear2():
    videos = db.query(Video).filter_by(expired=True,downloaded=False).all()
    cnt=0
    for video in videos:
        if cnt % 20 == 0:
            print(f'-{cnt} videos changed.')
            db.session.commit()
        db.session.delete(video)
        cnt += 1
    db.session.commit()


# *标记已经下载的视频
def db_mark_downloaded2():
    file = open('.\\file\\temp.txt','r')
    cnt = 0
    for line in file.readlines():
        if cnt % 20 == 0:
            print(f"-{cnt} video marked.")
            db.session.commit()

        name = line.replace('\n','')    
        db_video = db.query(Video).filter_by(new_name=name).all()
        if db_video is not None:
            for i in db_video:
                i.downloaded = True
                cnt = cnt + 1
    db.session.commit()
    file.close()


if __name__ == '__main__':
    # db_reset()
    # db_clear()
    # db_dumpfile()
    # db_change_column()
    # db_mark_downloaded2()
    # db_rename2()
    db_clear2()
    pass
