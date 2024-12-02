#!/usr/bin/env python
# encoding: utf-8
import datetime
import re

from scrapy import Spider
from scrapy.http import Request
from zealandShipReport.items import ZealandshipreportItem
from zealandShipReport.utils.common import parse_date


class EastLandSpider(Spider):
    """
    Gisborne港口的船报数据
    """
    name = "eastLand"
    allowed_domains = ['www.eastlandport.nz']

    # 获取当前的日期
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y/%m/%d")

    def start_requests(self):
        """
        爬虫入口
        """
        print("爬取Gisborne EastLand港口船期信息")
        url = 'https://www.eastlandport.nz/operations/shipping-schedule/'
        yield Request(url, callback=self.parse, meta={'source_url': url})

    def parse(self, response, **kwargs):
        """
        网页解析
        """
        # In Port的船期信息
        in_port_rows = response.xpath('.//div[@class="container container--shipping '
                                      'shipping--in-port"]/section/div/table/tbody/tr')
        if in_port_rows is not None:
            for row in in_port_rows:
                vessel = row.xpath('.//td[@class="shipname"]/span/text()').get()
                berth = row.xpath('.//td/span[@class="ship--berth"]/text()').get()
                columns = row.xpath('.//td/text()').getall()
                columns = columns[-11:]
                if re.search(r"logs", columns[8], re.IGNORECASE):
                    item = self.parse_data(columns, name=vessel, berth=berth, status='In Port')
                    yield item

        # Expected Arrivals的船期信息
        expected_arrivals_rows = response.xpath('.//div[@class="container container--shipping '
                                                'shipping--arrivals"]/section/div/table/tbody/tr')
        if expected_arrivals_rows is not None:
            for row in expected_arrivals_rows:
                vessel = row.xpath('.//td[@class="shipname"]/span/text()').get()
                berth = row.xpath('.//td/span[@class="ship--berth"]/text()').get()
                columns = row.xpath('.//td/text()').getall()
                # 这里有一些特殊情况 出发和到达的目的地都是Sea 出发时间和到达时间都没有
                if columns[-1] == 'Sea' and columns[-2] == 'Sea':
                    columns = columns[-5:]
                else:
                    columns = columns[-11:]
                if len(columns) < 11:
                    if re.search(r"logs", columns[2], re.IGNORECASE):
                        item = self.parse_data_error(columns, name=vessel, berth=berth, status='Expected Arrivals')
                        yield item
                else:
                    if re.search(r"logs", columns[8], re.IGNORECASE):
                        item = self.parse_data(columns, name=vessel, berth=berth, status='Expected Arrivals')
                        yield item

        # Departed Vessels的船期信息
        departed_vessels_rows = response.xpath('.//div[@class="container container--shipping '
                                               'shipping--departed"]/section/div/table/tbody/tr')
        if departed_vessels_rows is not None:
            for row in departed_vessels_rows:
                vessel = row.xpath('.//td[@class="shipname"]/span/text()').get()
                columns = row.xpath('.//td/text()').getall()
                columns = columns[-9:]
                if re.search(r"logs", columns[6], re.IGNORECASE):
                    item = self.parse_data_departed(columns, name=vessel, status='Departed Vessels')
                    yield item

    def parse_data(self, data, name, berth, status):
        """
        解析Item
        """
        item = ZealandshipreportItem()
        item['port'] = 'Gisborne'
        item['week'] = self.formatted_time
        item['status'] = status
        item['vessel'] = name
        item['imo'] = ''
        item['voyage'] = ''
        item['agent'] = data[6]
        item['exporter'] = data[7]
        item['arrival'] = parse_date(data[2])
        item['departure'] = parse_date(data[4])
        item['berth'] = berth
        item['trade'] = data[8]
        item['fromPort'] = data[9]
        item['toPort'] = data[10]
        item['originAndDest'] = ''
        return item

    def parse_data_error(self, data, name, berth, status):
        """
        解析Item
        """
        item = ZealandshipreportItem()
        item['port'] = 'Gisborne'
        item['week'] = self.formatted_time
        item['status'] = status
        item['vessel'] = name
        item['imo'] = ''
        item['voyage'] = ''
        item['agent'] = ''
        item['exporter'] = data[1]
        item['arrival'] = parse_date(data[0])
        item['departure'] = ''
        item['berth'] = berth
        item['trade'] = data[2]
        item['fromPort'] = data[3]
        item['toPort'] = data[4]
        item['originAndDest'] = ''
        return item

    def parse_data_departed(self, data, name, status):
        """
        解析Item
        """
        item = ZealandshipreportItem()
        item['port'] = 'Gisborne'
        item['week'] = self.formatted_time
        item['status'] = status
        item['vessel'] = name
        item['imo'] = ''
        item['voyage'] = ''
        item['agent'] = data[4]
        item['exporter'] = data[5]
        item['arrival'] = parse_date(data[0])
        item['departure'] = parse_date(data[2])
        item['berth'] = ''
        item['trade'] = data[6]
        item['fromPort'] = data[7]
        item['toPort'] = data[8]
        item['originAndDest'] = ''
        return item
