# -*- coding: utf-8 -*-
import datetime
import json
import os

import scrapy
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest

from UtrehdsCrawlers.items import UtrehdscrawlersItem

# Comments can be found in static.py


class DynamicSpider(scrapy.Spider):
    name = 'dynamic'
    start_urls = []
    urls = []

    def __init__(self, name=None, property_type=None, price_type=None, *args, **kwargs):
        super(DynamicSpider, self).__init__(*args, **kwargs)
        self.name = name
        self.property_type = property_type
        self.price_type = price_type

        cwd = os.getcwd()
        with open(os.path.join(cwd, "profiles.json"), 'r') as profiles:
            data = json.load(profiles)
            self.start_urls.append(
                data[name][property_type][price_type]['link'])
            self.general_link = data[name][property_type][price_type]['selectors']['link'][0]
            self.link = data[name][property_type][price_type]['selectors']['link'][1]
            self.next_page = data[name][property_type][price_type]['selectors']['nextPage']
            self.location = data[name][property_type][price_type]['selectors']['location']
            self.price = data[name][property_type][price_type]['selectors']['price']
            self.size = data[name][property_type][price_type]['selectors']['size']

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url=url, callback=self.parse, args={"wait": 1})

    def parse(self, response):
        for link in response.css(self.general_link):
            self.urls.append(response.urljoin(
                link.css(self.link).extract_first()))

        # next_page = response.xpath(
        #     self.next_page).extract_first()
        # next_page_join = response.urljoin(next_page)
        # if next_page is not None and next_page_join != self.start_urls[0]:
        #     yield SplashRequest(url=response.urljoin(next_page), callback=self.parse, args={"wait": 1})
        # else:
        for url in self.urls:
            yield SplashRequest(url=url, callback=self.parse_property, args={"wait": 1}, meta={'link': url})

    def parse_property(self, response):
        item = UtrehdscrawlersItem()
        item['link'] = response.meta['link']
        item['location'] = response.xpath(
            self.location).extract_first()
        item['price'] = response.xpath(
            self.price).extract_first()
        item['size'] = response.xpath(
            '//label[contains(text(), \"Užitná plocha:\")]/following-sibling::strong[1]/span[1]/text()').extract_first()
        item['property_type'] = self.property_type
        item['price_type'] = self.price_type
        item['time'] = datetime.datetime.now()
        yield item
