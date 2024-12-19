from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("",views.loginPage),
    path("uservalidation/",views.userValidation),
    path("index/",views.indexPage),
    path("logout/",views.logoutUser),
    path("dbconnectionform/",views.dbConnectionForm)
]