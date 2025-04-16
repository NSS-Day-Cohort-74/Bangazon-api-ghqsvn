from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from bangazonapi.models import *
from bangazonapi.views import (
    Products,
    ProductCategories,
    LineItems,
    Customers,
    Users,
    Orders,
    Cart,
    Payments,
    Profile,
    Store,
    report,
    register_user,
    login_user,
    report_login,
    report,
    favorite_sellers_report,
)

# pylint: disable=invalid-name
router = routers.DefaultRouter(trailing_slash=False)
router.register(r"products", Products, "product")
router.register(r"productcategories", ProductCategories, "productcategory")
router.register(r"lineitems", LineItems, "orderproduct")
router.register(r"customers", Customers, "customer")
router.register(r"users", Users, "user")
router.register(r"orders", Orders, "order")
router.register(r"cart", Cart, "cart")
router.register(r"payment-types", Payments, "payment")
router.register(r"profile", Profile, "profile")
router.register(r"stores", Store, "store")


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path(
        "reports/",
        include(
            [
                path("login", report_login, name="reports_login"),
                path("expensiveproducts", report, name="expensive_report"),
                path("inexpensiveproducts", report, name="inexpensive_report"),
                path("orders", report, name="order_report"),
                path(
                    "favoritesellers",
                    favorite_sellers_report,
                    name="favorite_sellers_report",
                ),
            ]
        ),
    ),
    path("register", register_user, name="register"),
    path("login", login_user, name="login"),
    path("api-token-auth", obtain_auth_token),
    path("api-auth", include("rest_framework.urls", namespace="rest_framework")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
