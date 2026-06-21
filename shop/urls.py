from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index , name="index"),
    path("about", views.about , name="AboutUs"),
    path("contact", views.contact , name="ContactUs"),
    path("tracker", views.tracker , name="Tracking Status"),
    path("search", views.search , name="search"),
    path("products/<int:myid>", views.productview , name="Product View"),
    path("checkout", views.checkout , name="Checkout"),
    path('payment-callback/', views.payment_callback, name='payment-callback')
]