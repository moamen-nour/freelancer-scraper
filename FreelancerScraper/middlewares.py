from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
import json

# Define here the models for your spider middleware

class FreelancerscraperSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


# Define here the models for your downloader middleware

class RotatingUserAgents(UserAgentMiddleware):
    def __init__(self, user_agent='Scrapy',  ua_file_path=''):
        super(RotatingUserAgents, self).__init__()
        self.user_agent = user_agent
        self.ua_file_path = ua_file_path
    
    @classmethod
    def from_crawler(cls, crawler):

        o = cls(crawler.settings['USER_AGENT'], crawler.settings.get('UA_FILE_PATH'))
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def process_request(self, request, spider):
        ua = self.ua_file.readline()
        if ua == '':
            self.ua_file.seek(0)
            ua = self.ua_file.readline()

        request.headers.setdefault('User-Agent', ua)

    def spider_opened(self, spider):
        self.ua_file = open(self.ua_file_path,'r')

    def spider_closed(self, spider):
        self.ua_file.close()