# -*- coding: utf-8 -*-
import os
import openpyxl
import datetime


class ZealandshipreportPipeline:
    """
    写入文件的pipline
    """
    def __init__(self):
        self.file = None
        if not os.path.exists('../output'):
            os.mkdir('../output')
        self.wb = openpyxl.Workbook()
        self.ws = self.wb.active
        self.ws.append([r'Port', 'Week', 'Status', 'Vessel', 'IMO_No', 'Voyage', 'Agent', 'Exporter', 'Arrival',
                        'Departure', 'Berth', 'Trade', 'From', 'ToPort', 'ORIGIN/DEST'])

    def process_item(self, item, spider):
        """
        处理item
        """
        if spider.name == 'tauranga':
            data = [item['port'], item['week'], item['status'], item['vessel'], item['imo'],
                    item['voyage'], item['agent'], item['exporter'], item['arrival'], item['departure'], item['berth'],
                    item['trade'], item['fromPort'], item['toPort'], item['originAndDest']]
            self.ws.append(data)
            return item

    def close_spider(self, spider):
        print("关闭爬虫程序")
        now = datetime.datetime.now()
        file_name = spider.name + "_" + now.strftime("%Y%m%d%H%M%S") + '.xlsx'
        self.wb.save(filename=f'../output/{file_name}')
        self.wb.close()
