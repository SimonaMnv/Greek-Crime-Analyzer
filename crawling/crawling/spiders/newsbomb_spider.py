import scrapy
# from crawling.crawling.items import ArticleItem
from scrapy.spiders import CrawlSpider


class NewsbombSpider(scrapy.Spider):
    name = 'newsbomb'
    allowed_domains = ['https://www.newsbomb.gr']
    start_urls = ['https://www.newsbomb.gr/ellada/astynomiko-reportaz']

    def parse(self, response):
        article_links = response.css('.item-title a ::attr(href)')
        next_page = int(response.css("span.nav-number::text").get()) + 1

        for link in article_links:
            url = link.get()
            if url:
                yield response.follow(url=url, callback=self.parse_article)
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def parse_article(self, response):
        title = response.css('h1::text').get()

        yield {
            'Title': title
        }

# 1. to scrape: go in crawling>crawling: scrapy crawl newsbomb
# 2. to check the html manually before parsing: scrapy shell > fetch(site) > print(response.text)

# headline, date, body = response.xpath("//script[contains(., 'articleBody')]/text()").extract()
# tags = response.xpath("//meta[@name='keywords']/@content")[0].extract()
