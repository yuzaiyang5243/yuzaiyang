#!/usr/bin/env python
#-*- coding:utf-8 -*-
""" 爬取百度贴吧帖子
    目的：1. 稍微复杂的获取多级网页内容
         2. 存储图片
"""
import urllib
import urllib2
import re
import os
import time

class BDTB(object):
    """ 先登录百度贴吧在根据帖子进入分吧并且获取图片 
    """
    def __init__(self):
        self.pageIndex = 1
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
        self.domain = 'http://tieba.baidu.com'
        # 初始化 headers
        self.headers = {'User-Agent' : self.user_agent}
        self.stories = []
        # 程序是否继续运行
        self.enable = False

    def getPage(self, url):
        """ 根据页数 获取页面原始内容
        """
        try:
            # 构建请求的request
            request = urllib2.Request(url, headers=self.headers)
            content = None
            for i in range(3):
                # 利用urlopen获取页面代码
                response = urllib2.urlopen(request, timeout=6)
                # 读取页面
                content = response.read()
                if content:
                    break
            # 转化编码
            return content.decode('utf-8')
        except urllib2.URLError, e:
            if hasattr(e,"reason"):
                print u"连接百度贴吧失败,错误原因",e.reason
                return None
        except UnicodeDecodeError, e:
            print u"连接百度贴吧失败,错误原因",e.reason
            return None
        except Exception, e:
            print u"连接百度贴吧失败,错误原因",e.reason
            return None

    def getConten(self, pageIndex):
        """ 根据页数返回该页所需的文本 (主)
            http://tieba.baidu.com/f?kw=%E9%87%8C%E7%95%AA&ie=utf-8&pn=0
        """
        pageIndex = (pageIndex - 1) * 50
        url = self.domain + "/f?kw=%E9%87%8C%E7%95%AA&ie=utf-8&pn=" + str(pageIndex)
        content = self.getPage(url)
        if not content:
            print u"页面加载失败...."
            return
        pattern = re.compile('<div class="threadlist_title pull_left j_th_tit.*?<a href="(.*?)".*?title="(.*?)"' +
                             '.*?<span class="tb_icon_author ".*?title="(.*?)"', re.S)
        items = re.findall(pattern, content)
        self.stories = []
        for item in items:
            # item[0]->超链接 item[1]->帖子标题, item[2]->帖子楼主
            #print item[1].encode('utf-8'), item[0], item[2].encode('utf-8')
            self.stories.append((item[0], item[1], item[2]))

    def getTitlePageNum(self, content):
        """ 获取帖子页数
        """
        pattern = re.compile('<li class="l_reply_num".*?<span.*?<span class="red">(.*?)</span>', re.S)
        items = re.findall(pattern, content)
        pageNum = items[0] if items else 1
        return int(pageNum)

    def getSecondConten(self, content, lis):
        """ 获取帖子内所需的所有文本 (二级)
        """
        pattern = re.compile('<img class="BDE_Image".*?src="(.*?)"', re.S)
        items = re.findall(pattern, content)
        for item in items:
            lis.append(item)

    def saveImage(self, dirname, filename, imageUrl):
        """ 保存图片
        """
        u = urllib2.urlopen(imageUrl)
        data = u.read()
        path = './download/%s' % (dirname)
        isExists = os.path.exists(path)
        if not isExists:
            print u'创建了名字叫 %s 的文件夹' % (dirname)
            os.makedirs(path)
        postfix = imageUrl.split('.')[-1]
        f = open('%s/%s' % (path, '%s.%s'%(filename, postfix)), 'wb')
        f.write(data)
        print u'正在保存一张图片到%s' % (dirname)
        f.close()

    def downloadTitle(self, content, title, pageNum):
        """ 下载帖子下面的所有图片 
        Args:
            title ： 帖子信息(单)
        """
        for i in xrange(pageNum):
            n = i + 1
            if n <= 1:
                content = content
            else:
                url = '%s%s?pn=%s' % (self.domain, title[0], n)
                content = self.getPage(url)
            if not content: 
                print u'第 %s 页加载失败....\n' % (n)
                continue
            lis = []
            self.getSecondConten(content, lis)
            if not lis:
                print u'搜索第 %s 页 该页没有找到图片 返回。。。\n' % (n)
            else:
                print u'正在下载。。。'
                for imageUrl in lis:
                    self.saveImage(title[2], str(time.time()), imageUrl)
                print u'下载结束 ！ 本次下载的图片是在该帖子中的第 %s 页\n' % (n)

    def getOneTitle(self, page):
        """ 敲击回车 获取一个帖子 按q推出 
            a -> 下载全部帖子中的图片
            q -> 退出
            d -> 下载当前帖子图片
        """
        input = None
        for index, title in enumerate(self.stories):
            if input != 'a':
                input = raw_input()                        
                pass
            # 退出
            if input == 'q':
                self.enable = False
                return  
            elif input == 'd':
                title = self.stories[index-1]
            content = self.getPage('%s%s' % (self.domain, title[0]))
            pageNum = self.getTitlePageNum(content)   
            # 下载图片
            if input in ['a', 'd']:
                self.downloadTitle(content, title, pageNum)
            title = self.stories[index]
            print u'主题: %s 发布人: %s 共%s页 ' % (title[1], title[2], pageNum)
            
    def start(self):
        """ 启动
        """
        print u"正在读取 百度贴吧,按回车查看新主题，Q退出"
        self.enable = True
        while self.enable:
            # 贴吧
            print u'===== 贴吧第 %s 页 =====' % (self.pageIndex)
            self.getConten(self.pageIndex)
            # 获取帖子
            self.getOneTitle(self.pageIndex)
            self.pageIndex += 1

    
bd = BDTB()
bd.start()







