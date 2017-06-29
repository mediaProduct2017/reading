#!/usr/bin/env python2
# coding=utf-8

import Queue
import threading  # used to populate items

import scrapy
from scrapy.contrib.linkextractors import LinkExtractor
from news.items import NewsItem


class NewsSpider(scrapy.Spider):
    # BFS queue
    g_queue_urls = Queue.Queue(100000)
    g_container_urls = {""}  # empty set
    lock = threading.Lock()

    name = "news"
    allowed_domains = ["sina.cn"]
    start_urls = (
        "http://news.sina.cn/?vt=1&sa=t124d1712309v84",
    )

    def parse_page(self, response):
        title_arr = response.xpath("/html/head/title/text()").extract()
        title = ""
        for i in title_arr:
            title += i
        content_arr = response.xpath("//div/text()").extract()
        content = ""
        for i in content_arr:
            if len(i) > 50:
                content = content + i
        # put data into an dictionary-like object
        item = NewsItem()
        item['title'] = title
        item['title_hash'] = hash(title)
        item['content'] = content
        item['url'] = response.url
        return item

    def wrapper_target_func(self, f, q, items):
        # populating items
        for _ in range(q.qsize()):
            tp_url = q.get(timeout=3)  # 3s timeout
            items.append(self.make_requests_from_url(tp_url))
            items.append(self.make_requests_from_url(tp_url).
                         replace(callback=self.parse_page))
        q.task_done()
        return

    def parse(self, response):
        # set the allowed domains in link
        ln_extractor = LinkExtractor(allow_domains="news.sina.cn",
                                     allow=".*vt=1.*")
        # vt=1 means it's the directory of articles, navigation page
        # get the links from the response
        links = ln_extractor.extract_links(response)
        urls = []
        items = []
        for i in links:
            urls.append(i.url)
            # all the urls not visited are put into queue and container.
            if i.url not in self.g_container_urls:
                self.g_queue_urls.put(i.url)
                self.g_container_urls.add(i.url)
        # make all the requests in the queue
        # to populate items
        for _ in range(20):
            threading.Thread(target=self.wrapper_target_func,
                             args=(self.g_queue_urls, items)).start()
        self.g_queue_urls.join()
        # the main thread is blocked until the queue is empty
        return items
