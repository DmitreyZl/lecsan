import ftplib
import os
from datetime import datetime
from io import BytesIO
import requests
import pandas as pd
from dateutil.relativedelta import relativedelta
from app.app.models import Order1, Delivery6, OrdersYM, OrdersOzon, Vendor1, Transport, Module, ImportProvider1, \
    Rule3, Profile1
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Max


def add_orders(request):
    if request.method != "POST":
        return JsonResponse({'status': 'Method Not Allowed'}, status=405)
    flo = BytesIO()
    ftp = ftplib.FTP()
    ftp.connect(os.environ.get("ftp_host"), int(os.environ.get("ftp_port")))
    ftp.login(os.environ.get("ftp_user"), os.environ.get("ftp_password"))
    ftp.retrbinary('RETR ' + '/www/ftph911250377.nichost.ru/Documents1C.xml', flo.write)
    flo.seek(0)
    df = pd.read_xml(flo)
    for index, row in df.iterrows():
        if not Order1.objects.filter(number_id=row['DocNum']).exists():
            s = Order1(row['DocNum'], row['Date'], row['CustCostTotalAmount'],
                       '', '', row['Manager'], '', 'Не обработан')
            s.save()
    return JsonResponse({'status': 'OK'}, status=200)


def update(request):
    if request.method != "POST":
        return JsonResponse({'status': 'Method Not Allowed'}, status=405)
    if Delivery6.objects.filter(number_id=request.GET.get('number', 0)).exists():
        query = Delivery6.objects.get(number_id=request.GET.get('number', 0))
        query.sum = request.GET.get('money', 0)
        query.date = request.GET.get('date', 0)
        if request.GET.get('type', 0) != 0:
            query.type = request.GET.get('type', 0)
        query.driver = request.GET.get('driver', 0)
        query.status = request.GET.get('status', 0)
        query.comment = request.GET.get('comment', 0)
        if request.GET.get('status_pay', 0) != 0:
            query.status_pay = request.GET.get('status_pay', 0)
        if request.GET.get('manager', 0) != 0:
            query.manager = request.GET.get('manager', 0)
        query.save()
    else:
        money = request.GET.get('money', 0)
        date = request.GET.get('date', 0)
        delivery = request.GET.get('type', 0)
        driver = request.GET.get('driver', 0)
        status = request.GET.get('status', 0)
        comment = request.GET.get('comment', 0)
        status_pay = request.GET.get('status_pay', 0)
        manager = request.GET.get('manager', 0)
        s = Delivery6(request.GET.get('number', 0), date, delivery, money, status, comment, driver, status_pay,
                      manager)
        s.save()
    return JsonResponse({'status': 'OK'}, status=200)


def update_order(request):
    if request.method != "POST":
        return JsonResponse({'status': 'Method Not Allowed'}, status=405)
    if Order1.objects.filter(number_id=request.GET.get('number', '')).exists():
        Order1.objects.filter(number_id=request.GET.get('number', '')).update(date=request.GET.get('date', ''),
                                                                              sum=request.GET.get('summa', ''),
                                                                              type_payment=request.GET.get(
                                                                                  'type_payment', ''),
                                                                              sum_payment=request.GET.get(
                                                                                  'money', ''),
                                                                              manager=request.GET.get('manager',
                                                                                                      ''),
                                                                              status=request.GET.get('status',
                                                                                                     ''),
                                                                              status_obr=request.GET.get(
                                                                                  'status_obr', ''))
    else:
        s = Order1(request.GET.get('number', ''), request.GET.get('date', ''), request.GET.get('summa', ''),
                   request.GET.get('type_payment', ''), request.GET.get('money', ''),
                   request.GET.get('manager', ''), request.GET.get('status', ''),
                   request.GET.get('status_obr', ''))
        s.save()
    return JsonResponse({'status': 'OK'}, status=200)


