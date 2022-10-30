"""
 @Author    Ray
 @Coding    UTF-8
 @Version   v1.0
 @TimeStamp 2022-10-21
 @Function  批量重命名下载的录播
 @Comment   None
"""

VNAME_FILE  = '.\\vname.txt'    # 保存视频名称和下载名称对应关系的文件路径
VIDEO_PATH  = '.\\video'        # 保存视频的路径

## 1.读取vname.txt文件
vname_file = open(VNAME_FILE,'r')
vname_dic = {}
for line in vname_file.readlines():
    vname = line.split('|')
    vname_dic[vname[0]] = vname[1].replace('\n','.mp4')


## 2.替换文件名
import os

folder_path = VIDEO_PATH
folder = os.listdir(folder_path)

for video in folder:
    if video in vname_dic.keys():
        old_path = os.path.join(folder_path, video)
        new_path = os.path.join(folder_path, vname_dic[video])
        os.rename(old_path,new_path)
        print(f'-{video} renamed as {vname_dic[video]}')
    else:
        print(f'-{video} not exist in {VNAME_FILE}')
