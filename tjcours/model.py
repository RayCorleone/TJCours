"""
 @Author    Ray
 @Coding    UTF-8
 @Version   v0.0
 @TimeStamp 2022-10-28
 @Function  数据库表映射
 @Comment   1)直链链接会过期, 想办法添加相关结构和函数
            2)打包一下数据库相关的工具, 类似flask
"""

from datetime import datetime
from threading import local

from tjcours.extention import db


class TeacherToCourse(db.Base):
    # 指定该类到表名
    __tablename__ = 'teacher_to_course'
    # 定义自增主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 定义具体字段
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))  #外键(关联course表的id)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))#外键(关联teacher表的id)

    # 判断数据是否未添加
    def not_exist(self):
        result = db.query(TeacherToCourse).filter_by(
            course_id = self.course_id,     #同一课号
            teacher_id = self.teacher_id    #同一老师
            ).first()
        if result is not None:
            return False
        return True


class Teacher(db.Base):
    # 指定该类到表名
    __tablename__ = 'teacher'
    # 定义自增主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 定义具体字段
    number = db.Column(db.String(10), nullable=False, index=True, unique=True)#教师号
    name = db.Column(db.Text, nullable=False)                                 #教师名
    # 定义关系
    courses = db.relationship('Course', secondary='teacher_to_course', back_populates='teachers')  #关联Course,中间表teacher_to_course,反向字段teachers


class Course(db.Base):
    # 指定该类到表名
    __tablename__ = 'course'
    # 定义自增主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 定义具体字段
    number = db.Column(db.String(15), nullable=False, index=True, unique=True)#课程号
    name = db.Column(db.Text, nullable=False)                                 #课程名
    term = db.Column(db.Integer, nullable=False, default=1)                   #开课学期(1/2)
    department = db.Column(db.String(15), nullable=False)                     #开课学院(继教/研究/本科/医学/新生x)
    # 定义关系
    videos = db.relationship('Video', back_populates='course')
    teachers = db.relationship('Teacher', secondary='teacher_to_course', back_populates='courses') #关联Teacher,中间表teacher_to_course,反向字段courses


class Video(db.Base):
    # 指定该类到表名
    __tablename__ = 'video'
    # 定义自增主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 定义具体字段
    v_date = db.Column(db.Date, nullable=False, index=True)     #视频录制日期
    size = db.Column(db.Float, nullable=False)                  #视频大小
    old_name = db.Column(db.Text, nullable=False)               #视频原名字
    new_name = db.Column(db.Text, nullable=False)               #视频新名字
    dirc_link = db.Column(db.Text, nullable=False)              #视频直链链接
    timestamp = db.Column(db.DateTime, default=datetime.now())  #视频数据更新时间
    expired = db.Column(db.Boolean, default=False)      #直链是否过期
    dumped = db.Column(db.Boolean, default=False)       #链接是否被导出过
    downloaded = db.Column(db.Boolean, default=False)   #视频是否已保存在本地
    # 定义外键
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))#课程号
    # 定义关系
    course = db.relationship('Course', back_populates='videos')

    # 判断数据是否未添加
    #TODO 考虑链接是否过期
    def can_update(self):
        result = db.query(Video).filter_by(
            v_date = self.v_date,       #同一日期
            course_id = self.course_id, #同一课程
            size = self.size,           #同一大小
            ).first()
        if result is not None:
            return False
        return True