def add_ym_orders(request):
    if request.method != "POST":
        return JsonResponse({'status': 'Method Not Allowed'}, status=405)
    r = requests.get('https://api.partner.market.yandex.ru/v2/campaigns/21641914/orders.json',
                     {'page': 1},
                     headers={
                         'Authorization': f'OAuth oauth_token="{os.environ.get("yandex_token")}", oauth_client_id="{os.environ.get("yandex_id")}"'})
    r = r.json()
    orders = r.get("orders")
    while r.get('pager').get("currentPage") < r.get('pager').get("pagesCount"):
        page = r.get('pager').get("currentPage") + 1
        r = requests.get('https://api.partner.market.yandex.ru/v2/campaigns/21641914/orders.json',
                         {'page': page},
                         headers={
                             'Authorization': f'OAuth oauth_token="{os.environ.get("yandex_token")}", oauth_client_id="{os.environ.get("yandex_id")}"'})
        r = r.json()
        orders += r.get("orders")
    for order in orders:
        report = requests.post(
            f"https://api.partner.market.yandex.ru/v2/campaigns/21641914/stats/orders.json?limit=200",
            json={"orders": [str(order['id'])]},
            headers={
                'Authorization': f'OAuth oauth_token="{os.environ.get("yandex_token")}", oauth_client_id="{os.environ.get("yandex_id")}"'})
        report = report.json()
        report_orders = report.get("result").get("orders")
        commissions = report_orders[0].get('commissions')
        sum_commissions = 0
        for commission in commissions:
            sum_commissions += float(commission.get('actual', 0))
        items_name = ''
        for item in order['items']:
            items_name += item['offerName'] + ', количество - ' + str(item['count']) + ', цена - ' + str(
                item['price']) + ' \n'
        if OrdersYM.objects.filter(number_id=str(order['id'])).exists():
            query = OrdersYM.objects.get(number_id=str(order['id']))
            query.status = order['status']
            query.substatus = order['substatus']
            query.commission = sum_commissions
            query.items_total = order['itemsTotal']
            query.total = order['total']
            query.items = items_name
            query.save()
        else:
            s = OrdersYM(order['id'], order['creationDate'], order['status'],
                         order['substatus'], sum_commissions,
                         order['itemsTotal'], order['total'], items_name)
            s.save()
    return JsonResponse({'status': 'OK'}, status=200)


def add_ozon_orders(request):
    if request.method != "POST":
        return JsonResponse({'status': 'Method Not Allowed'}, status=405)
    from app.app.ozon.client import OzonSellerClient
    client_id = request.GET.get('client_id', '258')
    if client_id == '258':
        client = OzonSellerClient(os.environ.get("ozon_api_key"), '258', 'api-seller.ozon.ru')
    else:
        client = OzonSellerClient(os.environ.get("ozon_api_key1"), '12712', 'api-seller.ozon.ru')
    today = datetime.today() + relativedelta(days=1)
    res = client.get_self_postings('2023-01-01T00:00:00.000Z', f'{str(today.date())}T00:00:00.000Z')
    for index, order in res.iterrows():
        items_name = ''
        commission_amount, total_discount_value, price = 0.0, 0.0, 0.0
        for item in order['products']:
            items_name += item['name'] + ', количество - ' + str(item['quantity']) + ', цена - ' + str(
                item['price']) + ' \n'
        for item in order['financial_data']['products']:
            price += item['price']
            total_discount_value += item['total_discount_value']
        res = client.get_sum_transaction(order['posting_number'], '2023-01-01T00:00:00.000Z',
                                         f'{str(today.date())}T00:00:00.000Z')
        commission_amount = sum_commission_ozon(res)
        if OrdersOzon.objects.filter(number_id=str(order['posting_number'])).exists():
            query = OrdersOzon.objects.get(number_id=str(order['posting_number']))
            query.status = order['status']
            query.substatus = order['substatus']
            query.discount_total = total_discount_value
            query.commission_amount = commission_amount
            query.total = price
            query.items = items_name
            query.save()
        else:
            s = OrdersOzon(str(order['posting_number']), str(client_id), order['in_process_at'], order['status'],
                           order['substatus'], total_discount_value, commission_amount, price, items_name)
            s.save()
    return JsonResponse({'status': 'OK'}, status=200)


def sum_commission_ozon(response):
    if response.status_code == 200:
        res = response.json()
        sum_commission = res['result'].get('sale_commission') + res['result'].get('processing_and_delivery') + \
                         res['result'].get('refunds_and_cancellations') + \
                         res['result'].get('services_amount') + res['result'].get('compensation_amount') + \
                         res['result'].get('money_transfer') + res['result'].get('others_amount')
        return sum_commission
    else:
        return 0


def add_vendor(request):
    if request.method != "POST":
        return JsonResponse({'status': 'Method Not Allowed'}, status=405)
    s = Vendor1(request.GET.get('name', 0), request.GET.get('transport', 0),
                str(request.GET.get('file_name', 0)),
                request.GET.get('last_import', 0), request.GET.get('status', 0), '')
    s.save()
    if not Transport.objects.filter(name=request.GET.get('transport', 0)).exists():
        t = Transport(request.GET.get('transport', 'None'), '', '', '', '', '', '', )
        t.save()
    return JsonResponse({'status': 'OK'}, status=200)


def update_vendor(request):
    if request.method != "POST":
        return JsonResponse({'status': 'Method Not Allowed'}, status=405)
    query = Vendor1.objects.filter(name=str(request.GET.get('name', 0))).get()
    query.transport = request.GET.get('transport', 0)
    query.file_name = str(request.GET.get('file_name', 0))
    query.last_import = request.GET.get('last_import', 0)
    query.active = request.GET.get('status', 0)
    query.save()
    return JsonResponse({'status': 'OK'}, status=200)


