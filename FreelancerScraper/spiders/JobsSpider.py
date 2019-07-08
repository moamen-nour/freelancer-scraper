import scrapy
from urllib.parse import urlencode , urlparse
import pymongo
from pymongo import ReplaceOne

class JobsSpider(scrapy.Spider):
    name = 'jobs'

    def __init__(self):
        # Connect to db
        self.mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.jobs_collection = self.mongo_client['freelancer']['jobs']

    def start_requests(self):
        base_url = 'http://www.freelancer.com/jobs/1/?'

        # Constant query strings
        base_url += 'languages=en&status=all'

        # Available filters
        job_types = ['local','featured','recruiter','fulltime']
        budgets = ['fixed','hourly','contest']
        min_budget = 0
        max_budget = 1000 #for testing only target -> 1000000
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
        print(urls, file=open('urls.txt', 'w'))

        # Send requests
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
            break # for testing only

    def parse(self, response):
        # Extract data fields from page
        operations = []
        for job in response.css('div.JobSearchCard-item'):
            title = job.css('a.JobSearchCard-primary-heading-link::text').get().strip()
            description = job.css('p.JobSearchCard-primary-description::text').get().strip()
            skills = job.css('a.JobSearchCard-primary-tagsLink::text').getall()
            days_left = self.getDaysLeft(job.css('span.JobSearchCard-primary-heading-days::text').get().strip())
            bid = job.css('div.JobSearchCard-primary-price::text').get().strip()
            verified = True if job.css('div.JobSearchCard-primary-heading-status').get() else False

            # Create a dictionary
            document = {
                'title'       : title,
                'description' : description,
                'skills'      : skills,
                'days_left'   : days_left,
                'bid'         : bid,
                'verified'    : verified
            }

            # Add to array
            operations.append(ReplaceOne(document , document , upsert=True))

        # Bulk insert extracted data from page(avoiding insertion of duplicates)
        self.jobs_collection.bulk_write(operations)

        # Go to next page and repeat till finishing this filter
        next_page_relative_url = response.css('a.Pagination-item::attr(href)')[-2].get()
        if next_page_relative_url != urlparse(response.url).path:
            query_string = urlparse(response.url).query
            to_follow_url = next_page_relative_url + '?' + query_string
            yield response.follow(to_follow_url, callback=self.parse)

    def getDaysLeft(self, string):
        days = str.split(string)[0]
        return 0 if days == 'Ended' else int(days)

    def closed(self, reason):
        # Close mongoDB client
        self.mongo_client.close()
