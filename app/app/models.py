from django.db import models


# Create your models here.

class Person(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    age = models.IntegerField()


class Order1(models.Model):
    number_id = models.CharField(max_length=100, primary_key=True)
    date = models.CharField(max_length=100, null=True, blank=True)
    sum = models.CharField(max_length=100, null=True, blank=True)
    type_payment = models.CharField(max_length=100, null=True, blank=True)
    sum_payment = models.CharField(max_length=100, null=True, blank=True)
    manager = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    status_obr = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'orders'


class Delivery6(models.Model):
    number_id = models.CharField(max_length=100, primary_key=True)
    adress = models.CharField(max_length=1000, null=True, blank=True)
    sum_order = models.CharField(max_length=100, null=True, blank=True)
    date = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    sum = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    comment = models.CharField(max_length=100, null=True, blank=True)
    driver = models.CharField(max_length=100, null=True, blank=True)
    status_pay = models.CharField(max_length=100, null=True, blank=True)
    manager = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'delivery'


class Driver(models.Model):
    fio = models.CharField(max_length=200, null=True, blank=True)
    number = models.CharField(max_length=100, null=True, blank=True)
    login = models.CharField(max_length=100, primary_key=True)
    report = models.CharField(max_length=200, null=True, blank=True)
    smena = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'driver'


class OrdersOzon(models.Model):
    number_id = models.CharField(max_length=100, primary_key=True)  # order_id
    client_id = models.CharField(max_length=100, null=True, blank=True)  # order_id
    date = models.CharField(max_length=100, null=True, blank=True)  # in_process_at
    status = models.CharField(max_length=100, null=True, blank=True)  # status
    substatus = models.CharField(max_length=100, null=True, blank=True)  # status
    discount_total = models.CharField(max_length=100, null=True, blank=True)  # total_discount_value sum
    commission_amount = models.CharField(max_length=100, null=True, blank=True)  # commission_amount sum
    total = models.CharField(max_length=100, null=True, blank=True)  # price sum
    items = models.CharField(max_length=1000, null=True, blank=True)

    class Meta:
        db_table = 'orders_ozon'


class OrdersYM(models.Model):
    number_id = models.CharField(max_length=100, primary_key=True)
    date = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    substatus = models.CharField(max_length=100, null=True, blank=True)
    commission = models.CharField(max_length=100, null=True, blank=True)
    items_total = models.CharField(max_length=100, null=True, blank=True)
    total = models.CharField(max_length=100, null=True, blank=True)
    items = models.CharField(max_length=1000, null=True, blank=True)

    class Meta:
        db_table = 'orders_market'


class ImportProvider1(models.Model):
    id_provider = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    count_new = models.CharField(max_length=200, null=True, blank=True)
    count_update = models.CharField(max_length=200, null=True, blank=True)
    date_register = models.CharField(max_length=200, null=True, blank=True)
    site = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'import_provider'


class Rule3(models.Model):
    id_rule = models.CharField(max_length=200, primary_key=True)
    story = models.CharField(max_length=200, null=True, blank=True)
    vendor = models.CharField(max_length=200, null=True, blank=True)
    vendor_site = models.CharField(max_length=20000, null=True, blank=True)
    section = models.CharField(max_length=20000, null=True, blank=True)
    type = models.CharField(max_length=200, null=True, blank=True)
    cb = models.CharField(max_length=200, null=True, blank=True)
    margin = models.CharField(max_length=200, null=True, blank=True)
    type_margin = models.CharField(max_length=200, null=True, blank=True)
    add_summ = models.CharField(max_length=200, null=True, blank=True, default='0.0')

    class Meta:
        db_table = 'rules'


class Items(models.Model):
    id_site = models.CharField(max_length=200, primary_key=True)
    brand = models.CharField(max_length=200, null=True, blank=True)
    section = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    article = models.CharField(max_length=200, null=True, blank=True)
    price = models.CharField(max_length=200, null=True, blank=True)
    quantity = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=200, null=True, blank=True)
    story = models.CharField(max_length=200, null=True, blank=True)
    willdberis = models.CharField(max_length=200, null=True, blank=True)
    is_kgt = models.CharField(max_length=200, null=True, blank=True)
    spb_quantity = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'items'


class ItemsProvider1(models.Model):
    id_vendor = models.CharField(max_length=200, primary_key=True)
    vendor_name = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    article = models.CharField(max_length=200, null=True, blank=True)
    price = models.CharField(max_length=200, null=True, blank=True)
    oc_price = models.CharField(max_length=200, null=True, blank=True)
    price_site = models.CharField(max_length=200, null=True, blank=True)
    quantity = models.CharField(max_length=200, null=True, blank=True)
    id_site = models.CharField(max_length=200, null=True, blank=True)
    story = models.CharField(max_length=200, null=True, blank=True)
    date_update = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'items_provider'
        

class Vendor1(models.Model):
    name = models.CharField(max_length=200, primary_key=True)
    transport = models.CharField(max_length=200, null=True, blank=True)
    file_name = models.CharField(max_length=200, null=True, blank=True)
    date_upload = models.CharField(max_length=200, null=True, blank=True)
    last_import = models.CharField(max_length=200, null=True, blank=True)
    active = models.CharField(max_length=200, null=True, blank=True)
    cron = models.CharField(max_length=200, null=True, blank=True)
    
    class Meta:
        db_table = 'vendors'


class Module(models.Model):
    name = models.CharField(max_length=200, primary_key=True)
    host = models.CharField(max_length=400, null=True, blank=True)
    api_key = models.CharField(max_length=400, null=True, blank=True)

    class Meta:
        db_table = 'modules'


class Profile1(models.Model):
    name = models.CharField(max_length=200, primary_key=True)
    module = models.CharField(max_length=200, null=True, blank=True)
    categor = models.CharField(max_length=10000, null=True, blank=True)
    character = models.CharField(max_length=10000, null=True, blank=True)
    active = models.CharField(max_length=200, null=True, blank=True)
    cron = models.CharField(max_length=200, null=True, blank=True)
    site = models.CharField(max_length=200, null=True, blank=True)
    
    class Meta:
        db_table = 'profiles'


class Transport(models.Model):
    name = models.CharField(max_length=200, primary_key=True)
    host = models.CharField(max_length=200, null=True, blank=True)
    port = models.CharField(max_length=200, null=True, blank=True)
    login = models.CharField(max_length=200, null=True, blank=True)
    password = models.CharField(max_length=200, null=True, blank=True)
    path = models.CharField(max_length=200, null=True, blank=True)
    name_file = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'transports'