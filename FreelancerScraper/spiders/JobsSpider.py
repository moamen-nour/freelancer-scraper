import scrapy
from urllib.parse import urlencode


class JobsSpider(scrapy.Spider):
    name = 'jobs'

    def start_requests(self):
        urls = []

        # send requests
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print('done')

