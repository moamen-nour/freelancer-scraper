import scrapy
from FreelancerScraper.items import JobItem
from FreelancerScraper.itemloaders import JobLoader
from urllib.parse import urlencode , urlparse
import random

class JobsSpider(scrapy.Spider):
    name = 'jobs'

    def start_requests(self):
        base_url = 'https://www.freelancer.com/jobs/?'

        # Constant query strings
        base_url += 'languages=en&status=all'

        # Available filters
        job_types = ['local','featured','recruiter','fulltime']
        budgets = ['fixed','hourly','contest']
        min_budget = 0
        max_budget = 1000000 #for testing only target -> 1000000
        step = 1000
        
        # Create urls with query strings combinations
        urls = []
        for job_type in job_types:
            for budget in budgets:
                # Add job type and buget filters to QS
                query_string = {
                    job_type : 'true',
                    budget : 'true'
                }

                # Ranges for budget
                if budget == 'fixed':
                    for i in range(min_budget,max_budget,step):
                        query_string['fixed_min'] = i
                        query_string['fixed_max'] = i + step
                        urls.append(base_url + '&' + urlencode(query_string))
                elif budget == 'hourly':
                    for i in range(min_budget,max_budget,step):
                        query_string['hourly_min'] = i
                        query_string['hourly_max'] = i + step
                        for j in range(1,5):
                            query_string['hourly_duration'] = j
                            urls.append(base_url + '&' + urlencode(query_string))
                else:
                    for i in range(min_budget,max_budget,step):
                        query_string['contest_min'] = i
                        query_string['contest_max'] = i + step
                        urls.append(base_url + '&' +urlencode(query_string))

        # Save urls to external file
        # print(urls, file=open('urls.txt', 'w'))

        # Shuffle and schedule requests
        # random.shuffle(urls)
        for url in urls:
            # Request passes through local proxy
            yield scrapy.Request(url=url, callback=self.parse, meta={'proxy':self.settings.get('PRIVOXY_URL')})
            # break # for testing only
        # for i in range(10000):
        #     yield scrapy.Request(url='http://icanhazip.com/', callback=self.parse, meta={'proxy':self.settings.get('PRIVOXY_URL')})


    def parse(self, response):
        # Extract data fields from page
        operations = []
        for job in response.css('div.JobSearchCard-item'):

            # Create a JobItem using JobLoader
            jobLoader = JobLoader(item=JobItem() , selector=job , response=response)
            jobLoader.add_css('title' , 'a.JobSearchCard-primary-heading-link::text')
            jobLoader.add_css('description' , 'p.JobSearchCard-primary-description::text')
            jobLoader.add_css('skills' , 'a.JobSearchCard-primary-tagsLink::text')
            jobLoader.add_css('remaining_time' , 'span.JobSearchCard-primary-heading-days::text')
            jobLoader.add_css('bid' , 'div.JobSearchCard-primary-price::text')
            jobLoader.add_css('verified' , 'div.JobSearchCard-primary-heading-status')

            yield jobLoader.load_item()
        

        # Go to next page and repeat till finishing this filter
        next_page_relative_url = response.css('a.Pagination-item::attr(href)')[-2].get()
        if next_page_relative_url != urlparse(response.url).path:
            query_string = urlparse(response.url).query
            to_follow_url = next_page_relative_url + '?' + query_string
            yield response.follow(to_follow_url, callback=self.parse)
        # print('$$$$$$$$$$$$ ' , response.text)
