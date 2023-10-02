import ftplib
from datetime import date, datetime
from io import BytesIO
from django.http import HttpResponse
from django.template import loader
import json
import numpy
import pandas as pd
from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from app.models import Order1, Delivery6, Driver, OrdersOzon, OrdersYM, ImportProvider1, Rule3, Items, \
    ItemsProvider1, Vendor1, Module, Profile1
from django.utils.safestring import SafeString
from app.helper import ServerSideTable
from app.models_table import SERVERSIDE_TABLE_COLUMNS, SERVERSIDE_TABLE_VENDOR_COLUMNS, \
    SERVERSIDE_TABLE_ITEMS_COLUMNS, \
    SERVERSIDE_TABLE_SALE_ITEMS_COLUMNS, SERVERSIDE_TABLE_BOINT_ITEMS_COLUMNS

data, data_list, load_boint_items, data_items = [], [], [], []
config = {'EXPORT_SITE': {
    'boint': 'https://boint.ru/',
    'технолайн': 'https://xn--80ajngjdd3a2a.xn--p1ai/',
    'maunfeld.spb': 'https://maunfeld.spb.ru/'
}}


def select_models(request):
    return render(request, "user.html")


def my_view(request):
    try:
        flo = BytesIO()
        ftp = ftplib.FTP()
        ftp.connect('ftp.h911250377.nichost.ru', 21)
        ftp.login('h911250377_s', 'A6k3s9ss')
        ftp.retrbinary('RETR ' + '/www/ftph911250377.nichost.ru/Documents1C.xml', flo.write)
        flo.seek(0)
        df = pd.read_xml(flo)
        error = ''
    except Exception as e:
        error = e
        df = pd.DataFrame([], columns=['Date', 'CustCostTotalAmount'])
    df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y')
    day = datetime.today().replace(day=1).date()
    end_day = (datetime.today().replace(day=1) + relativedelta(months=+1)).date()
    f = df.loc[df['Date'] >= str(day)].loc[df['Date'] < str(end_day)]
    f['Date'] = f['Date'].dt.date
    f.sort_values(by='Date', inplace=True)
    data = dates()
    sum_cast = list(f['CustCostTotalAmount'].groupby(f['Date']).sum())
    sum_cast = [round(v, 3) for v in sum_cast]
    if len(sum_cast) != 0:
        sum_today = round(sum_cast[-1], 2)
    else:
        sum_today = 0
    template = loader.get_template('charts-apex-chart.html')
    context = {'sum_today': sum_today, 'data': data, 'sum': sum_cast,
               'sum_all': round(sum(sum_cast), 2), 'mean_day': round(numpy.mean(sum_cast), 2),
               'error': error}
    rendered_page = template.render(context, request)
    return HttpResponse(rendered_page)


def my_view_managers(request):
    try:
        flo = BytesIO()
        ftp = ftplib.FTP()
        ftp.connect('ftp.h911250377.nichost.ru', 21)
        ftp.login('h911250377_s', 'A6k3s9ss')
        ftp.retrbinary('RETR ' + '/www/ftph911250377.nichost.ru/Documents1C.xml', flo.write)
        flo.seek(0)
        df = pd.read_xml(flo)
        error = ''
    except Exception as e:
        error = e
        df = pd.DataFrame([], columns=['Date', 'Manager'])
    df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y')
    day = datetime.today().replace(day=1).date()
    end_day = (datetime.today().replace(day=1) + relativedelta(months=+1)).date()
    now_day = datetime.today().date()
    p = df.loc[df['Date'] == str(now_day)]
    f = df.loc[df['Date'] >= str(day)].loc[df['Date'] < str(end_day)]
    sum_cast = f.groupby(by=['Manager'], as_index=False).sum(numeric_only=True)
    sum_cast1 = p.groupby(by=['Manager'], as_index=False).sum(numeric_only=True)
    sum_cast_all = df.groupby(by=['Manager'], as_index=False).sum(numeric_only=True)
    f['Date'] = f['Date'].dt.date
    f.sort_values(by='Date', inplace=True)
    template = loader.get_template('charts-highcharts.html')
    context = {'mount': now_day.strftime("%B"), 'date': now_day, 'sum_cast_all': sum_cast_all.values.tolist(),
               'sum_cast': sum_cast.values.tolist(), 'sum_cast1': sum_cast1.values.tolist(),
               'error': error}
    rendered_page = template.render(context, request)
    return HttpResponse(rendered_page)


