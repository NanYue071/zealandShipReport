#!/usr/bin/env python
# encoding: utf-8
import datetime
import re

from scrapy import Spider
from scrapy.http import Request
from zealandShipReport.items import ZealandshipreportItem


class EastLandSpider(Spider):
    """
    Gisborne港口的船报数据
    """
    name = "northPort"
    allowed_domains = ['northport.co.nz']

    # 获取当前的日期
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y/%m/%d")

    def start_requests(self):
        """
        爬虫入口
        """
        print("爬取Gisborne NorthPort港口船期信息")
        url = 'https://northport.co.nz/inportpage/allshippingmovements'
        yield Request(url, callback=self.parse, meta={'source_url': url})

    def parse(self, response, **kwargs):
        """
        网页解析
        """
        tables = response.xpath('.//table[@class="views-table cols-10 table table-condensed table-0 table-0 '
                                'table-0"]')
        if tables is not None:
            for table in tables:
                status = table.xpath('.//caption/text()').get()
                rows = table.xpath('.//tbody/tr')
                for row in rows:
                    cargo = row.xpath('.//td[@class="views-field views-field-field-sr-dcargo"]/text()').get()
                    if re.search(r"logs", cargo, re.IGNORECASE):
                        item = self.parse_data(row, status=status)
                        yield item

    def parse_data(self, data, status):
        """
        解析Item
        """
        item = ZealandshipreportItem()
        item['port'] = 'Gisborne'
        item['week'] = self.formatted_time
        item['status'] = status
        item['vessel'] = data.xpath('.//td[@class="views-field views-field-views-conditional"]/a/text()').get()
        item['imo'] = ''
        item['voyage'] = ''
        item['agent'] = data.xpath('.//td[@class="views-field views-field-field-sr-dagent"]/text()').get()
        item['exporter'] = ''
        item['arrival'] = data.xpath('.//td[@class="views-field views-field-field-sr-darrival"]/span/text()').get()
        item['departure'] = data.xpath('.//td[@class="views-field views-field-field-sr-ddeparturedate"]/span/text()').get()
        item['berth'] = data.xpath('.//td[@class="views-field views-field-field-sr-dberth"]/text()').get()
        item['trade'] = data.xpath('.//td[@class="views-field views-field-field-sr-dcargo"]/text()').get()
        item['fromPort'] = data.xpath('.//td[@class="views-field views-field-field-sr-dlastport"]/text()').get()
        item['toPort'] = data.xpath('.//td[@class="views-field views-field-field-sr-dnextport"]/text()').get()
        item['originAndDest'] = ''
        return item
