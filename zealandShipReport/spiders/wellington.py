#!/usr/bin/env python
# encoding: utf-8
from datetime import datetime, timedelta

import scrapy
import json
from scrapy import Spider
from zealandShipReport.items import ZealandshipreportItem
from zealandShipReport.utils.common import timestamp_to_date


class WellingtonSpider(Spider):
    """
    Napier港口的船报数据
    """
    name = "wellington"
    allowed_domains = ['jmt.centreport.co.nz']

    # 获取当前的日期
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y/%m/%d")

    def start_requests(self):
        """
        爬虫入口
        """
        print("爬取Wellington港口船期信息")

        requests = self.find_shipping_reports(style=0)

        yield requests

    def find_shipping_reports(self, style):

        url = 'https://jmt.centreport.co.nz/bin_public/jadehttp.dll/shipping_movements?CentricRestService'

        # 请求头中不手动设置 User-Agent
        headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*',
        }

        # 获取当前的日期
        toDate = datetime.now()
        # style为0的时候计算的是前一个月日期，style为1的时候是后一个月日期
        if style == 0:
            # 计算前一个月的日期（大约减去 30 天）
            fromDate = toDate - timedelta(days=30)
            movementDateDynamic = "Last,1,Month(s)"
        elif style == 1:
            fromDate = toDate + timedelta(days=30)
            movementDateDynamic = "Next,1,Month(s)"
        elif style == 2:
            fromDate = toDate + timedelta(days=30)
            movementDateDynamic = "Next,1,Month(s)"

        formatted_toData = toDate.strftime("%Y-%m-%d")
        formatted_fromDate = fromDate.strftime("%Y-%m-%d")

        if style == 0:
            # 4434.9是Logs类型
            json_data = {
                "shippingMovementsFilter": {
                    "fromDate": str(formatted_fromDate),
                    "inPortDate": "",
                    "includeArrivals": "true",
                    "includeDepartures": "true",
                    "includeShifts": "false",
                    "movementDateDynamic": movementDateDynamic,
                    "primaryCargoTypeObjStr": "4434.9",
                    "toDate": str(formatted_toData),
                    "vesselObjStr": "",
                    "vesselTypeObjStr": ""
                }
            }
        elif style == 1:
            json_data = {
                "shippingMovementsFilter": {
                    "fromDate": str(formatted_toData),
                    "inPortDate": "",
                    "includeArrivals": "true",
                    "includeDepartures": "true",
                    "includeShifts": "false",
                    "movementDateDynamic": movementDateDynamic,
                    "primaryCargoTypeObjStr": "4434.9",
                    "toDate": str(formatted_fromDate),
                    "vesselObjStr": "",
                    "vesselTypeObjStr": ""
                }
            }
        elif style == 2:
            # 4434.9是Logs类型
            json_data = {
                "shippingMovementsFilter": {
                    "fromDate": "",
                    "inPortDate": str(formatted_toData),
                    "includeArrivals": "true",
                    "includeDepartures": "true",
                    "includeShifts": "false",
                    "movementDateDynamic": movementDateDynamic,
                    "primaryCargoTypeObjStr": "4434.9",
                    "toDate": "",
                    "vesselObjStr": "",
                    "vesselTypeObjStr": ""
                }
            }

        if style == 0:
            requests = scrapy.Request(url=url,
                                      headers=headers,
                                      body=json.dumps(json_data),
                                      method='POST',
                                      callback=self.parse)
        elif style == 1:
            requests = scrapy.Request(url=url,
                                      headers=headers,
                                      body=json.dumps(json_data),
                                      method='POST',
                                      callback=self.expected_parse)
        elif style == 2:
            requests = scrapy.Request(url=url,
                                      headers=headers,
                                      body=json.dumps(json_data),
                                      method='POST',
                                      callback=self.inPort_parse)
        return requests

    def parse(self, response, **kwargs):
        """
        网页解析
        """
        # 前一个月Departed Vessels的船期信息
        data = json.loads(response.text)

        # 处理到达和离开的结果
        result = {}
        shipMessageList = data['shippingMovementArray']
        for shipMessage in shipMessageList:
            voyageCode = shipMessage['voyageCode']
            if voyageCode not in result:
                result[voyageCode] = {
                    'vessel': shipMessage['vesselName'],
                    'arrival': None,
                    'departure': None,
                    'berth': shipMessage['berth'],
                    'voyage': shipMessage['voyageCode'],
                    'agent': shipMessage['agent'],
                    'trade': shipMessage['primaryCargo'],
                    'fromPort': None,
                    'toPort': None,
                }
            if shipMessage['moveType'] == 'Arrive':
                result[voyageCode]['arrival'] = timestamp_to_date(shipMessage['arriveBerthDate'])
                result[voyageCode]['fromPort'] = shipMessage['fromToPort']
            elif shipMessage['moveType'] == 'Depart':
                result[voyageCode]['departure'] = timestamp_to_date(shipMessage['departBerthDate'])
                result[voyageCode]['toPort'] = shipMessage['fromToPort']
            else:
                result[voyageCode]['arrival'] = timestamp_to_date(shipMessage['arriveBerthDate'])
                result[voyageCode]['departure'] = timestamp_to_date(shipMessage['departBerthDate'])
                result[voyageCode]['fromPort'] = shipMessage['fromToPort']
                result[voyageCode]['toPort'] = shipMessage['fromToPort']

        # 将结果转换为列表
        final_result = [{'voyage': voyageCode, **items} for voyageCode, items in result.items()]
        for item_data in final_result:
            item = self.parse_data(item_data, status='Departed Vessels')
            yield item

        requests = self.find_shipping_reports(style=1)
        yield requests

    def expected_parse(self, response, **kwargs):
        """
        网页解析
        """
        # 后一个月Expected Arrivals的船期信息
        data = json.loads(response.text)

        # 处理到达和离开的结果
        result = {}
        shipMessageList = data['shippingMovementArray']
        for shipMessage in shipMessageList:
            voyageCode = shipMessage['voyageCode']
            if voyageCode not in result:
                result[voyageCode] = {
                    'vessel': shipMessage['vesselName'],
                    'arrival': None,
                    'departure': None,
                    'berth': shipMessage['berth'],
                    'voyage': shipMessage['voyageCode'],
                    'agent': shipMessage['agent'],
                    'trade': shipMessage['primaryCargo'],
                    'fromPort': None,
                    'toPort': None,
                }
            if shipMessage['moveType'] == 'Arrive':
                result[voyageCode]['arrival'] = timestamp_to_date(shipMessage['arriveBerthDate'])
                result[voyageCode]['fromPort'] = shipMessage['fromToPort']
            elif shipMessage['moveType'] == 'Depart':
                result[voyageCode]['departure'] = timestamp_to_date(shipMessage['departBerthDate'])
                result[voyageCode]['toPort'] = shipMessage['fromToPort']
            else:
                result[voyageCode]['arrival'] = timestamp_to_date(shipMessage['arriveBerthDate'])
                result[voyageCode]['departure'] = timestamp_to_date(shipMessage['departBerthDate'])
                result[voyageCode]['fromPort'] = shipMessage['fromToPort']
                result[voyageCode]['toPort'] = shipMessage['fromToPort']

        # 将结果转换为列表
        final_result = [{'voyage': voyageCode, **items} for voyageCode, items in result.items()]
        for item_data in final_result:
            item = self.parse_data(item_data, status='Expected Arrivals')
            yield item

        requests = self.find_shipping_reports(style=2)
        yield requests

    def inPort_parse(self, response, **kwargs):
        """
        网页解析
        """
        # In Port的船期信息
        data = json.loads(response.text)

        # 处理到达和离开的结果
        result = {}
        shipMessageList = data['shippingMovementArray']
        for shipMessage in shipMessageList:
            voyageCode = shipMessage['voyageCode']
            if voyageCode not in result:
                result[voyageCode] = {
                    'vessel': shipMessage['vesselName'],
                    'arrival': None,
                    'departure': None,
                    'berth': shipMessage['berth'],
                    'voyage': shipMessage['voyageCode'],
                    'agent': shipMessage['agent'],
                    'trade': shipMessage['primaryCargo'],
                    'fromPort': None,
                    'toPort': None,
                }
            if shipMessage['moveType'] == 'Arrive':
                result[voyageCode]['arrival'] = timestamp_to_date(shipMessage['arriveBerthDate'])
                result[voyageCode]['fromPort'] = shipMessage['fromToPort']
            elif shipMessage['moveType'] == 'Depart':
                result[voyageCode]['departure'] = timestamp_to_date(shipMessage['departBerthDate'])
                result[voyageCode]['toPort'] = shipMessage['fromToPort']
            else:
                result[voyageCode]['arrival'] = timestamp_to_date(shipMessage['arriveBerthDate'])
                result[voyageCode]['departure'] = timestamp_to_date(shipMessage['departBerthDate'])
                result[voyageCode]['fromPort'] = shipMessage['fromToPort']
                result[voyageCode]['toPort'] = shipMessage['fromToPort']

        # 将结果转换为列表
        final_result = [{'voyage': voyageCode, **items} for voyageCode, items in result.items()]
        for item_data in final_result:
            item = self.parse_data(item_data, status='In Port')
            yield item

    def parse_data(self, data, status):
        """
        解析Item
        """
        item = ZealandshipreportItem()
        item['port'] = 'Wellington'
        item['week'] = self.formatted_time
        item['status'] = status
        item['imo'] = ''
        item['exporter'] = ''
        item['vessel'] = data['vessel']
        item['arrival'] = data['arrival']
        item['departure'] = data['departure']
        item['berth'] = data['berth']
        item['voyage'] = data['voyage']
        item['agent'] = data['agent']
        item['trade'] = data['trade']
        item['fromPort'] = data['fromPort']
        item['toPort'] = data['toPort']
        item['originAndDest'] = ''
        return item