def my_orders(request):
    flo = BytesIO()
    ftp = ftplib.FTP()
    ftp.connect('ftp.h911250377.nichost.ru', 21)
    ftp.login('h911250377_s', 'A6k3s9ss')
    ftp.retrbinary('RETR ' + '/www/ftph911250377.nichost.ru/Documents1C.xml', flo.write)
    flo.seek(0)
    df = pd.read_xml(flo)
    df.loc[(df.Proveden == 'Да'), 'Proveden'] = 'Проведён'
    df.loc[(df.Proveden == 'Нет'), 'Proveden'] = 'Не проведён'
    df = df.sort_values(by='DocNum', ascending=True)
    status_obr, sum_payments, summa = [], [], []
    for index, row in df.iterrows():
        if Order1.objects.filter(number_id=row['DocNum']).exists():
            query = Order1.objects.get(number_id=row['DocNum'])
            if len(query.type_payment) != 0 and query.sum_payment != '-' and query.sum_payment != 'тест' and query.sum_payment != ' ':
                if float(query.sum_payment.replace(',', '.')) / float(query.sum.replace(',', '.')) == 1:
                    sum_payments.append('100')
                else:
                    sum_payments.append(
                        str(round(float(query.sum_payment.replace(',', '.')) / float(query.sum.replace(',', '.')),
                                  1) * 100))
            else:
                sum_payments.append('None')
            if Delivery6.objects.filter(number_id=row['DocNum']).exists():
                query1 = Delivery6.objects.get(number_id=row['DocNum'])
                if query1.sum != '':
                    summa.append(str(round(float(query1.sum.replace(',', '.')) / float(row['CustCostTotalAmount']),
                                           1) * 100))
                else:
                    summa.append('None')
            else:
                summa.append('None')
            status_obr.append(query.status_obr)
        else:
            if Delivery6.objects.filter(number_id=row['DocNum']).exists():
                query1 = Delivery6.objects.get(number_id=row['DocNum'])
                if query1.sum != '' and len(query1.status_pay) != 0:
                    summa.append(
                        str(round(float(query1.sum.replace(',', '.')) / float(row['CustCostTotalAmount']),
                                  1) * 100))
                else:
                    summa.append('None')
            else:
                summa.append('None')
            sum_payments.append('None')
            status_obr.append(' ')

    df['status_obr'] = status_obr
    df['sum_payments'] = sum_payments
    df['summa'] = summa
    template = loader.get_template('table-basic-table.html')
    context = {'df': df.values.tolist()}
    rendered_page = template.render(context, request)
    return HttpResponse(rendered_page)


