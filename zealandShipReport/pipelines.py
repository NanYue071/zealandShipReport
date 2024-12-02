# -*- coding: utf-8 -*-
import os
import openpyxl
import datetime


class ZealandshipreportPipeline:
    """
    写入文件的pipline
    """

    def __init__(self):
        now = datetime.datetime.now()
        self.file = None
        self.file_name = '../output/zealandShip' + "_" + now.strftime("%Y%m%d") + '.xlsx'
        if not os.path.exists('../output'):
            os.mkdir('../output')

        if os.path.exists(self.file_name):
            self.wb = openpyxl.load_workbook(self.file_name)
            self.ws = self.wb.active
        else:
            self.wb = openpyxl.Workbook()
            self.ws = self.wb.active
            self.ws.append([r'Port', 'Week', 'Status', 'Vessel', 'IMO_No', 'Voyage', 'Agent', 'Exporter', 'Arrival',
                            'Departure', 'Berth', 'Trade', 'From', 'ToPort', 'ORIGIN/DEST'])

    def process_item(self, item, spider):
        """
        处理item
        """
        # if spider.name == 'tauranga':
        data = [item['port'], item['week'], item['status'], item['vessel'], item['imo'],
                item['voyage'], item['agent'], item['exporter'], item['arrival'], item['departure'], item['berth'],
                item['trade'], item['fromPort'], item['toPort'], item['originAndDest']]
        self.ws.append(data)
        return item

    def close_spider(self, spider):
        print("关闭爬虫程序")
        self.wb.save(filename=self.file_name)
        self.wb.close()
