#!/usr/bin/env python
#-*- coding:utf-8 -*-
""" 爬取糗事百科段子.
    目的：1. 简单的获取网页内容
         2. 练习简单的 正则表达式
"""
import urllib
import urllib2
import re

class QSBK(object):
    """ 糗事百科爬虫 
    """
    def __init__(self):
        self.pageIndex = 1
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
        # 初始化 headers
        self.headers = {'User-Agent' : self.user_agent}
        # 存放段子的变量 每一个元素是每一页的段子们
        self.stories = []
        # 程序是否继续运行
        self.enable = False

    def getPage(self, pageIndex):
        """ 根据页数 获取页面原始内容
        """
        try:
            url = 'http://www.qiushibaike.com/hot/page/' + str(pageIndex)
            # 构建请求的request
            request = urllib2.Request(url, headers=self.headers)
            # 利用urlopen获取页面代码
            # 简单的opener 如果需要使用cookie需要urllib2.build_opener(handler) 在构建一个更强大的opener
            response = urllib2.urlopen(request, timeout=6)
            # 读取页面并且转化编码
            content = response.read().decode('utf-8')
            return content
        except urllib2.URLError, e:
            if hasattr(e,"reason"):
                print u"连接糗事百科失败,错误原因",e.reason
                return None

    
    def getPageItems(self,pageIndex):
        """ 返回本页不带图片的段子列表
        """
        pageCode = self.getPage(pageIndex)
        if not pageCode:
            print "页面加载失败...."
            return None
        # .*? 是一个固定的搭配，.和*代表可以匹配任意无限多个字符，加上？表示使用非贪婪模式进行匹配，也就是我们会尽可能短地做匹配
        # (.*?)代表一个分组，在这个正则表达式中我们匹配了五个分组，在后面的遍历item中，item[0]就代表第一个(.*?)所指代的内容，item[1]就代表第二个(.*?)所指代的内容，以此类推
        # re.S 标志代表在匹配时为点任意匹配模式，点.也可以代表换行符
        pattern = re.compile('<div class="author">.*?<a.*?</a>.*?<a.*?>.*?(.*?)</a>.*?'+
                             '<div class="content">\n(.*?)<!--(.*?)-->.*?</div>.*?'+
                             '<div class="stats">.*?<span.*?number.*?>(.*?)</i>', re.S)        
        items = re.findall(pattern, pageCode)
        #用来存储每页的段子们
        pageStories = []
        #遍历正则表达式匹配的信息
        for item in items:
            #item[0]是一个段子的发布者，item[1]是内容, item[2]是时间，item[3]是点赞数
            pageStories.append([item[0].strip(),item[1].strip(),item[2].strip(),item[3].strip()])
        return pageStories    

    #加载并提取页面的内容，加入到列表中
    def loadPage(self):
        #如果当前未看的页数少于2页，则加载新一页
        if self.enable == True:
            if len(self.stories) < 2:
                #获取新一页
                pageStories = self.getPageItems(self.pageIndex)
                #将该页的段子存放到全局list中
                if pageStories:
                    self.stories.append(pageStories)
                    #获取完之后页码索引加一，表示下次读取下一页
                    self.pageIndex += 1

    #调用该方法，每次敲回车打印输出一个段子
    def getOneStory(self,pageStories,page):
        #遍历一页的段子
        for story in pageStories:
            #等待用户输入
            input = raw_input()
            #每当输入回车一次，判断一下是否要加载新页面
            self.loadPage()
            #如果输入Q则程序结束
            if input in ["Q", "q"]:
                self.enable = False
                return
            print u"第%d页\t发布人:%s\t发布时间:%s\n%s\n赞:%s\n" %(page,story[0],story[2],story[1],story[3])

    #开始方法
    def start(self):
        print u"正在读取糗事百科,按回车查看新段子，Q退出"
        #使变量为True，程序可以正常运行
        self.enable = True
        #先加载一页内容
        self.loadPage()
        #局部变量，控制当前读到了第几页
        nowPage = 0
        while self.enable:
            if len(self.stories)>0:
                #从全局list中获取一页的段子
                pageStories = self.stories[0]
                #当前读到的页数加一
                nowPage += 1
                #将全局list中第一个元素删除，因为已经取出
                del self.stories[0]
                #输出该页的段子
                self.getOneStory(pageStories,nowPage)
 
spider = QSBK()
spider.start()    