def my_order(request):
    flo = BytesIO()
    ftp = ftplib.FTP()
    ftp.connect('ftp.h911250377.nichost.ru', 21)
    ftp.login('h911250377_s', 'A6k3s9ss')
    ftp.retrbinary('RETR ' + '/www/ftph911250377.nichost.ru/Documents1C.xml', flo.write)
    flo.seek(0)
    df = pd.read_xml(flo)
    df = df.loc[df['DocNum'] == request.GET['number']]
    flo1 = BytesIO()
    ftp1 = ftplib.FTP()
    ftp1.connect('ftp.h911250377.nichost.ru', 21)
    ftp1.login('h911250377_s', 'A6k3s9ss')
    ftp1.retrbinary('RETR ' + '/www/ftph911250377.nichost.ru/Logistik1C.xml', flo1.write)
    flo1.seek(0)
    dr = pd.read_xml(flo1)
    dr = dr.loc[dr['DocNum'] == request.GET['number']]
    df.loc[(df.Proveden == 'Да'), 'Proveden'] = 'Проведён'
    df.loc[(df.Proveden == 'Нет'), 'Proveden'] = 'Не проведён'
    dr.loc[(dr.Proveden == 'Да'), 'Proveden'] = 'Проведён'
    dr.loc[(dr.Proveden == 'Нет'), 'Proveden'] = 'Не проведён'
    sum, driver, typ, stat, comment, typ_paym, sum_pay, status_pay, status, status_obr = [], [], [], [], [], [], [], [], [], []
    for index, row in dr.iterrows():
        if Delivery6.objects.filter(number_id=row['DocNum']).exists():
            query = Delivery6.objects.get(number_id=row['DocNum'])
            sum.append(query.sum)
            stat.append(query.status)
            comment.append(query.comment)
            driver.append(query.driver)
            typ.append(query.type)
            status_pay.append(query.status_pay)
        else:
            sum.append(' ')
            stat.append(' ')
            comment.append(' ')
            driver.append(' ')
            typ.append(' ')
            status_pay.append(' ')

    for index, row in df.iterrows():
        if Order1.objects.filter(number_id=row['DocNum']).exists():
            query = Order1.objects.get(number_id=row['DocNum'])
            typ_paym.append(query.type_payment)
            sum_pay.append(query.sum_payment)
            status.append(query.status)
            status_obr.append(query.status_obr)
        else:
            typ_paym.append(' ')
            sum_pay.append(' ')
            status.append(row['Proveden'])
            status_obr.append(' ')

    dr['type'] = typ
    dr['sum'] = sum
    dr['driver'] = driver
    dr['stat'] = stat
    dr['comment'] = comment
    dr['status_pay'] = status_pay
    df['type_pay'] = typ_paym
    df['sum_pay'] = sum_pay
    df['status'] = status
    df['status_obr'] = status_obr
    dr['Date'] = dr['Date'].apply(format_date)
    drivers = [r._asdict() for r in Driver.objects.all()]
    item_descript, item_count, item_price = get_info_goods(request.GET['number'])
    goods = pd.DataFrame()
    flo2 = BytesIO()
    ftp2 = ftplib.FTP()
    ftp2.connect('ftp.h911250377.nichost.ru', 21)
    ftp2.login('h911250377_s', 'A6k3s9ss')
    ftp2.retrbinary('RETR ' + '/www/ftph911250377.nichost.ru/Goods1C.xml', flo2.write)
    flo2.seek(0)
    goog = pd.read_xml(flo2)
    vendor_price, marge, marge_proch = [], [], []
    for item in item_descript:
        w = goog[goog['Name'] == item]
        if len(w) != 0:
            price = float(item_price[item_descript.index(item)])
            v_price = round(float(w['Price']), 5)
            vendor_price.append(v_price)
            marge.append(round(price - v_price, 5))
            proch = round((1 - v_price / price) * 100, 5)
            marge_proch.append(proch)
        else:
            vendor_price.append(0)
            marge.append(0)
            marge_proch.append(0)
    goods['descript'] = item_descript
    goods['count'] = item_count
    goods['price'] = item_price
    goods['vendor_price'] = vendor_price
    goods['marge'] = marge
    goods['marge_proch'] = marge_proch
    itog = {'str': 'Итого:',
            'count': goods['count'].count(),
            'sum': round(goods['price'].sum(), 5),
            'sum_vendor': round(goods['vendor_price'].sum(), 5),
            'sum_marge': round(goods['marge'].sum(), 5),
            'sum_marge_proch': round((1 - goods['vendor_price'].sum() / goods['price'].sum()) * 100, 5)
            }
    template = loader.get_template('order.html')
    context = {'num': request.GET['number'], 'df': df.values.tolist(), 'dr': dr.values.tolist(),
               'goods': goods.values.tolist(), 'drivers': drivers,
               'itog': itog}
    rendered_page = template.render(context, request)
    return HttpResponse(rendered_page)


