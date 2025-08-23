# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import scrapy.item


class EmagCrawlersItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class MouseItem(scrapy.Item):
    name = scrapy.Field()
    brand = scrapy.Field()
    URL = scrapy.Field()
    price = scrapy.Field()
    tip = scrapy.Field()
    interfata_mouse = scrapy.Field()
    interfata_receiver = scrapy.Field()
    tehnologie = scrapy.Field()
    culoare = scrapy.Field()