import os
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from zealandShipReport.spiders.eastLand import EastLandSpider
from zealandShipReport.spiders.tauranga import TaurangaSpider

if __name__ == '__main__':
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'settings'
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    mode_to_spider = {
        'Tauranga': TaurangaSpider,
        'EastLand': EastLandSpider
    }
    process.crawl(mode_to_spider['Tauranga'])
    process.crawl(mode_to_spider['EastLand'])
    process.start()
