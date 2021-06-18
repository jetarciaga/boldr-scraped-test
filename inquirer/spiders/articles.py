import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.exceptions import CloseSpider

import re
from datetime import datetime


class ArticlesSpider(CrawlSpider):
    name = 'articles'
    allowed_domains = ['newsinfo.inquirer.net']
    start_urls = ['https://newsinfo.inquirer.net/category/latest-stories']

    rules = (
        Rule(LinkExtractor(restrict_xpaths="//div[@id='ch-ls-head']/h2/a"), callback='parse_item', follow=True),
        Rule(LinkExtractor(restrict_xpaths="//div[@id='ch-more-news']/a[position() = last()]"))
    )

    def parse_item(self, response):
        date_extract = response.xpath("normalize-space(//div[@id='art_plat']/text()[position() = last()])").get()
        
        # extract date and time 
        time = re.search(r"(\d:\w+\s\w+)", date_extract).group()
        date = re.search(r"([A-Z][a-z]+\s\d+,\s\d+)", date_extract).group()

        # Convert string to datetime object
        curr_date = datetime.strptime(date, "%B %d, %Y")
        start_date = datetime(2021, 1, 1)
        end_date = datetime(2021, 5, 31)

        if curr_date >= start_date and curr_date <= end_date:            
            paragraphs = response.xpath("//div[@id='article_content']/div/p/text()").getall()
            paragraph = [words for words in paragraphs if not (words.startswith("/r") or words.startswith("The Inquirer"))]
            content = " ".join(paragraph)
                    
            yield {
                'title': response.xpath("//h1[@class='entry-title']/text()").get(),
                'author': response.xpath("//div[@id='art_author']/span/a/text()").get(),
                'date': time + ' ' + date,
                'content': content
            }
        elif curr_date < start_date:
            raise CloseSpider('All articles from given dates has been scraped successfully')