def dates():
    ls = []
    day = datetime.today().replace(day=1)
    end_day = datetime.today().replace(day=1) + relativedelta(months=+1)
    while day < end_day:
        ls.append(str(day.date()))
        day = day + relativedelta(days=+1)
    return ls


def format_date(d):
    try:
        return datetime.strptime(d, '%d.%m.%Y').strftime('%Y-%m-%d')
    except ValueError:
        return d


def get_info_goods(number):
    flo = BytesIO()
    ftp = ftplib.FTP()
    ftp.connect('ftp.h911250377.nichost.ru', 21)
    ftp.login('h911250377_s', 'A6k3s9ss')
    ftp.retrbinary('RETR ' + '/www/ftph911250377.nichost.ru/Documents1C.xml', flo.write)
    flo.seek(0)
    df = pd.read_xml(flo, xpath=".//GoodsInfo")

    flo1 = BytesIO()
    ftp1 = ftplib.FTP()
    ftp1.connect('ftp.h911250377.nichost.ru', 21)
    ftp1.login('h911250377_s', 'A6k3s9ss')
    ftp1.retrbinary('RETR ' + '/www/ftph911250377.nichost.ru/Documents1C.xml', flo1.write)
    flo1.seek(0)
    dr = pd.read_xml(flo1)
    index = dr.index[dr['DocNum'] == number].tolist()
    item_descript = list(df.loc[index]['GoodsDescription'])
    item_count = list(df.loc[index]['Quantity'])
    item_price = list(df.loc[index]['InvoicedCost'])
    return item_descript, item_count, item_price


def ozon_order(request):
    from ozon.client import OzonSellerClient
    today = datetime.today() + relativedelta(days=1)
    client_id = request.GET.get('client_id', '258')
    if client_id == '258':
        client = OzonSellerClient('f1a2ea3c-cf97-4373-9dd6-ca8492cb3879', '258', 'api-seller.ozon.ru')
    else:
        client = OzonSellerClient('4328a3e4-e0d4-4914-98d5-852e3d7170b1', '12712', 'api-seller.ozon.ru')
    query = [r._asdict() for r in OrdersOzon.objects.filter(number_id=request.GET.get('id', 0))]
    r = client.get_order(request.GET.get('id', 0))
    r = r.json().get("result")
    items = r.get('products')
    delivery = r.get('delivery_method')
    delivery.update({'delivering_date': r.get('delivering_date')})
    if r.get('customer') is not None and r.get('customer').get('address') is not None:
        delivery.update({'city': r.get('customer').get('address').get('address_tail')})
    report = client.get_sum_transaction(request.GET.get('id', 0), '2023-01-01T00:00:00.000Z',
                                        f'{str(today.date())}T00:00:00.000Z')
    report = report.json()
    report_orders = report.get("result")
    template = loader.get_template('order-ozon.html')
    context = {'dr': query, 'num': request.GET.get('id', 0),
               'delivery': [delivery], 'items': items, 'commissions': report_orders}
    rendered_page = template.render(context, request)
    return HttpResponse(rendered_page)


