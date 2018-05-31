from scrapy.conf import settings
from urllib import urlencode
from scrapy import Request, FormRequest
import scrapy
import json
import csv
from datetime import timedelta, date, datetime


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
        total_source_list = []
        total_source_data = {}

        for room_type in room_type_rates:
            room_type_id = room_type['room_type_id']
            room_name_infos = room_names[room_type_id]

            for ro_info in room_name_infos:
                room_name = ro_info['name']
                for room_info in room_type['intervals']:
                    start_date = room_info['start_date']
                    start_date = start_date.split('-')
                    start_year = int(start_date[0])
                    start_month = int(start_date[1])
                    start_day = int(start_date[2])
                    start_date = date(start_year, start_month, start_day)

                    end_date = room_info['end_date']
                    end_date = end_date.split('-')
                    end_year = int(end_date[0])
                    end_month = int(end_date[1])
                    end_day = int(end_date[2])
                    end_date = date(end_year, end_month, end_day)
                    price_values = [value for key, value in room_info.items()
                                    if 'day_' in key.lower() and '_guests' not in key.lower()]

                    date_range = self.daterange(start_date, end_date)
                    date_list = []
                    for single_date in date_range:
                        date_list.append(single_date)
                    for s_date in date_list:
                        index_single_date = date_list.index(s_date)
                        day_index = index_single_date % 7
                        each_price = price_values[day_index]
                        total_source_data.update({s_date: each_price})
            total_source_list.append(total_source_data)

        with open('output.csv', 'wb') as out_csv:
            writer = csv.writer(out_csv)
            writer.writerow(["Client ID", "", "", "Inventory"])
            writer.writerow(["", "", "", "", "DQ", "DK"])
            writer.writerow(["year", "month", "day", "ALL",
                             room_type_rates[0]['room_type_id'], room_type_rates[1]['room_type_id']])

    def daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)



