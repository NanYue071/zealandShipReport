#!/usr/bin/env python
# encoding: utf-8
from datetime import datetime

import scrapy
import json
import re
from scrapy import Spider
from zealandShipReport.items import ZealandshipreportItem


class NelsonSpider(Spider):
    """
    Napier港口的船报数据
    """
    name = "nelson"
    allowed_domains = ['www.portnelson.co.nz']

    # 获取当前的日期
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y/%m/%d")

    # inPort船报的页数
    in_port_page = 0
    # 每页查询的数量
    every_page_num = 20
    # inPort船报已收集的数量
    in_port_already_num = 0

    # Expected Arrivals船报的页数
    expected_arrivals_page = 0
    # Expected Arrivals船报已收集的数量
    expected_arrivals_already_num = 0

    # Departed Vessels船报的页数
    departed_vessels_page = 0
    # Departed Vessels船报已收集的数量
    departed_vessels_already_num = 0

    def start_requests(self):
        """
        爬虫入口
        """
        print("爬取Nelson港口船期信息")

        # In Port信息
        url = 'https://www.portnelson.co.nz/Umbraco/api/ShippingSchedule/inPort'

        # 请求头中不手动设置 User-Agent
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json, text/plain, */*',
            'Cookie': 'ARRAffinity=7759b4c8c1899256669c5f85a6e81106abd8510133ffa14265a6f52542b12402; '
                      'ARRAffinitySameSite=7759b4c8c1899256669c5f85a6e81106abd8510133ffa14265a6f52542b12402; '
                      '_ga=GA1.1.540224871.1733427745; monsido=4241733427745949; '
                      'ASP.NET_SessionId=4tmq4nnl55mmnpdennrnucud; '
                      '__RequestVerificationToken=xGM7h-vL97J1qQbYnaSTHVWBaQpLXKtUz0Q17HdGbOaOygCouhAiU6MqWYMO_x'
                      '-n7rKfFOR0FTII5EqTr3JnqcdGiih01qHN-28Lgeh5sA01; '
                      '_ga_R08YXJJFJ4=GS1.1.1733748845.4.1.1733748880.0.0.0 '
        }

        json_data = {
            "CurrentPage": self.in_port_page,
            "Operator": "All",
            "SortAsc": True,
            "Take": self.every_page_num,
        }

        requests = scrapy.Request(url=url,
                                  headers=headers,
                                  body=json.dumps(json_data),
                                  method='POST',
                                  callback=self.parse)

        yield requests

    def parse(self, response, **kwargs):
        """
        网页解析
        """
        # In Port的船期信息
        data = json.loads(response.text)

        shipMessageList = data['Vessels']
        for shipMessage in shipMessageList:
            if re.search(r"log", shipMessage['Purpose'], re.IGNORECASE):
                item = self.parse_data(shipMessage, status='In Port')
                yield item
        # 先判断是否有更多in port的船报信息
        if data['TotalCount'] - self.in_port_already_num > self.every_page_num:
            if self.in_port_page == 0:
                self.in_port_page = 2
            else:
                self.in_port_page += 1
            self.in_port_already_num = self.every_page_num + self.in_port_already_num
            self.every_page_num = 10

            # 更多的In Port信息
            url = 'https://www.portnelson.co.nz/Umbraco/api/ShippingSchedule/inPort'

            # 请求头中不手动设置 User-Agent
            headers = {
                'Content-Type': 'application/json;charset=UTF-8',
                'Accept': 'application/json, text/plain, */*',
                'Cookie': 'ARRAffinity=7759b4c8c1899256669c5f85a6e81106abd8510133ffa14265a6f52542b12402; '
                          'ARRAffinitySameSite=7759b4c8c1899256669c5f85a6e81106abd8510133ffa14265a6f52542b12402; '
                          '_ga=GA1.1.540224871.1733427745; monsido=4241733427745949; '
                          'ASP.NET_SessionId=4tmq4nnl55mmnpdennrnucud; '
                          '__RequestVerificationToken=xGM7h-vL97J1qQbYnaSTHVWBaQpLXKtUz0Q17HdGbOaOygCouhAiU6MqWYMO_x'
                          '-n7rKfFOR0FTII5EqTr3JnqcdGiih01qHN-28Lgeh5sA01; '
                          '_ga_R08YXJJFJ4=GS1.1.1733748845.4.1.1733748880.0.0.0 '
            }

            json_data = {
                "CurrentPage": self.in_port_page,
                "Operator": "All",
                "SortAsc": True,
                "Take": self.every_page_num,
            }

            yield scrapy.Request(url=url,
                                 headers=headers,
                                 body=json.dumps(json_data),
                                 method='POST',
                                 callback=self.parse)
        else:
            self.every_page_num = 20
            # 查看Expected Arrivals信息
            url = 'https://www.portnelson.co.nz/Umbraco/api/ShippingSchedule/arriving'

            # 请求头中不手动设置 User-Agent
            headers = {
                'Content-Type': 'application/json;charset=UTF-8',
                'Accept': 'application/json, text/plain, */*',
                'Cookie': 'ARRAffinity=7759b4c8c1899256669c5f85a6e81106abd8510133ffa14265a6f52542b12402; '
                          'ARRAffinitySameSite=7759b4c8c1899256669c5f85a6e81106abd8510133ffa14265a6f52542b12402; '
                          '_ga=GA1.1.540224871.1733427745; monsido=4241733427745949; '
                          'ASP.NET_SessionId=4tmq4nnl55mmnpdennrnucud; '
                          '__RequestVerificationToken=xGM7h-vL97J1qQbYnaSTHVWBaQpLXKtUz0Q17HdGbOaOygCouhAiU6MqWYMO_x'
                          '-n7rKfFOR0FTII5EqTr3JnqcdGiih01qHN-28Lgeh5sA01; '
                          '_ga_R08YXJJFJ4=GS1.1.1733748845.4.1.1733748880.0.0.0 '
            }

            json_data = {
                "CurrentPage": self.expected_arrivals_page,
                "Operator": "All",
                "SortAsc": True,
                "Take": self.every_page_num,
            }

            yield scrapy.Request(url=url,
                                 headers=headers,
                                 body=json.dumps(json_data),
                                 method='POST',
                                 callback=self.arrive_parse)

    def arrive_parse(self, response, **kwargs):
        """
        网页解析
        """
        # Expected Arrivals的船期信息
        data = json.loads(response.text)

        shipMessageList = data['Vessels']
        for shipMessage in shipMessageList:
            if re.search(r"log", shipMessage['Purpose'], re.IGNORECASE):
                item = self.parse_data(shipMessage, status='Expected Arrivals')
                yield item
        # 先判断是否有更多Expected Arrivals的船报信息
        if data['TotalCount'] - self.expected_arrivals_already_num > self.every_page_num:
            if self.expected_arrivals_page == 0:
                self.expected_arrivals_page = 2
            else:
                self.expected_arrivals_page += 1
            self.expected_arrivals_already_num = self.expected_arrivals_page + self.expected_arrivals_already_num
            self.every_page_num = 10

            # 更多的Expected Arrivals信息
            url = 'https://www.portnelson.co.nz/Umbraco/api/ShippingSchedule/arriving'

            # 请求头中不手动设置 User-Agent
            headers = {
                'Content-Type': 'application/json;charset=UTF-8',
                'Accept': 'application/json, text/plain, */*',
                'Cookie': 'ARRAffinity=7759b4c8c1899256669c5f85a6e81106abd8510133ffa14265a6f52542b12402; '
                          'ARRAffinitySameSite=7759b4c8c1899256669c5f85a6e81106abd8510133ffa14265a6f52542b12402; '
                          '_ga=GA1.1.540224871.1733427745; monsido=4241733427745949; '
                          'ASP.NET_SessionId=4tmq4nnl55mmnpdennrnucud; '
                          '__RequestVerificationToken=xGM7h-vL97J1qQbYnaSTHVWBaQpLXKtUz0Q17HdGbOaOygCouhAiU6MqWYMO_x'
                          '-n7rKfFOR0FTII5EqTr3JnqcdGiih01qHN-28Lgeh5sA01; '
                          '_ga_R08YXJJFJ4=GS1.1.1733748845.4.1.1733748880.0.0.0 '
            }

            json_data = {
                "CurrentPage": self.expected_arrivals_page,
                "Operator": "All",
                "SortAsc": True,
                "Take": self.every_page_num,
            }

            yield scrapy.Request(url=url,
                                 headers=headers,
                                 body=json.dumps(json_data),
                                 method='POST',
                                 callback=self.arrive_parse)
        else:
            self.every_page_num = 20
            # 查看Departed Vessels信息
            url = 'https://www.portnelson.co.nz/Umbraco/api/ShippingSchedule/departed'

            # 请求头中不手动设置 User-Agent
            headers = {
                'Content-Type': 'application/json;charset=UTF-8',
                'Accept': 'application/json, text/plain, */*',
                'Cookie': 'ARRAffinity=7759b4c8c1899256669c5f85a6e81106abd8510133ffa14265a6f52542b12402; '
                          'ARRAffinitySameSite=7759b4c8c1899256669c5f85a6e81106abd8510133ffa14265a6f52542b12402; '
                          '_ga=GA1.1.540224871.1733427745; monsido=4241733427745949; '
                          'ASP.NET_SessionId=4tmq4nnl55mmnpdennrnucud; '
                          '__RequestVerificationToken=xGM7h-vL97J1qQbYnaSTHVWBaQpLXKtUz0Q17HdGbOaOygCouhAiU6MqWYMO_x'
                          '-n7rKfFOR0FTII5EqTr3JnqcdGiih01qHN-28Lgeh5sA01; '
                          '_ga_R08YXJJFJ4=GS1.1.1733748845.4.1.1733748880.0.0.0 '
            }

            json_data = {
                "CurrentPage": self.departed_vessels_page,
                "Operator": "All",
                "SortAsc": True,
                "Take": self.every_page_num,
            }

            yield scrapy.Request(url=url,
                                 headers=headers,
                                 body=json.dumps(json_data),
                                 method='POST',
                                 callback=self.departed_parse)

    def departed_parse(self, response, **kwargs):
        """
        网页解析
        """
        # Departed Vessels的船期信息
        data = json.loads(response.text)

        shipMessageList = data['Vessels']
        for shipMessage in shipMessageList:
            if re.search(r"log", shipMessage['Purpose'], re.IGNORECASE):
                item = self.parse_data(shipMessage, status='Departed Vessels')
                yield item
        # 先判断是否有更多Departed Vessels的船报信息
        if data['TotalCount'] - self.departed_vessels_already_num > self.every_page_num:
            if self.departed_vessels_page == 0:
                self.departed_vessels_page = 2
            else:
                self.departed_vessels_page += 1
            self.departed_vessels_already_num = self.departed_vessels_page + self.departed_vessels_already_num
            self.every_page_num = 10

            # 更多的Departed Vessels信息
            url = 'https://www.portnelson.co.nz/Umbraco/api/ShippingSchedule/departed'

            # 请求头中不手动设置 User-Agent
            headers = {
                'Content-Type': 'application/json;charset=UTF-8',
                'Accept': 'application/json, text/plain, */*',
                'Cookie': 'ARRAffinity=7759b4c8c1899256669c5f85a6e81106abd8510133ffa14265a6f52542b12402; '
                          'ARRAffinitySameSite=7759b4c8c1899256669c5f85a6e81106abd8510133ffa14265a6f52542b12402; '
                          '_ga=GA1.1.540224871.1733427745; monsido=4241733427745949; '
                          'ASP.NET_SessionId=4tmq4nnl55mmnpdennrnucud; '
                          '__RequestVerificationToken=xGM7h-vL97J1qQbYnaSTHVWBaQpLXKtUz0Q17HdGbOaOygCouhAiU6MqWYMO_x'
                          '-n7rKfFOR0FTII5EqTr3JnqcdGiih01qHN-28Lgeh5sA01; '
                          '_ga_R08YXJJFJ4=GS1.1.1733748845.4.1.1733748880.0.0.0 '
            }

            json_data = {
                "CurrentPage": self.departed_vessels_page,
                "Operator": "All",
                "SortAsc": True,
                "Take": self.every_page_num,
            }

            yield scrapy.Request(url=url,
                                 headers=headers,
                                 body=json.dumps(json_data),
                                 method='POST',
                                 callback=self.departed_parse)

    def parse_data(self, data, status):
        """
        解析Item
        """
        item = ZealandshipreportItem()
        item['port'] = 'Nelson'
        item['week'] = self.formatted_time
        item['status'] = status
        item['imo'] = ''
        item['exporter'] = ''
        item['vessel'] = data['VesselName']
        item['arrival'] = data['ArrivalDate']['Text']
        item['departure'] = data['DepartedDate']['Text']
        item['berth'] = data['BerthCode']
        item['voyage'] = ''
        item['agent'] = data['OperatorCode']
        item['trade'] = data['Purpose']
        item['fromPort'] = ''
        item['toPort'] = ''
        item['originAndDest'] = ''
        return item
