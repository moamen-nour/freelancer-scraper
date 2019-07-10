from scrapy import signals
from stem import Signal
from stem.control import Controller
import time
import requests
from requests.exceptions import RequestException

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

class NewIpAllocator(object):

    def __init__(self, tor_listening_port, control_password, proxies):
        self.req_count = 0
        self.new_ip = '0.0.0.0'
        self.old_ip = '0.0.0.0'
        self.proxies = proxies
        self.controller = Controller.from_port(port=tor_listening_port)
        self.controller.authenticate(password=control_password)

    @classmethod
    def from_crawler(cls, crawler):
        # Read needed values from settings module
        settings = crawler.settings
        proxies = {
            'http': settings.get('PRIVOXY_URL'),
        }
        return cls(settings.get('TOR_LISTENING_PORT'), settings.get('CONTROL_PASSWORD'), proxies)

    # Here I try to allocate a new IP
    def process_request(self, request, spider):

        # If we already done 5 requests or if it is the first time get a new ip
        if(self.req_count == 5 or self.new_ip == '0.0.0.0'):
            # Reset counter and attempt to get a new ip
            self.req_count = 0

            # Allocate a new ip
            self.renew_tor_ip()
            self.get_current_ip()
            while self.new_ip == self.old_ip:# We got the same old ip so retry after 5 seconds
                print('Assigned old ip waiting...')
                time.sleep(5)
                
                self.renew_tor_ip()
                self.get_current_ip()

        # Inrement req_count
        self.req_count += 1
        
        return None # Pass request down through Downloader pipeline

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_closed(self, spider):
        self.controller.close()

    # Gets current assigned ip
    def get_current_ip(self):
        try:
            # Store old ip
            self.old_ip = self.new_ip 

            # Send request to icanhazip.com to know my ip
            self.new_ip = requests.get('http://icanhazip.com/',proxies=self.proxies).text

            # Display new ip
            print ('Connected with IP: %s' % self.new_ip)
            
        except RequestException as ex:
            print(ex.message)

    # Connects to Tor network using stem controller
    # and asks to assign a new ip
    def renew_tor_ip(self):
        self.controller.signal(Signal.NEWNYM)
    