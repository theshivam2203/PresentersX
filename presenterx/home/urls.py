from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path("", views.index, name="base"),
    path("about", views.about, name="about"),
    path("features", views.features, name="features"),
    path("contact", views.contact, name="contact"),
]