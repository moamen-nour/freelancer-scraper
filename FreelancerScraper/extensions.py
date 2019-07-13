from scrapy import signals
from scrapy.exceptions import NotConfigured
from stem import Signal
from stem.control import Controller
import time
import requests
from requests.exceptions import RequestException


class IpChanger(object):

    def __init__(self, limit, tor_listening_port, control_password, proxies):
        self.limit = limit
        self.req_count = 0
        self.proxies = proxies
        self.controller = Controller.from_port(port=tor_listening_port)
        self.controller.authenticate(password=control_password)

    @classmethod
    def from_crawler(cls, crawler):
       
        if not crawler.settings.getbool('EXT_IP_CHANGER'):
            raise NotConfigured

        # Read needed values from settings module
        settings = crawler.settings
        proxies = {'http': settings.get('PRIVOXY_URL_HTTP'),
                    'https': settings.get('PRIVOXY_URL_HTTPS')}
        
        # Create instance
        ext = cls(settings.getint('EXT_IP_CHANGER_LIMIT'), settings.get('TOR_LISTENING_PORT'), settings.get('CONTROL_PASSWORD'), proxies)

        # Register to receive signal when downloader finishes downloading a request
        crawler.signals.connect(ext.update_req_count, signal=signals.response_downloaded)

        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)

        return ext

    def update_req_count(self, request, spider):
        self.req_count += 1
        if self.req_count == self.limit:
            # Reset counter and attempt to get a new ip
            self.req_count = 0

            # Allocate a new ip
            self.renew_tor_ip()

    # Gets current assigned ip
    def get_current_ip(self):
        try:
            # Send request to icanhazip.com to know my ip
            return requests.get('http://icanhazip.com/', proxies=self.proxies).text

        except RequestException as ex:
            print(ex.message)

    # Connects to Tor network using stem controller
    # and asks to assign a new ip
    def renew_tor_ip(self):
        current_ip = old_ip = self.get_current_ip()
        
        while(current_ip == old_ip):
            # Wait till tor can receive a new identity signal
            while(not self.controller.is_newnym_available()):
                time.sleep(self.controller.get_newnym_wait())
        
            # Request new identity
            self.controller.signal(Signal.NEWNYM)

            current_ip = self.get_current_ip()
        
        print ('Connected with IP: %s' % current_ip)


    def spider_closed(self, spider):
        self.controller.close()