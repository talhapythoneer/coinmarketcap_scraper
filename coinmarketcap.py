import scrapy
from scrapy.crawler import CrawlerProcess
from random import randrange

# you can use packetstream proxies if you want
proxyURL = 'yourHTTPProxy'

meta = {
    'proxy': proxyURL,
}


class CoinMarketCap(scrapy.Spider):
    name = "CoinMarketCap"

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'Data.csv',
        # 'CONCURRENT_REQUESTS': '1',
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
        'ROBOTSTXT_OBEY': False,
        'FEED_EXPORT_ENCODING': 'utf-8-sig'
    }

    def start_requests(self):
        for i in range(1, 100 + 1):
            yield scrapy.Request(url="https://coinmarketcap.com/?page=" + str(i),
                             callback=self.parse, dont_filter=True,
                             headers={
                                 'USER-AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                               "like Gecko) Chrome/81.0.4044.138 Safari/537.36",
                             },
                             meta=meta
                             )

    def parse(self, response):
        if response.status != 200:
            new_request = response.request.copy()
            new_request.dont_filter = True
            yield new_request
        else:
            coins = response.css("td > a.cmc-link::attr(href)").extract()
            coins = [coin.split("?")[0] for coin in coins]

            for company in coins:
                # company = "/currencies/helpico/"
                yield scrapy.Request(url="https://coinmarketcap.com" + company,
                                    callback=self.parse2, dont_filter=True,
                                    headers={
                                        'USER-AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                                    "like Gecko) Chrome/81.0.4044.138 Safari/537.36",
                                    },
                                    meta=meta
                                    )

    def parse2(self, response):
        if response.status != 200:
            new_request = response.request.copy()
            new_request.dont_filter = True
            yield new_request
        else:
            name = response.css("h2::text").extract_first()
            marketcap = response.css("div.statsValue::text").extract_first()
            watchlist = response.css("div.nameSection > div > div.namePill::text").extract()[-1]

            watchlist = watchlist.strip().split(" ")[1]

            price = response.css("div.priceValue > span::text").extract_first()
            if price:
                price = price.strip()

            yield {
                "Name": name,
                "Price": price,
                "MarketCap": marketcap,
                "Watchlist": watchlist
            }

process = CrawlerProcess()
process.crawl(CoinMarketCap)
process.start()
