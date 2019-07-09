# Defines the models of scraped items

import scrapy

# Defines a scraped item by the Freelancer scraper
class JobItem(scrapy.Item):
    title = scrapy.Field()
    description = scrapy.Field()
    skills = scrapy.Field()
    remaining_time = scrapy.Field()
    bid = scrapy.Field()
    verified = scrapy.Field()