from pkgutil import get_data
import scrapy
from scrapy_splash import SplashRequest


class QuotesJsSpider(scrapy.Spider):
    name = 'quotes-js'
    custom_settings = {
        'RETRY_TIMES': 10,
    }

    def __init__(self, *args, **kwargs):
        # to be able to load the Lua script on Scrapy Cloud, make sure your
        # project's setup.py file contains the "package_data" setting, similar
        # to this project's setup.py
        self.LUA_SOURCE = get_data(
            'splash_scrapy_spm_headless_proxy_example', 'scripts/smart_proxy_manager.lua'
        ).decode('utf-8')
        super(QuotesJsSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        yield SplashRequest(
            url='http://quotes.toscrape.com/js/',
            endpoint='execute',
            args={
                'lua_source': self.LUA_SOURCE,
                'timeout': 60,
            },
            # tell Splash to cache the lua script, to avoid sending it for every request
            cache_args=['lua_source'],
            meta={
                'max_retry_times': 10,
            }
        )

    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').extract_first(),
                'author': quote.css('span small::text').extract_first(),
                'tags': quote.css('div.tags a.tag::text').extract(),
            }
        next_page = response.css('li.next > a::attr(href)').extract_first()
        if next_page:
            yield SplashRequest(
                url=response.urljoin(next_page),
                endpoint='execute',
                args={'lua_source': self.LUA_SOURCE},
                cache_args=['lua_source'],
            )
