# coding: utf-8

# crawlerClass.py

import mysql.connector
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base


class Crawler:
    def __init__(self, dbname):
        try:
            self.table = dict()
            self.engine = create_engine('mysql+mysqlconnector://new_user:new_password@localhost:3306/%s' % dbname,
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
            print "Crawler instance has no attribute 'session'"

    def dbcommit(self):
        self.session.commit()

    def createindextables(self):
        # establish the database schema
        # self means it is instance method, not class method or static method
        Base = declarative_base()

        class Urllist(Base):
            __tablename__ = 'urllist'

            id = Column(Integer, primary_key=True, autoincrement=True)
            # autoincrement=True by default

            url = Column(String(80), nullable=False)
            # maximum of 80 characters
            title = Column(String(80))
            content = Column(String(20000))

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
