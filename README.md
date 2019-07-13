# Freelancer Jobs Scraper

A Scrapy crawler that extract jobs from freelancer website

### Prerequisites
* [Scrapy](https://scrapy.org/download/) - Web scraping framework
* [Tor](https://2019.www.torproject.org/docs/debian.html.en) - For anonymous browsing via IP changing
* [Stem](https://stem.torproject.org/download.html) - Tor controller
* [Privoxy](https://www.privoxy.org/#DOWNLOAD) - To further hide your identity when communicating with Tor
* [Requests](https://2.python-requests.org/en/master/user/install/) - Used to send requests to identify new identity assigned by Tor
* [MongoDB](https://www.mongodb.com/download-center/community) - To store our jobs documents
* [PyMongo](https://api.mongodb.com/python/current/installation.html) - Python mongoDB driver

#### Tor configuration file
Open config file
```
sudo vim /etc/tor/torrc
```
Uncomment
```
# ControlPort 9051
# CookieAuthentication 1
# HashedControlPassword (Hashed password)
```
To hash a password
```
tor --hash-password my_password
```
Restart Tor
```
sudo /etc/init.d/tor restart
```
#### Privoxy configuration file
Open config file
```
sudo vim /etc/privoxy/config
```
Uncomment
```
#        forward-socks5t             /     127.0.0.1:9050 .
```
Restart Privoxy
```
sudo /etc/init.d/privoxy restart
```


### Running the Crawler

Clone repo
```
git clone https://gitlab.com/inetworks-ml-internship/avengers/freelancer-scraper
cd FreelancerScraper
```
Setup env variables
```
export CONTROL_PASSWORD=(your unhashed tor password)
export http_proxy=http://127.0.0.1:8118
export https_proxy=https://127.0.0.1:8118
```
Run the crawler
```
scrapy crawl jobs
```


