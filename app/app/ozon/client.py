import requests
import re
import pandas as pd
from upload.ozon.response import Response


class OzonSellerClient:
    def __init__(self, api_key, client_id, host=r'api-seller.ozon.ru'):
        self.api_key = api_key
        self.client_id = client_id
        self.host = host
        self.headers = {
            'Host': host,
            'Client-Id': client_id,
            'Api-Key': api_key,
            'Content-Type': 'application/json'}

    def get_products(self, params=None, page_size=100):
        if params is None:
            params = {}
        method = r'/v2/product/list'
        scopes = r'https://' + self.host + method
        return self.get_product_data(scopes, params, page_size)

    def get_products_info(self, params=None, page_size=100) -> pd.DataFrame:
        if params is None:
            params = {}
        method = r'/v2/product/info'
        scopes = r'https://' + self.host + method
        return self.get_ozon_paged_data(scopes, params, page_size)

    def get_products_category(self, params=None, page_size=100) -> pd.DataFrame:
        if params is None:
            params = {}
        method = r'/v2/category/tree'
        scopes = r'https://' + self.host + method
        return self.get_ozon_paged_data(scopes, params, page_size)

    def get_products_category_attribute(self, params=None, page_size=100) -> pd.DataFrame:
        if params is None:
            params = {}
        method = r'/v3/category/attribute'
        scopes = r'https://' + self.host + method
        return self.get_ozon_paged_data(scopes, params, page_size)

    def post_product(self, params=None):
        if params is None:
            params = {}
        method = r'/v2/product/import'
        scopes = r'https://' + self.host + method
        resource = requests.post(scopes, json=params, headers=self.headers)
        print(resource.text)
        print(resource.status_code)
        return resource.json()

    def post_stocks(self, params=None):
        if params is None:
            params = {}
        method = r'/v2/products/stocks'
        scopes = r'https://' + self.host + method
        resource = requests.post(scopes, json=params, headers=self.headers)
        print(resource.text)
        print(resource.status_code)
        return resource.json()

    def post_prices(self, params=None):
        if params is None:
            params = {}
        method = r'/v1/product/import/prices'
        scopes = r'https://' + self.host + method
        resource = requests.post(scopes, json=params, headers=self.headers)
        print(resource.text)
        print(resource.status_code)
        return resource.json()

    def get_ozon_postings(self, start_date, end_date, offset_increment=1000):
        method = r'/v2/posting/fbo/list'
        scopes = r'https://' + self.host + method
        params = {'dir': 'asc',
                  'filter': {
                      'since': start_date,
                      'to': end_date
                  },
                  'limit': offset_increment,
                  'offset': "0",
                  "translit": True,
                  "with": {
                      "analytics_data": True,
                      "financial_data": True
                  }
                  }

        return self.post_ozon_offset_data(scopes, params, offset_increment)

    def get_self_postings(self, start_date, end_date, offset_increment=1000):
        method = r'/v3/posting/fbs/list'
        scopes = r'https://' + self.host + method
        params = {'dir': 'asc',
                  'filter': {
                      'since': start_date,
                      'to': end_date
                  },
                  'limit': offset_increment,
                  'offset': 0,
                  "translit": True,
                  "with": {
                      "analytics_data": True,
                      "financial_data": True
                  }
                  }

        return self.post_ozon_offset_data(scopes, params, offset_increment)

    def get_stocks(self, params=None, page_size=100):
        if params is None:
            params = {'page': 1}
        method = r'/v2/product/info/stocks'
        scopes = r'https://' + self.host + method
        return self.get_product_data(scopes, params, page_size)

    def get_transactions(self, start_date, end_date, page_size=500):
        method = r'/v2/finance/transaction/list'
        scopes = r'https://' + self.host + method
        params = {
            "filter": {
                "date": {
                    "from": start_date,
                    "to": end_date,
                },
                "transaction_type": "all"
            },
            "page": 1
        }

        return self.get_ozon_paged_data(scopes, params, page_size)

    def get_ozon_offset_data(self, scopes, params, offset_increment=50):
        params = params.copy()
        dataframe = pd.DataFrame()
        offset = 0
        result_len = 1

        while result_len > 0:
            print('[Log]: ', offset, ' rows loaded')
            raw_response = requests.get(scopes, json=params, headers=self.headers)
            response = Response(raw_response, body_key='result')
            data = response.get_results()

            if data is None:
                print('[Log]: Empty server response. Retrying.')
                continue

            dataframe = dataframe.append(pd.DataFrame(data))

            result_len = len(data)
            offset += offset_increment
            params['offset'] = str(offset)

        request_scopes = re.findall(r'\/v.?\/(.*)', scopes)[0]
        dataframe['request_scopes'] = request_scopes

        return dataframe

    def get_product_data(self, scopes, params, page_size=100):
        df = pd.DataFrame()
        params = params.copy()
        params['page_size'] = page_size
        result_len = params['page_size']
        page = 1

        while result_len == page_size:
            raw_response = requests.post(scopes, json=params, headers=self.headers)
            r = Response(raw_response, body_key='result')

            data = r.get_results()

            if data is None:
                print('[Log]: Empty server response. Retrying.')
                continue
            else:
                data = data['items']
            df = data

            result_len = len(r.get_results()['items'])
            page += 1
            params['page'] = str(page)

        return df

    def get_ozon_paged_data(self, scopes, params, page_size=100):
        df = pd.DataFrame()
        params = params.copy()
        params['page_size'] = page_size
        result_len = params['page_size']
        page = 1

        while result_len == page_size:
            raw_response = requests.post(scopes, json=params, headers=self.headers)
            r = Response(raw_response, body_key='result')
            df = r.get_results()
            if df is None:
                print('[Log]: Empty server response. Retrying.')
                continue

            result_len = len(r.get_results())
            page += 1
            params['page'] = str(page)

        return df

    def post_ozon_offset_data(self, scopes, params, offset_increment=1000):
        params = params.copy()
        dataframe = pd.DataFrame()
        offset = 0
        has_next = True

        while has_next:
            print('[Log]: ', offset, ' rows loaded')
            raw_response = requests.post(scopes, json=params, headers=self.headers)
            response = Response(raw_response, body_key='result')
            data = response.get_results()

            if data is None:
                print('[Log]: Empty server response. Retrying.')
                continue
            if len(data) == 0:
                break
            has_next = data['has_next']
            l = pd.DataFrame(data['postings'])
            dataframe = pd.concat([dataframe, l])
            offset += offset_increment
            params['offset'] = offset

        request_scopes = re.findall(r'\/v.?\/(.*)', scopes)[0]
        dataframe['request_scopes'] = request_scopes

        return dataframe

    def get_sum_transaction(self, id_order, start_date, end_date):
        method = r'/v3/finance/transaction/totals'
        scopes = r'https://' + self.host + method
        params = {
            "date": {
                "from": start_date,
                "to": end_date
            },
            "posting_number": str(id_order),
            "transaction_type": "all"
        }
        reqwest = requests.post(scopes, headers=self.headers, json=params)
        return reqwest

    def get_order(self, id_order):
        method = r'/v3/posting/fbs/get'
        scopes = r'https://' + self.host + method
        params = {
            "posting_number": str(id_order),
            "with": {
                "analytics_data": False,
                "barcodes": False,
                "financial_data": True,
                "product_exemplars": True,
                "translit": False
            }
        }
        reqwest = requests.post(scopes, headers=self.headers, json=params)
        return reqwest