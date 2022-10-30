# TJCours
> TJ Crawler 网上课程直链获取(courses.tongji)
>
> **P.S. 更多材料，请联系邮箱 rayhuc@163.com，并备注说明来意**

<br/>

### (一) 基本信息

- 作者：Ray
- 时间：2022-10-21
- 说明：
  - 可以批量爬取 courses 上自己收藏了的课程的直链，并存入数据库 (SQLite) 中；
  - 用户需要在网页手动输入个人的学号和密码，完成统一认证后才能使用；
  - 项目个人无聊时编写的代码，无其他意图，其他使用代码时也不要瞎搞哈；
  - 目前没有添加 UI，欢迎有兴趣的青年才俊完善项目；

<br/>


### (二) 环境配置 (Win)

#### 1. 安装虚拟环境和必要包

- 推荐使用 pipenv 安装虚拟环境和包

  ```bash
  pipenv install
  pipenv shell
  ```

<br/>

#### 2. 下载 Webdriver

- 按照电脑安装 Chrome 的版本，在 [ChromeDriver 网站](https://chromedriver.chromium.org/) 下载对应的 Webdriver；
- 将下载好的文件放在该文件夹下，替换 `chromedriver.exe`

<br/>

### (三) 项目运行()

#### 1. 启动虚拟环境 (shell)

- 进入命令行，cd 到当前目录，启动虚拟环境，运行 `app.py`：

  ```bash
  pipenv shell
  python app.py
  ```

<br/>

#### 2. 手动登录 (login)

- 在弹出的自动测试窗口中，使用统一身份认证登录； 

  <img src=".\res\login.jpg" alt="image-20221030231640142" style="zoom:50%;" />

- 登录成功后，在命令行按下 `Enter`，告知程序以登陆成功，开始下一步；

  <img src=".\res\confirm.jpg" alt="image-20221030231932881" style="zoom:80%;" />

<br/>

#### 3. 模式选择 (chose mode)  

- 在命令行输入 1/2/3/x 以选择不同的爬取模式**(推荐 2)**，输入后按下 `Enter` 开始爬取：

  | Code  |            Mode            | Status |                           Function                           |
  | :---: | :------------------------: | :----: | :----------------------------------------------------------: |
  |   1   |         dashboard          | 不维护 | 从 dashbasrd 爬取数据，没有数据库，功能简单；可以在configs.py 中修改一些参数，调整爬取数据 |
  | **2** | **collection (This term)** | 维护中 | 从 collection 爬取数据，有数据库，只可以爬取已经收藏的课程；可以在configs.py 中修改一些参数，调整爬取数据 |
  |   3   |   collection (Last term)   | 未开工 |          从 上学期的 collection 爬取数据，还没代码           |
  |   x   |            exit            |   -    |                      结束进程，退出程序                      |

- 爬到的直链除了存到数据库中，还存到了 `.\file\i_link.txt` 中，其他文件说明如下：

  |    File     | Mode |                            Usage                             |
  | :---------: | :--: | :----------------------------------------------------------: |
  | db_link.txt | 覆写 |          保存从数据库导出的 **直链链接**, 用来下载           |
  | db_name.txt | 追加 | 保存从数据库导出 **原始文件名** 和 **修改文件名**, 用来批量改名 |
  | i_link.txt  | 覆写 |            保存单次爬取的  **直链链接**, 用来下载            |
  | i_name.txt  | 覆写 | 保存单次爬取的 **原始文件名** 和 **修改文件名**, 用来批量改名 |
  |   log.txt   | 追加 |              运行的 log 记录，每次运行时不覆写               |

<br/>

#### 4. 下载视频 (download)

- 复制直链链接，然后使用自己本地的下载器（迅雷、IDM 等都行)，直接添加任务即可；
- 部分下载器会自动读取剪切板，复制之后就会自动弹出下载框；

<br/>

#### 5. 后续处理 (other)

> **以下功能还没来得及整合，可以跑跑代码自己完成**

- 下载后的文件一般名字比较乱，可以根据 `i_name.txt` 或 `db_name.txt` 改名，代码在 `.temp\aio_rename,py` 和 `db_tool.py` 中都有；
- 数据库中有很多数据，`db_tool.py` 有一些数据处理和读取的函数可以使用，推荐自己写一些函数，可以实现更多的操作；
- 如果有问题，欢迎联系邮箱 rayhuc@163.com，并备注说明来意