def ym_order(request):
    query = [r._asdict() for r in OrdersYM.objects.filter(number_id=request.GET.get('id', 0))]
    r = requests.get(
        f"https://api.partner.market.yandex.ru/v2/campaigns/21641914/orders/{request.GET.get('id', 0)}.json",
        headers={
            'Authorization': 'OAuth oauth_token="y0_AgAAAABBAG54AAkt9wAAAADc546hAtx0ij7mS1WvR2Euzk5TesblsPE", oauth_client_id="72476ae9013147a1b57b2a5983786170"'})
    r = r.json().get("order")
    items = r.get('items')
    delivery = r.get('delivery')
    report = requests.post(
        f"https://api.partner.market.yandex.ru/v2/campaigns/21641914/stats/orders.json?limit=200",
        json={"orders": [int(request.GET.get('id', 0))]},
        headers={
            'Authorization': 'OAuth oauth_token="y0_AgAAAABBAG54AAkt9wAAAADc546hAtx0ij7mS1WvR2Euzk5TesblsPE", oauth_client_id="72476ae9013147a1b57b2a5983786170"'})
    report = report.json()
    report_orders = report.get("result").get("orders")
    delivery_price = report.get("result").get("orders")[0].get("deliveryTotal")
    template = loader.get_template('order-ym.html')
    context = {'dr': query, 'num': request.GET.get('id', 0), 'delivery_price': delivery_price,
               'delivery': [delivery], 'items': items, 'commissions': report_orders[0].get('commissions')}
    rendered_page = template.render(context, request)
    return HttpResponse(rendered_page)


def ym_orders(request):
    query = [r._asdict() for r in OrdersYM.objects.all()]
    template = loader.get_template('table-orders-ym.html')
    context = {'dr': query}
    rendered_page = template.render(context, request)
    return HttpResponse(rendered_page)


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


def ozon_orders(request):
    client_id = request.GET.get('client_id', '258')
    query = [r._asdict() for r in OrdersOzon.objects.filter(client_id=client_id).all()]
    template = loader.get_template('table-orders-ozon.html')
    context = {'dr': query, 'client_id': client_id}
    rendered_page = template.render(context, request)
    return HttpResponse(rendered_page)


def statistics_items(request):
    data = [r._asdict() for r in ImportProvider1.objects.filter(site=request.GET.get('site', 'технолайн'))]
    template = loader.get_template('import_vendors_statistics.html')
    context = {'df': data, 'site': request.GET.get('site', 'boint')}
    rendered_page = template.render(context, request)
    return HttpResponse(rendered_page)


def my_items(request):
    if request.GET.get('name_item', 0) == 0:
        name_item = '-'
    else:
        name_item = request.GET.get('name_item', 0).replace('_', ' ')

    data = Items.objects.filter(story=request.GET.get('site', 'boint'))

    vendors = [r._asdict() for r in
               ItemsProvider1.objects.filter(id_site != '').filter(story=request.GET.get('site', 'boint'))]
    build_list = []
    global data_list
    data_list = []
    for v in vendors:
        if v['id_site'] not in build_list:
            dict_build = [r._asdict() for r in data.filter(id_site=v['id_site'])]
            if len(dict_build) == 0:
                continue
            dict_build[0].update({'vendor': str([v])})
            data_list = data_list + dict_build
            build_list.append(v['id_site'])
        else:
            b_vendor = data_list[build_list.index(v['id_site'])]
            old = eval(b_vendor['vendor'])
            old.append(str([v]))
            data_list[build_list.index(v['id_site'])].update({'vendor': str(old)})
    data_list = data_list + [r._asdict() for r in data.filter(not_(id_site.in_(build_list)))]
    vendors_list = [r._asdict() for r in Vendor1.objects.filter(active='Активен').all()]
    template = loader.get_template('items.html')
    context = {'vendors': vendors_list, 'name_item': name_item,
               'site': request.GET.get('site', 'boint'), 'id_item': request.GET.get('id_item', '-'),
               'brand_item': request.GET.get('brand_item', '-'),
               'section_item': request.GET.get('section_item', '-'),
               'article_item': request.GET.get('article_item', '-'),
               'price_item': request.GET.get('price_item', '-'), 'quantity_item': request.GET.get('quantity_item', '-'),
               'status_item': request.GET.get('status_item', '-'), 'vendor': request.GET.get('vendor', '-')}
    rendered_page = template.render(context, request)
    return HttpResponse(rendered_page)


