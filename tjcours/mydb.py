"""
 @Author    Ray
 @Coding    UTF-8
 @Version   v0.0
 @TimeStamp 2022-10-28
 @Function  数据库工具打包
 @Comment   None
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Date, Text, DateTime, String, ForeignKey, Boolean, Float

from tjcours.configs import DATABASE_PATH


class Mydb:
    
    def __init__(self):
        #指定引擎为sqlite
        self.Engine = create_engine(DATABASE_PATH, echo=False)
        #建立基本映射类
        self.Base = declarative_base()
        #建立session对象
        t_session = sessionmaker(bind = self.Engine)
        self.session = t_session()
        #建立query对象
        self.query = self.session.query
        #声明各类数据
        self.Column = Column
        self.relationship = relationship
        self.Integer = Integer
        self.Date = Date
        self.Text = Text
        self.DateTime = DateTime
        self.String = String
        self.ForeignKey = ForeignKey
        self.Boolean = Boolean
        self.Float = Float
    
    def drop_all(self):
        self.Base.metadata.drop_all(self.Engine)
    
    def create_all(self):
        self.Base.metadata.create_all(self.Engine, checkfirst=True)