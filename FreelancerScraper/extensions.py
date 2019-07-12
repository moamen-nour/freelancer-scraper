from scrapy.signals import response_downloaded
from scrapy.exceptions import NotConfigured
from stem import Signal
from stem.control import Controller
import time
import requests
from requests.exceptions import RequestException


class DownloaderRequestCounter(object):

    def __init__(self, limit, tor_listening_port, control_password, proxies):
        self.limit = limit
        self.req_count = 0
        self.new_ip = '0.0.0.0'
        self.old_ip = '0.0.0.0'
        self.proxies = proxies
        self.controller = Controller.from_port(port=tor_listening_port)
        self.controller.authenticate(password=control_password)

    @classmethod
    def from_crawler(cls, crawler):
       
        if not crawler.settings.getbool('EXT_REQ_COUNTER'):
            raise NotConfigured

        # Read needed values from settings module
        settings = crawler.settings
        proxies = {'https': settings.get('PRIVOXY_URL')}
        
        # Create instance
        ext = cls(settings.getint('EXT_REQ_COUNTER_LIMIT'), settings.get('TOR_LISTENING_PORT'), settings.get('CONTROL_PASSWORD'), proxies)

        # Register to receive signal when downloader finishes downloading a request
        crawler.signals.connect(ext.update_req_count, signal=response_downloaded)

        return ext

    def update_req_count(self, request, spider):
        self.req_count += 1
        if self.req_count == self.limit:
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