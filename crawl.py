# coding: utf-8
# test font size

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
        # print self.__dict__
        # print self
        # print self.session
        try:
            self.session.close()
        except AttributeError:
            print "Crawler instance has no attribute 'session'"

    def dbcommit(self):
        self.session.commit()

    def createindextables(self):
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

        class Wordlist(Base):
            __tablename__ = 'wordlist'
            word = Column(String(20), nullable=False)
            id = Column(Integer, primary_key=True)

        self.table['wordlist'] = Wordlist

        class Wordlocation(Base):
            __tablename__ = 'wordlocation'
            wordid = Column(Integer, ForeignKey(word.id), nullable=False)
            urlid = Column(Integer, ForeignKey(url.id), nullable=False)
            location = Column(Integer)
            id = Column(Integer, primary_key=True)

        word = relationship(Wordlist)
        url = relationship(Urllist)

        self.table['wordlocation'] = Wordlocation

        class Link(Base):
            __tablename__ = 'link'
            fromid = Column(Integer, ForeignKey(urlfrom.id), nullable=False)
            toid = Column(Integer, ForeignKey(urlto.id), nullable=False)
            id = Column(Integer, primary_key=True)

        urlfrom = relationship(Urllist)
        urlto = relationship(Urllist)

        self.table['link'] = Link

        class Linkword(Base):
            __tablename = 'linkword'
            linkid = Column(Integer, ForeignKey(link.id), nullable=False)
            wordid = Column(Integer, ForeignKey(wordlist.id), nullable=False)
            id = Column(Integer, primary_key=True)

        link = relationship(Link)
        wordlist = relationship(Wordlist)

        self.table['linkword'] = Linkword

        Base.metadata.create_all(self.engine)