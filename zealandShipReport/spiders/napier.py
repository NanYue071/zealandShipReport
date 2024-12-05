#!/usr/bin/env python
# encoding: utf-8
import datetime

import scrapy
from scrapy import Spider
from zealandShipReport.items import ZealandshipreportItem


class NapierSpider(Spider):
    """
    Napier港口的船报数据
    """
    name = "napier"
    allowed_domains = ['www.napierport.co.nz']

    # 获取当前的日期
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y/%m/%d")

    def start_requests(self):
        """
        爬虫入口
        """
        print("爬取Napier港口船期信息")
        url = 'https://www.napierport.co.nz/wp-admin/admin-ajax.php'

        requests = scrapy.FormRequest(url=url,
                                      formdata={'action': 'vesselsinport'},
                                      method='POST',
                                      callback=self.parse)

        yield requests

    def parse(self, response, **kwargs):
        """
        网页解析
        """
        # In Port的船期信息
        in_port_columns = response.xpath('.//div[@class="divtable-body asd tablefortabs clear"]/div['
                                                   '@log-row="logs"]')
        if in_port_columns is not None:
            for columns in in_port_columns:
                item = self.parse_data(columns, status='In Port')
                yield item

        next_url = 'https://www.napierport.co.nz/wp-admin/admin-ajax.php'
        yield scrapy.FormRequest(url=next_url,
                                 formdata={'action': 'vesselsdue'},
                                 method='POST',
                                 callback=self.second_parse)

    def second_parse(self, response, **kwargs):
        """
        网页解析
        """
        # Expected Arrivals的船期信息
        expected_arrivals_columns = response.xpath('.//div[@class="divtable-body asd tablefortabs clear"]/div['
                                                   '@log-row="logs"]')
        if expected_arrivals_columns is not None:
            for columns in expected_arrivals_columns:
                item = self.parse_data(columns, status='Expected Arrivals')
                yield item

        next_url = 'https://www.napierport.co.nz/wp-admin/admin-ajax.php'
        yield scrapy.FormRequest(url=next_url,
                                 formdata={'action': 'vesselsdeparture'},
                                 method='POST',
                                 callback=self.third_parse)

    def third_parse(self, response, **kwargs):
        """
        网页解析
        """
        # Departed Vessels的船期信息
        departed_vessels_columns = response.xpath('.//div[@class="divtable-body asd tablefortabs clear"]/div['
                                                   '@log-row="logs"]')
        if departed_vessels_columns is not None:
            for columns in departed_vessels_columns:
                item = self.parse_data(columns, status='Departed Vessels')
                yield item

    def parse_data(self, data, status):
        """
        解析Item
        """
        item = ZealandshipreportItem()
        item['port'] = 'Napier'
        item['week'] = self.formatted_time
        item['status'] = status
        item['imo'] = ''
        item['exporter'] = ''
        if status == 'Departed Vessels':
            item['vessel'] = data.xpath('.//div[@class="cell cell-5"]/a/text()').get()
            item['arrival'] = data.xpath('.//div[@class="two-cell cell cell-1"]/text()').get()
            item['departure'] = data.xpath('.//div[@class="cell cell-3"]/text()').get()
            item['berth'] = ''
            item['voyage'] = data.xpath('.//div[@class="cell cell-6"]/text()').get()
            item['agent'] = data.xpath('.//div[@class="cell cell-11"]/text()').get()
            item['trade'] = data.xpath('.//div[@class="cell cell-7"]/text()').get()
            item['fromPort'] = data.xpath('.//div[@class="cell cell-8"]/text()').get()
            item['toPort'] = data.xpath('.//div[@class="cell cell-9"]/text()').get()
            item['originAndDest'] = data.xpath('.//div[@class="cell cell-10"]/text()').get()
        elif status == 'Expected Arrivals':
            item['vessel'] = data.xpath('.//div[@class="cell cell-4"]/a/text()').get()
            item['arrival'] = data.xpath('.//div[@class="two-cell cell cell-1"]/text()').get()
            item['departure'] = data.xpath('.//div[@class="cell cell-3"]/text()').get()
            item['voyage'] = data.xpath('.//div[@class="cell cell-5"]/text()').get()
            item['agent'] = data.xpath('.//div[@class="cell cell-12"]/text()').get()
            item['berth'] = ''
            item['trade'] = data.xpath('.//div[@class="cell cell-6"]/text()').get()
            item['fromPort'] = data.xpath('.//div[@class="cell cell-9"]/text()').get()
            item['toPort'] = data.xpath('.//div[@class="cell cell-10"]/text()').get()
            item['originAndDest'] = data.xpath('.//div[@class="cell cell-11"]/text()').get()
        elif status == 'In Port':
            item['vessel'] = data.xpath('.//div[@class="cell cell-5"]/a/text()').get()
            item['arrival'] = data.xpath('.//div[@class="cell cell-2"]/text()').get()
            item['departure'] = data.xpath('.//div[@class="two-cell cell cell-1"]/text()').get()
            item['berth'] = data.xpath('.//div[@class="cell cell-1"]/text()').get()
            item['voyage'] = data.xpath('.//div[@class="cell cell-6"]/text()').get()
            item['agent'] = data.xpath('.//div[@class="cell cell-11"]/text()').get()
            item['trade'] = data.xpath('.//div[@class="cell cell-7"]/text()').get()
            item['fromPort'] = data.xpath('.//div[@class="cell cell-8"]/text()').get()
            item['toPort'] = data.xpath('.//div[@class="cell cell-9"]/text()').get()
            item['originAndDest'] = data.xpath('.//div[@class="cell cell-10"]/text()').get()
        return item
