import json
from rest_framework.views import APIView
from rest_framework.response import Response
from sources.models import sources
from django.http import JsonResponse
from rest_framework.decorators import api_view
import os
import pandas as pd
from main.connectors import connectors
from .views import decryptDbCredential
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from .views import changeDateFormat

def pieChart(request,id):
		source_id = id
		path = f'assest/parquet_files/source_{source_id}'
		dir_list = os.listdir(path)
		table_name = 'HumanResources.vJobCandidateEducation.parquet'
		if  table_name in dir_list:
			parquet_file_path = f'{path}/{table_name}'
			data = pd.read_parquet(parquet_file_path)
			column_counts = data.pivot_table(columns = ['Edu.StartDate'], aggfunc = 'size').to_dict()
			chart_name = [key for key in column_counts]
			individual_chart_count = [column_counts[key] for key in column_counts]
			return {'chart_name':chart_name,'count':individual_chart_count}
def barChart(request,id):
		source_id = id
		print("sourceid---->",source_id)
		path = f'assest/parquet_files/source_{source_id}'
		dir_list = os.listdir(path)
		table_name = 'HumanResources.vJobCandidateEducation.parquet'
		if  table_name in dir_list:
			parquet_file_path = f'{path}/{table_name}'
			data = pd.read_parquet(parquet_file_path)
			column_counts = data.pivot_table(columns = ['Edu.Level'], aggfunc = 'size').to_dict()
			x_values = [key for key in column_counts]
			y_values = [column_counts[key] for key in column_counts]
		return {'x_axis':x_values,'y_axis':y_values}

def lineChart(request,id):
	source_id = id
	path = f'assest/parquet_files/source_{source_id}'
	dir_list = os.listdir(path)
	table_name = 'HumanResources.vJobCandidateEducation.parquet'
	if  table_name in dir_list:
		parquet_file_path = f'{path}/{table_name}'
		data = pd.read_parquet(parquet_file_path)
		column_counts = data.pivot_table(columns = ['Edu.StartDate'], aggfunc = 'size').to_dict()
		chart_name = [key for key in column_counts]
		individual_chart_count = [column_counts[key] for key in column_counts]
	return {'x_axis':chart_name,'y_axis':individual_chart_count}

class Sources(APIView):
	@api_view(('GET',))
	def get(self):
		_sources = [user.selected_tables for user in sources.objects.all()]
		print("_sources", _sources)
		# _sources = [
		#	 {
		#		 'source1': ['table1', 'table2']
		#	 },
		#	 {
		#		 'source2': ['table1', 'table2']
		#	 }
		# ]
		return Response({'data': _sources}, status=200)

	@api_view(('POST',))
	def getTables(request):
		source_id = request.data['source_id']
		path = f'assest/parquet_files/source_{source_id}'
		dir_list = os.listdir(path)
		# table_list = {}
		column_list ={}
		for table in dir_list:
			_path = f'{path}/{table}'
			data = pd.read_parquet(_path)
			table_name = table.rsplit('.', 1)[0]
			# table_list[table_name] = list(data.columns.values)
			column_name = list(data.columns.values)
			column_data_types = data.dtypes.astype(str)
			column_data_types = ['string' if dtype == 'object' else dtype for dtype in column_data_types]
			column_information = list(zip(column_name, column_data_types))
			column_data=[]
			for column in column_information:
				dict={}
				dict['column_name'] = column[0]
				dict['type'] = column[1]
				column_data.append(dict)
			column_list[table_name] = column_data 
			print("column-list----->",column_list)
		return JsonResponse({'table_list': column_list})
		
	@api_view(('POST',))
	def getData(request):
		source_id = request.data['source_id']
		table_name = request.data['table_name']
		limit = int(request.data['limit'])
		current_page = int(request.data['current_page'])
		path = f'assest/parquet_files/source_{source_id}/{table_name}.parquet'
		data = pd.read_parquet(path)
		data = changeDateFormat(data)
		total_records = len(data.index)
		# data = data.head(50)
		start_row = (limit*current_page)-limit + 1
		data = data.iloc[(start_row - 1):(limit * current_page)]
		table_records = data.to_json(orient='records')
		return JsonResponse({'data': json.loads(table_records),'total_record':total_records})
	@api_view(('POST',))
	def showTables(request):
		if request.method == 'POST':
			decrypted_credential = decryptDbCredential(request.data)
			driver_name = decrypted_credential['driver_name']
			server_name = decrypted_credential['server_name']
			database_name = decrypted_credential['database_name']
			port = decrypted_credential['port']
			user_name = decrypted_credential['user_name']
			password = decrypted_credential['password']
			connection = connectors(driver_name = driver_name, server_name = server_name, database_name = 
			database_name, port = port, user_name = user_name, password = password)
		
			tables = connection.get_tables()
		
			return JsonResponse({'tables': tables})
	@api_view(('POST',))
	def showSheets(request):
		source = request.data['source']
		if request.method == 'POST' and request.data['file'] and source == "Excel":
			file = request.FILES['file']
			print("file------>",file)
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
	@api_view(('POST',))
	def report(request,id):
		source_id = id
		bar_chart_value = barChart(request,source_id)
		pie_chart_value = pieChart(request,source_id)
		line_chart_value = lineChart(request,source_id)
		return JsonResponse({'pie_chart':pie_chart_value,'bar_chart':bar_chart_value,'line_chart':line_chart_value})
	
	@api_view(('POST',))
	def refresh(request,source_id):
		print("refresh block executed")
		source_id = source_id
		source_file = sources.objects.get(source_id=source_id)
		source_tables = source_file.selected_tables.split(",")
		db_credential_data = source_file.db_credential
		db_credential_data = db_credential_data.replace("'", "\"")
		source_file = json.loads(db_credential_data)
		db_credential = decryptDbCredential(source_file)
		# print("source-->",db_credential.get('server_name'))
		connector = connectors(**db_credential)
		for table in source_tables:
			parquet_file_path = f'assest/parquet_files/source_{source_id}/{table}.parquet'
			target_table = pd.read_parquet(parquet_file_path)
			# target_table_result = target_table.to_string()
			loaded_df = connector.incremental_load(target_table,table)
			if loaded_df is not None:
				loaded_df.to_parquet(parquet_file_path, index=False)
		return JsonResponse({'table_name':source_tables})
