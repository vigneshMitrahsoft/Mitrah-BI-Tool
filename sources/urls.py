from django.urls import path
from . import views

urlpatterns = [
    path("tables", views.getTables),
    path("sheets", views.getSheets),
    path("sourcerecords",views.sourceRecords)
]