def my_vendor_items(request):
    global data, data_items
    data, data_items = [], []
    data_items = [r._asdict() for r in Items.objects.filter(story=request.GET.get('site', 'boint')).all()]
    if request.GET.get('name_item', 0) == 0:
        name_item = '-'
    else:
        name_item = request.GET.get('name_item', 0).replace('_', ' ')
    data = [r._asdict() for r in
            ItemsProvider1.objects.filter(story=request.GET.get('site', 'boint')).filter(id_site='').all()]
    vendors = [r._asdict() for r in Vendor1.objects.filter(active='Активен').all()]
    template = loader.get_template('vendor_items.html')
    context = {'vendors': vendors, 'name_item': name_item,
               'site': request.GET.get('site', 'boint'),
               'brand': request.GET.get('brand', '-'),
               'article_item': request.GET.get('article_item', '-'),
               'price1': request.GET.get('price1', '-'), 'quantity1': request.GET.get('quantity1', '-'),
               'price_oc': request.GET.get('price_oc', '-')}
    rendered_page = template.render(context, request)
    return HttpResponse(rendered_page)


def wildberries_items(request):
    data = [r._asdict() for r in Items.objects.filter(story='wildberries').all()]
    global load_boint_items
    load_boint_items = [r._asdict() for r in Items.objects.filter(story='boint')]

    if request.GET.get('name_item', 0) == 0:
        name_item = '-'
    else:
        name_item = request.GET.get('name_item', 0).replace('_', ' ')
    template = loader.get_template('wildberries_items.html')
    context = {'df': data, 'name_item': name_item,
               'site': request.GET.get('site', 'boint'), 'id_item': request.GET.get('id_item', '-'),
               'brand_item': request.GET.get('brand_item', '-'),
               'section_item': request.GET.get('section_item', '-'),
               'article_item': request.GET.get('article_item', '-'),
               'price_item': request.GET.get('price_item', '-'), 'quantity_item': request.GET.get('quantity_item', '-'),
               'status_item': request.GET.get('status_item', '-')}
    rendered_page = template.render(context, request)
    return HttpResponse(rendered_page)


def my_vendors(request):
    data = [r._asdict() for r in Vendor1.objects.all()]
    transport = [r._asdict() for r in Transport.objects.all()]
    template = loader.get_template('table-vendors.html')
    context = {'df': data, 'transport': transport}
    rendered_page = template.render(context, request)
    return HttpResponse(rendered_page)


def my_modules(request):
    data = [r._asdict() for r in Module.objects.all()]
    template = loader.get_template('table-market.html')
    context = {'df': data}
    rendered_page = template.render(context, request)
    return HttpResponse(rendered_page)


