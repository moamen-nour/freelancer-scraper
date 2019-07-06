import scrapy
from urllib.parse import urlencode


class JobsSpider(scrapy.Spider):
    name = 'jobs'

    def start_requests(self):
        base_url = 'http://www.freelancer.com/jobs/1/?'

        # constant query strings
        base_url += 'languages=en&status=all'

        # available filters
        job_types = ['local','featured','recruiter','fulltime']
        budgets = ['fixed','hourly','contest']
        min_budget = 0
        max_budget = 1000 #for testing only target -> 1000000
        step = 1000
        
        # create urls with query strings combinations
        urls = []
        for job_type in job_types:
            for budget in budgets:
                # add job type and buget filters to QS
                query_string = {
                    job_type : 'true',
                    budget : 'true'
                }

                # ranges for budget
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

        # save urls to external file
        print(urls, file=open('urls.txt', 'w'))

        # send requests
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print('done')

