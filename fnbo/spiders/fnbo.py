import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from fnbo.items import Article
import requests
import json


class fnboSpider(scrapy.Spider):
    name = 'fnbo'
    start_urls = ['https://www.fnbo.com/insights/archive/newsroom/']

    def parse(self, response):
        articles = json.loads(
            requests.get('https://www.fnbo.com/ajax/articles/index.jsp?category=Newsroom,Community%20Newsroom').text)
        for article in articles:
            link = response.urljoin(article['article-path'])
            date = article["article-date"]
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//span[@class="text-item"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
