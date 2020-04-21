import datetime
import json
import os

import scrapy

from UtrehdsCrawlers.items import UtrehdscrawlersItem


class StaticSpider(scrapy.Spider):
    name = 'static'
    start_urls = []
    urls = []

    # takes arguments which is then used to get data in json
    def __init__(self, name=None, property_type=None, price_type=None, *args, **kwargs):
        super(StaticSpider, self).__init__(*args, **kwargs)
        self.name = name
        self.property_type = property_type
        self.price_type = price_type

        # opens json and saves data
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

    # starts the spider process
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # saves all links on given page
        for link in response.css(self.general_link):
            self.urls.append(
                response.urljoin(link.css(self.link).extract_first()))

        # finds all links that will be scrapped
        # once finished it opens each link and extracts the data
        # page_url = response.xpath(self.next_page).get()
        # if page_url is not None and response.urljoin(page_url) != self.start_urls[0]:
        #     yield scrapy.Request(url=response.urljoin(page_url), callback=self.parse)
        # else:
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse_property)

    # scraps actual data
    def parse_property(self, response):
        item = UtrehdscrawlersItem()
        item['link'] = response.request.url
        item['location'] = response.xpath(
            self.location).extract_first()
        item['price'] = response.xpath(
            self.price).extract_first()
        item['size'] = response.xpath(
            self.size).extract_first()
        item['property_type'] = self.property_type
        item['price_type'] = self.price_type
        item['time'] = datetime.datetime.now()
        yield item
