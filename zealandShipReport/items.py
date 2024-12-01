import scrapy


class ZealandshipreportItem(scrapy.Item):
    port = scrapy.Field()
    week = scrapy.Field()
    status = scrapy.Field()
    vessel = scrapy.Field()
    imo = scrapy.Field()
    voyage = scrapy.Field()
    agent = scrapy.Field()
    exporter = scrapy.Field()
    arrival = scrapy.Field()
    departure = scrapy.Field()
    berth = scrapy.Field()
    trade = scrapy.Field()
    fromPort = scrapy.Field()
    toPort = scrapy.Field()
    originAndDest = scrapy.Field()
    pass