def delete_vendor(request):
    if request.method != "POST":
        return JsonResponse({'status': 'Method Not Allowed'}, status=405)
    Vendor1.objects.get(name=str(request.GET.get('name', 0))).delete()
    return JsonResponse({'status': 'OK'}, status=200)


def add_module(request):
    if request.method != "POST":
        return JsonResponse({'status': 'Method Not Allowed'}, status=405)
    s = Module(request.GET.get('name', 0), request.GET.get('host', 0), request.GET.get('apikey', 0))
    s.save()
    return JsonResponse({'status': 'OK'}, status=200)


def update_module(request):
    if request.method != "POST":
        return JsonResponse({'status': 'Method Not Allowed'}, status=405)
    query_site = Module.objects.filter(name=request.GET.get('name', 0)).get()
    query_site.host = request.GET.get('client_id', 0)
    query_site.api_key = request.GET.get('api_key', 0)
    query_site.save()
    return JsonResponse({'status': 'OK'}, status=200)


def delete_profile(request):
    if request.method != "POST":
        return JsonResponse({'status': 'Method Not Allowed'}, status=405)
    Profile1.objects.filter(name=request.GET.get('name', 0)).delete()
    return JsonResponse({'status': 'OK'}, status=200)


@csrf_exempt
def add_user(request):
    if request.method != "POST":
        return JsonResponse({'status': 'Method Not Allowed'}, status=405)
    User.objects.create_user("admin", "admin@boint.com", "nimda")
    return JsonResponse({'status': 'OK'}, status=200)


@csrf_exempt
def add_modules(request):
    if request.method != "POST":
        return JsonResponse({'status': 'Method Not Allowed'}, status=405)
    s = ImportProvider1('1', "test", "", "")
    s.save()
    return JsonResponse({'status': 'OK'}, status=200)


def update_profile(request):
    if request.method != "POST":
        return JsonResponse({'status': 'Method Not Allowed'}, status=405)
    if not Profile1.objects.filter(name=request.GET.get('name', 0)).exists():
        s = Profile1(request.GET.get('name', 0), request.GET.get('module', 0), request.GET.get('category', 0),
                     request.GET.get('character', 0), request.GET.get('active', 0), request.GET.get('cron', 0),
                     request.GET.get('site', 0))
        s.save()
    else:
        query = Profile1.objects.filter(name=request.GET.get('name', 0)).get()
        query.name = request.GET.get('name', 0)
        query.module = request.GET.get('module', 0)
        query.categor = request.GET.get('category', 0)
        query.character = request.GET.get('character', 0)
        query.active = request.GET.get('active', 0)
        query.cron = request.GET.get('cron', 0)
        query.site = request.GET.get('site', 0)
        query.save()
    return JsonResponse({'status': 'OK'}, status=200)


def add_rule(request):
    if request.method != "POST":
        return JsonResponse({'status': 'Method Not Allowed'}, status=405)
    result = Rule3.objects.aggregate(Max('id_rule'))
    if result is None:
        result = 0
    s = Rule3(int(result['rating__max']) + 1, request.GET.get('story', 0), request.GET.get('vendor', 0),
              request.GET.get('vendor_site', 0), request.GET.get('section', 0),
              request.GET.get('type', 0), request.GET.get('cb', 0),
              request.GET.get('margin', 0), request.GET.get('type_margin', 0),
              request.GET.get('add_summ', '0.0'))
    s.save()
    return JsonResponse({'status': 'OK'}, status=200)


def update_rule(request):
    if request.method != "POST":
        return JsonResponse({'status': 'Method Not Allowed'}, status=405)
    query = Rule3.objects.filter(id_rule=request.GET.get('id', 0)).get()
    query.story = request.GET.get('story', 0)
    query.vendor = request.GET.get('vendor', 0)
    query.vendor_site = request.GET.get('vendor_site', 0)
    query.section = request.GET.get('section', 0)
    query.type = request.GET.get('type', 0)
    query.cb = request.GET.get('cb', 0)
    query.margin = request.GET.get('margin', 0)
    query.type_margin = request.GET.get('type_margin', 0)
    query.add_summ = request.GET.get('add_summ', '0.0')
    query.save()
    return JsonResponse({'status': 'OK'}, status=200)


def delete_rule(request):
    if request.method != "POST":
        return JsonResponse({'status': 'Method Not Allowed'}, status=405)
    Rule3.objects.filter(Rule3.id_rule == str(request.GET.get('id', 0))).delete()
    return JsonResponse({'status': 'OK'}, status=200)
