import os
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from zealandShipReport.spiders.eastLand import EastLandSpider
from zealandShipReport.spiders.tauranga import TaurangaSpider
from zealandShipReport.spiders.northPort import NorthPortSpider
from zealandShipReport.spiders.napier import NapierSpider
from zealandShipReport.spiders.wellington import WellingtonSpider
from scrapy import signals
from scrapy.signalmanager import dispatcher


def spider_closed(spider, reason):
    if spider.name == 'tauranga':
        process.crawl(mode_to_spider['EastLand'])
    elif spider.name == 'eastLand':
        process.crawl(mode_to_spider['northPort'])


os.environ['SCRAPY_SETTINGS_MODULE'] = 'settings'
settings = get_project_settings()
process = CrawlerProcess(settings)
mode_to_spider = {
    'Tauranga': TaurangaSpider,
    'EastLand': EastLandSpider,
    'northPort': NorthPortSpider,
    'napier': NapierSpider,
    'wellington': WellingtonSpider,
}

# 连接信号，爬虫关闭时触发 `spider_closed` 回调函数
# dispatcher.connect(spider_closed, signal=signals.spider_closed)

process.crawl(mode_to_spider['wellington'])
process.start()
