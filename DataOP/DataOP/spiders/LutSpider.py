from datetime import datetime
import scrapy


class LutSpider(scrapy.Spider):
    name = "lut"
    start_urls = [
        'https://www.lut.com.br/todos-leiloes-online/0/2/3/127'
    ]

    # Parse link of all auctions
    def parse(self, response):
        auctions = response.xpath('/html/body/main/div/section/ul/li/a/@href').getall()
        print(len(auctions))
        for auction_href in auctions:
            auction_link = response.urljoin(auction_href)
            print(auction_href)
            yield scrapy.Request(auction_link, callback=self.parse_auction)

        next_page = response.xpath("//a[@rel='next']/@href").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    # Parse all lots from an auction
    def parse_auction(self, response):
        xpath = "//*[contains(@href,'/lote') and @class = 'btn-default']/@href"
        for lot_href in response.xpath(xpath).getall():
            lot_link = response.urljoin(lot_href)
            print(lot_href)
            yield scrapy.Request(lot_link, callback=self.parse_lot)

        next_page = response.xpath("//a[@rel='next']/@href").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse_auction)

    # Parse lot info
    def parse_lot(self, response):
        yield {
            'title': response.xpath('//*[@id="desc0"]/text()').get().strip(),
            'bid': response.xpath('//*[@id="lance0"]/text()').get().strip(),
            'opening': response.xpath('/html/body/main/div/section[1]/div[2]/p[2]/time/text()').get().strip(),
            'ending' : response.xpath("//time[@id='endDate0']/text()").get().strip(),
            'extract_dt' : datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
