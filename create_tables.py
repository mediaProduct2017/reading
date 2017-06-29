# coding: utf-8

# create_tables.py

import os
import mysql.connector
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

import db_info


class TableCreator:
    def __init__(self, dbname):
        user = os.environ["MYSQL_USERNAME"]
        password = os.environ["MYSQL_PASSWORD"]
        host = 'reading.cjnyfwqsuidc.us-west-1.rds.amazonaws.com'
        self.table = dict()
        try:
            self.engine = create_engine('mysql+mysqlconnector://%s:%s@%s:3306/%s' % (user, password, host, dbname),
                                        echo=False)
            DBSession = sessionmaker(bind=self.engine)
            self.session = DBSession()
        except:
            raise Exception

    def __del__(self):
        # print self
        try:
            self.session.close()
        except AttributeError:
            print "Wrong in __del__: the instance has no attribute 'session'"

    def dbcommit(self):
        self.session.commit()

    def createindextables(self):
        # establish the database schema
        # self means it is instance method, not class method or static method
        Base = declarative_base()

        class Urllist(Base):
            __tablename__ = 'urllist'

            id = Column(Integer, primary_key=True, autoincrement=True)
            # for primary_key, unique=True and nullable=False are implicated
            # for primary_key, autoincrement=True by default
            # If no other index, clustered index is created automatically for primary key

            url = Column(String(256), nullable=False)
            # maximum of 256 characters, varchar(256)
            title = Column(String(256))
            # String(80)
            content = Column(Text)
            # varchar(10240), varchar(20000)

        self.table['urllist'] = Urllist
        # print 2

        class Wordlist(Base):
            __tablename__ = 'wordlist'
            word = Column(String(20), nullable=False)
            id = Column(Integer, primary_key=True)

        self.table['wordlist'] = Wordlist

        class Wordlocation(Base):
            __tablename__ = 'wordlocation'

            wordid = Column(Integer, ForeignKey('wordlist.id'))
            word = relationship(Wordlist)
            urlid = Column(Integer, ForeignKey('urllist.id'), nullable=False)
            url = relationship(Urllist)

            location = Column(Integer)
            id = Column(Integer, primary_key=True)

        self.table['wordlocation'] = Wordlocation

        class Link(Base):
            __tablename__ = 'link'
            fromid = Column(Integer, ForeignKey('urllist.id'), nullable=False)
            urlfrom = relationship(Urllist)
            toid = Column(Integer, ForeignKey('urllist.id'), nullable=False)
            urlto = relationship(Urllist)
            id = Column(Integer, primary_key=True)

        self.table['link'] = Link

        class Linkword(Base):
            __tablename__ = 'linkword'

            linkid = Column(Integer, ForeignKey('link.id'), nullable=False)
            link = relationship(Link)
            wordid = Column(Integer, ForeignKey('wordlist.id'), nullable=False)
            word = relationship(Wordlist)
            id = Column(Integer, primary_key=True)

        self.table['linkword'] = Linkword
        # print 3

        # print self.engine
        Base.metadata.create_all(self.engine)
        # print 4
