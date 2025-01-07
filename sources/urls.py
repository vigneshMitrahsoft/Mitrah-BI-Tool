from django.urls import path
from . import views
from sources.api import Sources

urlpatterns = [
	path("tables", views.getTables),
	path("sheets", views.getSheets),
	path("sourcerecords",views.sourceRecords),
    path("source", views.getSource),
    path("source/<int:id>", views.sourceData),
	path("gettablelist",views.getTableList),
	path("gettabledata",views.getTableData),
    path("sources", Sources.get),
    path("gettables", Sources.getTables),
    path("getdata", Sources.getData),
    path("showtables", Sources.showTables),
    path("showsheets", Sources.showSheets),
    # path("barchart/<int:id>",Sources.barChart),
    # path("piechart/<int:id>",Sources.pieChart),
    path("report/<int:id>", Sources.report),
    path("viewsreport/<int:id>", views.refresh),
    path("viewsbarchart/<int:id>", views.barChart),
    path("viewspiechart/<int:id>",views.pieChart),
    path("linechart/<int:id>", views.test),
]