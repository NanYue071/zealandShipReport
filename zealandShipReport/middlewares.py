# encoding: utf-8
from scrapy import signals
from zealandShipReport.utils import crawl_proxy
import random
import json
import re
from zealandShipReport import settings
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.http.headers import Headers


class IPProxyMiddleware(object):
    """
    代理IP中间件
    """
    def __init__(self):
        # 爬取有效ip
        self.ip_list = crawl_proxy.get_ips(pages=3, refresh=False)
        # 请求已经失败的次数
        self.retry_time = 0
        self.index = random.randint(0, len(self.ip_list) - 1)

    def process_request(self, request, spider):
        # 失败重试次数
        self.retry_time = 0
        # 随机选取 ip
        proxy = json.loads(self.ip_list[self.index])
        print('选取的 ip：' + proxy.get('url'))
        # 设置代理
        request.meta['Proxy'] = proxy.get('url')

    def process_response(self, request, response, spider):
        """
        处理返回的 Response
        :param request:
        :param response:
        :param spider:
        :return:
        """
        # 针对4**、和5** 响应码，重新选取 ip
        if re.findall('[45]\d+', str(response.status)):
            print(u'[%s] 响应状态码：%s' % (response.url, response.status))
            if self.retry_time > settings.get('MAX_RETRY', 5):
                return response
            if response.status == 418:
                sec = random.randrange(30, 35)
                print(u'休眠 %s 秒后重试' % sec)
                # time.sleep(sec)
            self.retry_time += 1
            proxy = json.loads(random.choice(self.ip_list))
            print('失败 %s 次后，重新选取的 ip：%s' % (self.retry_time, proxy.get('url')))
            request.meta['Proxy'] = proxy.get('url')
            return request
        return response


class RandomUserAgentMiddleware(UserAgentMiddleware):
    """
    随机选取 代理
    """
    def __init__(self, user_agent):
        self.user_agent = user_agent
        self.headers = Headers()

    @classmethod
    def from_crawler(cls, crawler):
        """
        开始构造请求前执行的方法
        :param crawler:整个爬虫的全局对象
        :return
        """
        # 从配置里获取 用户代理（User-Agent） 列表
        return cls(user_agent=crawler.settings.get('USER_AGENT_LIST'))

    def process_request(self, request, spider):
        """
        发送请求前执行的方法
        :param request:请求
        :param spider:爬虫应用
        :return:
        """
        # 从 代理 列表中随机选取一个 代理
        agent = random.choice(self.user_agent)
        print('当前 User-Agent ：', agent)
        self.headers['User-Agent'] = agent
        request.headers = self.headers


class ZealandshipreportDownloaderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
