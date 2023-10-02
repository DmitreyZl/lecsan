from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

import app.app.views as views
import app.app.answers as answers

urlpatterns = [
    path("", views.select_models),
    path("general_dashboard_sales/", views.my_view),
    path("sales_by_managers/", views.my_view_managers),
    path("orders/", views.my_orders),
    path("order/", views.my_order),
    path("order_ozon/", views.ozon_order),
    path("ozon_orders/", views.ozon_orders),
    path("ym_orders/", views.ym_orders),
    path("order_ym/", views.ym_order),
    path("items/", views.my_items),
    path("vendor_items/", views.my_vendor_items),
    path("wildberries_items/", views.wildberries_items),
    path("items/statistics/", views.statistics_items),
    path("modules/", views.my_modules),
    path("vendors/", views.my_vendors),
    path("modules/ym_profiles/", views.ym_profiles),
    path("modules/profiles/", views.my_profiles),
    path("load_vendor_items/", views.load_vendor_items),
    path("load_items/", views.load_items),
    path("load_boint_items/", views.load_boint_items),
    path("load/", views.load),
    path("vendor/", views.my_vendor),
    path("add_rule/", answers.add_rule),
    path("update_rule/", answers.update_rule),
    path("delete_rule/", answers.delete_rule, name='delete_rule'),
    path("add_orders/", answers.add_orders),
    path("update/", answers.update),
    path("update_order/", answers.update_order),
    path("add_ym_orders/", answers.add_ym_orders, name='add_ym_orders'),
    path("add_ozon_orders/", answers.add_ozon_orders, name='add_ozon_orders'),
    path("add_vendor/", answers.add_vendor, name='add_vendor'),
    path("update_vendor/", answers.update_vendor, name='update_vendor'),
    path("delete_vendor/", answers.delete_vendor, name='delete_vendor'),
    path("add_module/", answers.add_module, name='add_module'),
    path("update_module/", answers.update_module, name='update_module'),
    path("add_user/", answers.add_user, name='add_user'),
    path("add_modules/", answers.add_modules, name='add_modules'),
    path("admin/", admin.site.urls),
    path("login/", views.my_login),
]

if bool(settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
