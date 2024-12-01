#!/usr/bin/env python
# encoding: utf-8
import datetime
import re

from scrapy import Spider
from scrapy.http import Request
from zealandShipReport.items import ZealandshipreportItem
from zealandShipReport.utils.common import parse_time


class TaurangaSpider(Spider):
    """
    Tauranga港口的船报数据
    """
    name = "tauranga"
    allowed_domains = ['www.port-tauranga.co.nz']

    # 获取当前的日期
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y/%m/%d")

    def start_requests(self):
        """
        爬虫入口
        """
        print("爬取Tauranga港口船期信息")
        url = 'https://www.port-tauranga.co.nz/operations/shipping-schedules/'
        yield Request(url, callback=self.parse, meta={'source_url': url})

    def parse(self, response, **kwargs):
        """
        网页解析
        """
        # In Port的船期信息
        in_port_rows = response.xpath('.//table[@id="pot-data-table-11"]/tbody/tr')
        if in_port_rows is not None:
            for row in in_port_rows:
                columns = row.xpath('.//td/text()').getall()
                if re.search(r"logs", columns[6], re.IGNORECASE):
                    item = self.parse_data(columns, status='In Port')
                    yield item

        # Expected Arrivals的船期信息
        expected_arrivals_rows = response.xpath('.//table[@id="pot-data-table-2"]/tbody/tr')
        if expected_arrivals_rows is not None:
            for row in expected_arrivals_rows:
                columns = row.xpath('.//td/text()').getall()
                if re.search(r"logs", columns[6], re.IGNORECASE):
                    item = self.parse_data(columns, status='Expected Arrivals')
                    yield item

        # Departed Vessels的船期信息
        departed_vessels_rows = response.xpath('.//table[@id="pot-data-table-3"]/tbody/tr')
        if expected_arrivals_rows is not None:
            for row in expected_arrivals_rows:
                columns = row.xpath('.//td/text()').getall()
                if re.search(r"logs", columns[6], re.IGNORECASE):
                    item = self.parse_data(columns, status='Departed Vessels')
                    yield item

    def parse_data(self, data, status):
        """
        解析Item
        """
        item = ZealandshipreportItem()
        item['port'] = 'Tauranga'
        item['week'] = self.formatted_time
        item['status'] = status
        item['vessel'] = data[0]
        item['imo'] = data[1]
        item['voyage'] = ''
        item['agent'] = data[5]
        item['exporter'] = ''
        item['arrival'] = parse_time(data[2])
        item['departure'] = parse_time(data[3])
        item['berth'] = data[4]
        item['trade'] = data[6]
        item['fromPort'] = data[7]
        item['toPort'] = data[8]
        item['originAndDest'] = ''
        return item
