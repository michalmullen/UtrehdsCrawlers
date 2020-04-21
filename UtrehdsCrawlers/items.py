# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader


class UtrehdscrawlersItem(scrapy.Item):
    # define the fields for your item here like:
    link = scrapy.Field()
    location = scrapy.Field()
    price = scrapy.Field()
    size = scrapy.Field()
    property_type = scrapy.Field()
    price_type = scrapy.Field()
    time = scrapy.Field()
