from builtins import str
import json
from django.http import  JsonResponse
from django.shortcuts import redirect, render
from main.connectors import connectors
import pandas as pd
from .models import sources
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import os

def getTables(request):
	if request.method == 'POST':
		driver_name = request.POST.get('driver_name')
		server_name = request.POST.get('server_name')
		database_name = request.POST.get('database_name')
		port = request.POST.get('sport')
		user_name = request.POST.get('user_name')
		password = request.POST.get('password')
		connection = connectors(driver_name = driver_name, server_name = server_name, database_name = 
		database_name, port = port, user_name = user_name, password = password)
	  
		tables = connection.get_tables()
	   
		return JsonResponse({'tables': tables})


def getSheets(request):
	source = request.POST.get('source')
	if request.method == 'POST' and request.FILES.get('file') and source == "Excel":
		file = request.FILES['file']
		file_ext = file.name.rsplit('.', 1)[-1]
		if file_ext in ('xls','xlsx'):
			df = pd.ExcelFile(file)
			sheet_names = df.sheet_names
			return JsonResponse({'sheets':sheet_names})
		else:
			return JsonResponse({'error':"Invalid Format"})
		
	if request.method == 'POST' and request.FILES.get('file') and source == "Csv":
		file = request.FILES['file']
		file_ext = file.name.rsplit('.', 1)[-1]
		if file_ext in ('csv'):
			return JsonResponse({'error':"VALID CSV"})
		else:
			return JsonResponse({'error':"Invalid Format"})

def sourceRecords(request):
	# source_details = request.POST.get("source_details")
	# checked_tables = request.POST.get("checked_tables")
	# db_credential = json.loads(source_details)
	# selected_tables = checked_tables.split(",")
	# user_id = 1
	# create_db = sources.objects.create(db_credential = db_credential, selected_tables = selected_tables, user_id = user_id)
	# source_id = create_db.source_id
	# params = f'{db_credential["user_name"]}:{db_credential["password"]}@{db_credential["server_name"]}/{db_credential["database_name"]}'
	# if db_credential['driver_name'] == "SQL Server":
	# 	connection_string = f'mssql+pyodbc://{params}?driver=ODBC+Driver+17+for+SQL+Server'
	# elif db_credential['driver_name'] == "MySQL":
	# 	connection_string =f'mysql+pymysql://{params}'
	# elif db_credential['driver_name'] == "PostgreSQL":
	# 	connection_string = f'postgresql+pg8000://{params}' 
  
	# engine = create_engine(connection_string)
	# connection = engine.connect()
	# for table in selected_tables:
	# 	query_string = f"select * from {table}"
	# 	selected_table = connection.execute(text(query_string))
	# 	df = pd.DataFrame(selected_table.fetchall())
	# 	parquet_name = f'{table}.parquet'
	# 	path_directory = "assest/parquet_files"
	# 	source_path_directory = f"assest/parquet_files/source_{source_id}"
	# 	 # if not os.path.exists(path_directory):
	# 	 #	 os.makedirs(path_directory)
	# 	 # else:
	# 	 #	 source_path_directory = f"assest/parquet_files/source_{source_id}"
	# 	 #	 if not os.path.exists(source_path_directory):
	# 	 #		 os.makedirs(source_path_directory)
	# 	 #		 if os.path.exists(source_path_directory):
	# 	 #			 file_path = f'{source_path_directory}/.{parquet_name}'
	# 	 #			 df.to_parquet(file_path)
	# 	 #	 else:
	# 	 #		 file_path = f'{source_path_directory}/.{parquet_name}'
	# 	 #		 df.to_parquet(file_path)
	# 	if not os.path.exists(path_directory):
	# 		os.makedirs(path_directory)
	# 	elif os.path.exists(path_directory) and not os.path.exists(source_path_directory):
	# 		os.makedirs(source_path_directory)
	# 		if os.path.exists(path_directory) and os.path.exists(source_path_directory):
	# 			file_path = f'{source_path_directory}/{parquet_name}'
	# 			df.to_parquet(file_path)
	# 	else:
	# 		file_path = f'{source_path_directory}/{parquet_name}'
	# 		df.to_parquet(file_path)
	source_id = 26
	return redirect(f"/source_records/{source_id}")
def sourceData(request,id):
	try:
		is_exist = sources.objects.get(source_id = id)
		if is_exist:
			print("the source id id------>:",id)
			return render(request,"table_visualization.html",{'source_id':id})
	except:
		print("error message ")
		return render(request,"error_page.html",{'id':id})
def getTableList(request):
	print("source blockk ecex")
	sourcess = id
	print("the id value is------------------->:",sourcess)
	source_id = request.POST.get('source_id')
	path = f'assest/parquet_files/source_{source_id}'
	dir_list = os.listdir(path)
	table_list = {}
	for table in dir_list:
		_path = f'{path}/{table}'
		print("path", _path)
		data = pd.read_parquet(_path)
		table_name = table.rsplit('.', 1)[0]
		table_list[table_name] = list(data.columns.values)
	return JsonResponse({'table_list': table_list})

def getTableData(request):
	print("inside get", request.POST.get('source_id[]'))
	source_id = request.POST.get('source_id')
	print(source_id)
	table_name = request.POST.get('table_name')
	print(table_name)
	limit = int(request.POST.get('limit'))
	current_page = int(request.POST.get('current_page'))
	path = f'assest/parquet_files/source_{source_id}/{table_name}.parquet'
	data = pd.read_parquet(path)
	total_records = len(data.index)
	print("total records----->",total_records)
	# data = data.head(50)
	start_row = (limit*current_page)-limit + 1
	print("strat-row",start_row)
	data = data.iloc[(start_row - 1):(limit * current_page)]
	table_records = data.to_json(orient='records')
	return JsonResponse({'data': json.loads(table_records),'total_record':total_records})