def my_profiles(request):
    characters_site = pd.read_csv(config['EXPORT_SITE'][request.GET.get('site', 'boint')] +
                                  'bitrix/catalog_export/lecsan_export/catalogs/characters.csv')
    df = pd.read_csv(config['EXPORT_SITE'][request.GET.get('site', 'boint')] +
                     'bitrix/catalog_export/lecsan_export/catalogs/export_new.csv')
    category_ozon = ['Встраиваемая_вытяжка_в_столешницу', 'Вытяжка_каминная', 'Мини-печь_духовка_электропечь',
                     'Чайник_электрический', 'Микроволновая_СВЧ-печь', 'Блендер_погружной',
                     'Мясорубка_электрическая', 'Соковыжималка_электрическая', 'Встраиваемая_панель_газовая',
                     'Встраиваемая_панель_комбинированная', 'Встраиваемая_панель_электрическая_индукционная',
                     'Встраиваемая_панель_электрическая_не_индукционная', 'Аэрогриль', 'Мультиварка_скороварка',
                     'Тостер', 'Встраиваемый_духовой_шкаф_газовый', 'Телевизор', 'Встраиваемая_микроволновая_печь',
                     'Встраиваемый_духовой_шкаф_электрический', 'Плита_газовая', 'Компактная_кухонная_плита']
    characters_ozon = ['Идентификатор_товара_артикул', 'Название_товара', 'Изображения',
                       'Цена_с_учетом_скидок', 'Ставка_НДС_для_товара', 'Длина_упаковки',
                       'Ширина_упаковки', 'Высота_упаковки', 'Вес_товара_в_упаковке', 'Бренд', 'Категория']
    category_avito = ['Термометры и метеостанции', 'Очистители воздуха', 'Обогреватели', 'Кондиционеры',
                      'Вентиляторы', 'Холодильники и морозильные камеры', 'Посудомоечные машины',
                      'Плиты', 'Мелкая кухонная техника', 'Эпиляторы', 'Фены и приборы для укладки',
                      'Машинки для стрижки', 'Бритвы и триммеры', 'Швейные машины', 'Утюги', 'Пылесосы',
                      'Стиральные машины', 'Другое', 'Вытяжки']
    category_site = list(df['Категория'].unique())
    module = ['Ozon']
    site = ['технолайн', 'boint', 'mainfled.spb']
    b_lines = [row for row in reversed(list(open("./static/logs/import_ozon.txt", "r+")))]
    data = [r._asdict() for r in Profile1.objects.filter(site=request.GET.get('site', 'технолайн')).all()]
    template = loader.get_template('export_profile.html')
    context = {'df': data, 'module': module, 'story_category': category_site,
               'category': category_ozon, 'category_avito': category_avito,
               'story_brand': characters_ozon, 'brand': list(characters_site['Характеристики'].unique()),
               'b_lines': b_lines, 'site': site, 'market': 'Ozon'}
    rendered_page = template.render(context, request)
    return HttpResponse(rendered_page)


def ym_profiles(request):
    characters_site = pd.read_csv(config['EXPORT_SITE']['boint'] +
                                  'bitrix/catalog_export/lecsan_export/catalogs/characters.csv')
    characters_site_tech = pd.read_csv(config['EXPORT_SITE']['boint'] +
                                       'bitrix/catalog_export/lecsan_export/catalogs/characters.csv')
    characters_ym = ['Идентификатор_товара_артикул', 'Название_товара', 'Остаток',
                     'Цена_с_учетом_скидок', 'Категория', 'Изображения',
                     'Описание_товара',
                     'Вес_товара_в_упаковке', 'Бренд']
    site = ['технолайн', 'boint', 'mainfled.spb']
    b_lines = [row for row in reversed(list(open("./static/logs/import_ym.txt", "r+")))]
    data = [r._asdict() for r in Profile1.objects.filter(module='YandexMarket').all()]
    template = loader.get_template('export_profile.html')
    context = {'df': data,
               'story_brand': characters_ym, 'brand': list(characters_site['Характеристики'].unique()),
               'brand_tech': list(characters_site_tech['Характеристики'].unique()),
               'b_lines': b_lines, 'site': site, 'market': 'YandexMarket'}
    rendered_page = template.render(context, request)
    return HttpResponse(rendered_page)


def load():
    global data_list
    ret = ServerSideTable(request, data_list, SERVERSIDE_TABLE_COLUMNS).output_result()
    return jsonify(ret)


def load_boint_items():
    global load_boint_items
    ret = ServerSideTable(request, load_boint_items, SERVERSIDE_TABLE_BOINT_ITEMS_COLUMNS).output_result()
    return jsonify(ret)


def load_items():
    global data_items
    ret = ServerSideTable(request, data_items, SERVERSIDE_TABLE_ITEMS_COLUMNS).output_result()
    return jsonify(ret)


def load_vendor_items():
    global data
    ret = ServerSideTable(request, data, SERVERSIDE_TABLE_VENDOR_COLUMNS).output_result()
    return jsonify(ret)
