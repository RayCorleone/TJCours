import os
def rename():
    ## 2.替换文件名
    folder_path = 'E:\\video'
    folder = os.listdir(folder_path)

    for video in folder:
        name_slt = video.split('_')
        base_name = name_slt[0]+'_'+name_slt[1]
        
        old_path = os.path.join(folder_path, video)
        try: #直接命名(无后缀数字)
            new_name = base_name + '.mp4'
            new_path = os.path.join(folder_path, new_name)
            os.rename(old_path, new_path)
            print(f'-{video} renamed as {new_name}')
        #直接命名失败(循环尝试,添加后缀数字)
        except FileExistsError:
            tail_num = 1
            while True:
                try:
                    new_name = base_name+'_('+str(tail_num)+').mp4'
                    new_path = os.path.join(folder_path, new_name)
                    os.rename(old_path, new_path)
                    print(f'-{video} renamed as {new_name}')
                    break
                except FileExistsError:
                    tail_num = tail_num + 1
                    if tail_num > 100:
                        break

def reload():
    name_file = open('.\\file\\db_name.txt','r+')
    
    dic = {}
    for line in name_file.readlines():
        line = line.replace('\n','')
        if line not in dic.keys():
            dic[line] = 1
        else:
            dic[line] += 1

    for i in dic:
        new_line = str(dic[i])+'|'+i+'\n'
        name_file.write(new_line)

    name_file.close()

def file_cnt():
    # 导出数据库数据
    name_file = open('.\\file\\db_name.txt','r')
    db_dic = {}
    for line in name_file.readlines():
        number = int(line.split('|')[0])
        name = line.split('|')[1].replace('\n','')
        db_dic[name] = number
    name_file.close()

    # 导出文件夹数据
    folder_path = 'E:\\video'
    folder = os.listdir(folder_path)
    for video in folder:
        name_slt = video.replace('.mp4','').split('_')
        base_name = name_slt[0]+'_'+name_slt[1]
        if base_name in db_dic.keys():
            db_dic[base_name] -= 1
    
    for i in db_dic:
        if db_dic[i] == 0:
            print(i)

if __name__ == '__main__':
    reload()
    # file_cnt()
