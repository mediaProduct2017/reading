#!/usr/bin/env python2
# coding=utf-8

import Queue
import threading  # used to populate items which are returned by parse
# Deal with the parsing tasks from a navigation page by multithreads

import scrapy
from scrapy.contrib.linkextractors import LinkExtractor
from news.items import NewsItem


class NewsSpider(scrapy.Spider):
    # BFS queue
    g_queue_urls = Queue.Queue(100000)
    g_container_urls = {""}  # empty set
    # lock = threading.Lock() # lock is not directly used

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
        # //div means all the div blocks in the document
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

    def wrapper_target_func(self, q, items):
        # 本质上是一个kernal，每个thread都来执行这个kernal
        # 这个kernal的输入内存是用q来控制的（不是用数组或列表来控制的），输出内存是用items来控制的，读写是分离的，在这种情况下，parallel programming比较容易，否则的话，parallel programming barrier需要精心设置
    
        # populating items which are returned by parse
        # Deal with the parsing tasks from a navigation page by multithreads
        '''
        while q.qsize()>0:
            tp_url = q.get(timeout=3)
            items.append(self.make_requests_from_url(tp_url).
                         replace(callback=self.parse_page))
            items.append(self.make_requests_from_url(tp_url)) 
        # 这里的while循环才是对的，下面的for循环用作kernal是不合适的
        '''
        for _ in range(q.qsize()):
            # 从开始执行kernal算起，执行多少次循环
            # In a queue, there are many urls from a navigation page
            tp_url = q.get(timeout=3)  # 3s timeout
            # 有可能是None？在代码上有改进的余地
            items.append(self.make_requests_from_url(tp_url).
                         replace(callback=self.parse_page))
            # first get the parsing results, parse the content of url
            # in the thread, parse_page is called and item instances are filled
            items.append(self.make_requests_from_url(tp_url))
            # then append the requests, send the url for more urls to parse
        q.task_done()
        # 发送队列已空的信息
        return

    def parse(self, response):
        # set the allowed domains in link
        ln_extractor = LinkExtractor(allow_domains="news.sina.cn",
                                     allow=".*vt=1.*")
        # vt=1 means it's the directory of articles, navigation page
        # .* is regular expression
        # get the links from the response
        links = ln_extractor.extract_links(response)
        # response is the page to crawl
        
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
        # 当有多个线程共享一个东西的时候，使用queue来做共享的协调，本质上是shared memory
        # 对于GPU编程的c语言的cuda，每个kernal读入哪个内存，写出到哪个内存，是通过编程控制的
        # 此处，读入的内存部分是通过queue来体现的，但编程中不具体控制单个kernal；写出的内存部分是通过一个列表来控制的。
        for _ in range(20):  # 20 threads
            threading.Thread(target=self.wrapper_target_func,
                             args=(self.g_queue_urls, items)).start()
        # parallel programming, for循环中是Thread函数时，不再是serial execution，而是parallel execution。
        # 此种parallel programming的方法，不是针对一个thread给出一个kernal function，而是把kernal function的集合wrapper_target_func给出来。thread数目可能多于或者少于kernal function的集合中kernal的数目，如果多于，则只有部分thread有用，如果少于，则一个thread在执行完一个kernal后，可能还要执行另一个或多个kernal。
        self.g_queue_urls.join()
        # the main thread is blocked until the queue is empty
        # 上面的parallel execution全部执行完之后，才往下执行，返回items.
        # 相当于GPU编程中的syncthreads()，是parallel programming的barrier
        # Every kernal has a bunch of thread blocks, there could be barriers between different blocks
        # 因为q与items输入输出相分离，所以parallel programming的结构上可以只用一个block，一个barrier位于最后
        # 当一个page上的所有链接的具体内容都被提取之后，才进入下一个page（其实就是第一个链接）获取新的链接
        # scrapy首先parse交给它的网页的内容，然后进入到parse函数返回的items中的网页，再调用parse，不断进行下去
        # 对于一次parse函数的调用，可以认为，返回的有子链接的内容（第一次进入的是导航目录），还有孙链接的链接地址
        # 因为只有一个kernal-wrapper_target_func，所以不存在不同kernal之间的implicit barrier
        return items
