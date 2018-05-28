from scrapy.conf import settings
from urllib import urlencode
from scrapy import Request, FormRequest
import scrapy
import json
from datetime import timedelta, date


class SiteProductItem(scrapy.Item):
    Classic_Twin_Room = scrapy.Field()
    Single_Room = scrapy.Field()
    Superior_Double_Room = scrapy.Field()
    Classic_Double_Room = scrapy.Field()
    Family_Room = scrapy.Field()


class NewEvents (scrapy.Spider):

    name = "scrapingdata"
    allowed_domains = ['www.cloudbeds.com', 'hotels.cloudbeds.com']
    LOGIN_URL = 'https://hotels.cloudbeds.com/auth/login'
    CONTENT_API_URL = 'https://hotels.cloudbeds.com/hotel/get_content'

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
        data = {
            'lang': 'en',
            'property_id': client_id,
            'group_id': client_id,
            'version': 'https://static1.cloudbeds.com/myfrontdesk-front/initial-12.0/app.js.gz',
            'announcementsLast': ''
        }

        yield FormRequest(url=self.CONTENT_API_URL,
                          callback=self.parse_product,
                          headers=self.HEADERS,
                          method='POST',
                          formdata=data)

    def parse_product(self, response):
        data = json.loads(response.body_as_unicode())
        num_rooms = data['num_rooms']
        room_names = data['room_names']
        room_type_rates = data['room_type_rates']

        for room_type in room_type_rates:
            room_type_id = room_type['room_type_id']
            room_name_infos = room_names[room_type_id]

            for ro_info in room_name_infos:
                room_name = ro_info['name']
                for room_info in room_type['intervals']:
                    start_date = room_info['start_date']
                    end_date = room_info['end_date']
                    price_values = [value for key, value in room_info.items()
                                    if 'day_' in key.lower() and '_guests' not in key.lower()]
                    date_range = self.daterange(start_date, end_date)
                    for single_date in date_range:
                        index_single_date = single_date.indexOf(date_range)
                        each_price = price_values[index_single_date]

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

    def daterange(start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)



