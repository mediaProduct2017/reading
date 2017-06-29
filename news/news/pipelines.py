# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import mysql.connector
from scrapy import log
import os
import db_info
import bleach


class NewsPipeline(object):

    def __init__(self):
        # number of news inserted into database
        self.s_number_news_got = 0
        self.conn = mysql.connector.connect(user=os.environ["MYSQL_USERNAME"],
                                            password=os.environ["MYSQL_PASSWORD"],
                                            host='reading.cjnyfwqsuidc.us-west-1.rds.amazonaws.com',
                                            database='newsdb')
        self.cursor = self.conn.cursor()

    def open_spider(self, spider):
        self.conn.autocommit(1)
        self.conn.set_character_set('utf8')
        self.cursor.execute('SET NAMES utf8;')
        self.cursor.execute('SET CHARACTER SET utf8;')
        self.cursor.execute('SET character_set_connection=utf8;')

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):
        self.store_data_into_mysql(
            item['title'], item['title_hash'],
            item['content'], item['url'])
        return item

    def store_data_into_mysql(self, title, title_hash, content, url):
        # Primary key is title_hash
        SELCT_IF_EXIST = "SELECT * FROM urllist WHERE page_id = '%d'"
        INSERT_INTO_DB_VALUES = "INSERT INTO urllist VALUES(%d, %s, %s, %s);"
        rows = self.cursor.execute(SELCT_IF_EXIST % title_hash)
        if rows.fetchone() is None and len(content) > 10:
            self.cursor.execute(INSERT_INTO_DB_VALUES,
                                (title_hash, url, bleach.clean(title),
                                 bleach.clean(content)))
            self.s_number_news_got += 1
            log.msg(str(self.s_number_news_got) + ":title:"
                    + title + " url:" + url, level=log.INFO)
