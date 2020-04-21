# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#
# Will polish data, connect and save to mysql database.

from scrapy.exceptions import NotConfigured
from scrapy.exceptions import DropItem
from geopy.geocoders import Nominatim
import requests
import MySQLdb


class DuplicatesPipeline(object):

    def __init__(self):
        self.links_seen = set()

    def process_item(self, item, spider):
        if item['link'] in self.links_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.links_seen.add(item['link'])
            return item


class DataNormalizationPileline(object):

    # gets location name and turns it into (long, lat)
    def location(self, item):

        url = "https://us1.locationiq.com/v1/search.php"

        data = {
            'key': '8f64307daed1b7',
            'q': item['location'],
            'format': 'json'
        }

        response = requests.get(url, params=data)

        print(response.text)

        # geolocator = Nominatim(domain="localhost:8080", scheme='http')
        # location = geolocator.geocode(item['location'])
        item['location'] = [15.00000, 15.00000]
        return item

    # extraces price amount and currency

    def price(self, item):
        # get price value
        self.currency_origin = str(item['price'])
        try:
            amount = ''.join([n for n in item['price'] if n.isdigit()])
            amount = int(amount)
        except Exception as e:
            print(e)
            amount = 0
        # prices such as 0kc suggest that you should offer a price
        if amount <= 2:
            item['price'] = None
            return item
        else:
            # rent prices are often written in terms of k (*1000)
            if amount < 1000 and item['price_type'] == 'rent':
                item['price'] = amount * 1000
            else:
                item['price'] = amount
            self.currency(item)
        # adds currency to price
        return item

    # finds and sets currency in price string
    def currency(self, item):
        currency_type = ''.join(
            [n for n in self.currency_origin if n.isalpha()])
        if currency_type.upper() in "CZKC":
            currency_type = "CZK"
        elif currency_type.upper() in "EURO":
            currency_type = "EUR"
        elif currency_type.upper() in "USD":
            currency_type = "USD"
        else:
            currency_type = "CZK"
        item['price'] = [item['price'], currency_type]
        return item

    # polishes scrapped data
    def process_item(self, item, spider):

        # runs all functions and updates the items for the next pipeline step
        item = self.location(item)
        item = self.price(item)

        return item


class UtrehdsCrawlersPipeline(object):

    # http://scrapingauthority.com/scrapy-database-pipeline/
    # checks for duplicates in db and saves to db

    def __init__(self, db, user, passwd, host):
        self.db = db
        self.user = user
        self.passwd = passwd
        self.host = host

    @classmethod
    def from_crawler(cls, crawler):
        db_settings = crawler.settings.getdict("DB_SETTINGS")
        if not db_settings:  # if we don't define db config in settings
            raise NotConfigured  # then raise error
        db = db_settings['db']
        user = db_settings['user']
        passwd = db_settings['passwd']
        host = db_settings['host']
        return cls(db, user, passwd, host)  # returning pipeline instance

    def open_spider(self, spider):
        self.conn = MySQLdb.connect(db=self.db,
                                    user=self.user, passwd=self.passwd,
                                    host=self.host,
                                    charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    # checks for duplicates in db and returns id / if non found returns 0
    def duplicates_checker(self, link: str) -> int:
        sql = f"SELECT id FROM `data` WHERE link = '{link}';"
        item_id = self.cursor.execute(sql)
        self.conn.commit()
        return item_id

    # updates item last_seen in database
    def update_last_seen(self, id: int):
        sql = f"UPDATE `data` SET `last_seen` = NOW() WHERE `data`.`id` = {id};"
        self.cursor.execute(sql)
        self.conn.commit()

    def duplicates_process(self, item) -> bool:
        # 1. check if url in item matches in database

        item_id = self.duplicates_checker(item['link'])

        if item_id == 0:
            return True
        else:
            print('duplicate found')
            self.update_last_seen(item_id)
            return False

        # 1.1 if true compare data to see if data needs to be updated in db
        # 2 Check if location and size matches in database
        # 2.1 if true send email with data for manual review

    # checks for duplicates in db and if none saves it.
    def process_item(self, item, spider):

        # if there are no duplicates save dave item to db
        if self.duplicates_process(item):
            sql = f"INSERT INTO `data` (`link`, `longitude`, `latitude`, `price`, `currency`, `size`, `property_type`, `price_type`, `first_seen`, `last_seen`) VALUES ('{item['link']}', '{item['location'][0]}', '{item['location'][1]}', '{item['price'][0]}', '{item['price'][1]}', '{item['size']}', '{item['property_type']}', '{item['price_type']}', '{item['time']}', '{item['time']}');"
            self.cursor.execute(sql)
            self.conn.commit()

            return item

    def close_spider(self, spider):
        self.conn.close()
