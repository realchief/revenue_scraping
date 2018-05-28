from scrapy.conf import settings
from urllib import urlencode
from scrapy import Request, FormRequest
import scrapy


class SiteProductItem(scrapy.Item):
    Classic_Twin_Room = scrapy.Field()
    Single_Room = scrapy.Field()
    Superior_Double_Room = scrapy.Field()
    Classic_Double_Room = scrapy.Field()
    Family_Room = scrapy.Field()


class NewEvents (scrapy.Spider):

    name = "scrapingdata"
    allowed_domains = ['www.cloudbeds.com']
    LOGIN_URL = 'https://hotels.cloudbeds.com/auth/login'

    FORM_DATA = {
        'email': 'ari1601@hotmail.com',
        'password': 'Cloudbeds@22'
    }

    HEADERS = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36'
    }

    settings.overrides['ROBOTSTXT_OBEY'] = False

    def start_requests(self):
        yield FormRequest(url=self.LOGIN_URL,
                          callback=self.after_login,
                          headers=self.HEADERS,
                          method='POST',
                          formdata=self.FORM_DATA)

    def after_login(self, response):
        client_id = response.url.split('/')[-1]
        API_URL = 'https://hotels.cloudbeds.com/connect_data/' + client_id
        yield Request(url=API_URL,
                      callback=self.parse_product,
                      dont_filter=True
                      )

    def parse_product(self, response):

        prod_item = SiteProductItem()
        prod_item['container_num'] = self._parse_ContainerNumber(response)

        if any(value for value in prod_item.values()):
            return prod_item


    @staticmethod
    def _parse_ContainerNumber(response):
        try:
            ContainerNumber = response.xpath('//table[@width="95%"][3]/tr[3]/td[1]//text()').extract()
            if ContainerNumber:
                ContainerNumber = str(ContainerNumber[0])
            if not ContainerNumber and response.xpath('//td[@class="bor_L_none"]/a/font/u//text()'):
                ContainerNumber = str(response.xpath('//td[@class="bor_L_none"]/a/font/u//text()')[0].extract())
            if not ContainerNumber and response.xpath('//span[@class="tracking_container_id"]//text()'):
                ContainerNumber = str(response.xpath('//span[@class="tracking_container_id"]//text()')[0].extract())
            if not ContainerNumber and response.xpath('//tr[@class="field_odd"]//text()').extract():
                ContainerNumber = str(response.xpath('//tr[@class="field_odd"]//text()').extract()[3])
            return ContainerNumber if ContainerNumber else None
        except Exception as e:
            print('No Data')



