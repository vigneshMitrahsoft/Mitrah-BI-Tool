import os
import io
import base64
import json
import urllib
from builtins import str
from django.http import  JsonResponse
from django.shortcuts import redirect, render
import pandas as pd
from .models import sources,reports
from main.connectors import connectors
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode
import matplotlib.pyplot as plt


def decryptDbCredential(data):
	def decrypt_data(encrypted_data, secret_key):
		ciphertext = b64decode(encrypted_data['ciphertext'])
		iv = b64decode(encrypted_data['iv'])
		key = secret_key.encode('utf-8')
		cipher = AES.new(key, AES.MODE_CBC, iv)
		decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size)
		return decrypted_data.decode('utf-8')
	encrypted_data = {
		'ciphertext': data['ciphertext'],
		'iv': data['iv'],
	}
	secret_key = "navissmith010701"
	decrypted_data = decrypt_data(encrypted_data, secret_key)
	# print(f'Decrypted data: {decrypted_data}')
	value = json.loads(decrypted_data)
	# print(type(decrypted_data))
	return value
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

def changeDateFormat(data_frame):
	for col in data_frame.columns:
		if data_frame[col].dtype == 'datetime64[ns]':
			data_frame[col] = data_frame[col].dt.strftime('%Y-%m-%d %H:%M:%S')
	# data_frame['ModifiedDate'] = format(data_frame['ModifiedDate'], 'dd/mm/yyyy')
	return data_frame
def changePandasDatatypes(source,column_and_dtypes):
	type_mapping = {
    'int': 'Int',
	'tinyint':'Int',
    'bigint': 'Int',
	'integer':'Int',
    'float': 'float',
    'decimal': 'float',
    'varchar': 'string',
    'nvarchar': 'string',
    'datetime': 'datetime',
    'date': 'datetime',
    'bit': 'bool',
    'char': 'string'
	}
	for value in column_and_dtypes:
		column_name = value[0]
		column_type = value[1]
		if column_name in source.columns:
			if column_type in type_mapping:
				source[column_name] = source[column_name].astype(type_mapping[column_type])
			elif column_type =="timestamp with time zone":
				source[column_name] = pd.to_datetime(source[column_name], errors='coerce')
				source[column_name] = source[column_name].dt.tz_localize(None)
				source[column_name] = source[column_name].astype("datetime")
				# if source[column_name].dt.tz is None:
				# 	source[column_name] = source[column_name].dt.tz_localize('UTC')
				# source[column_name] = source[column_name].dt.tz_convert('UTC')
	print("source->",source)
	return source
def sourceRecords(request):
	source_details = request.POST.get("source_details")
	source_details = json.loads(source_details)
	db_credential = decryptDbCredential(source_details)
	checked_tables = request.POST.get("checked_tables")
	selected_tables = checked_tables.split(",")
	user_id = 1
	source_id = 14
	# create_db = sources.objects.create(db_credential = source_details, selected_tables = checked_tables, user_id = user_id)
	# source_id = create_db.source_id
	connector = connectors(**db_credential)
	for table in selected_tables:
		select_table = connectors(driver_name = db_credential['driver_name'], server_name = db_credential['server_name'], database_name = 
	db_credential['database_name'], port = db_credential['port'], user_name = db_credential['user_name'], password = db_credential['password']).get_selected_tables(table)
		select_table = connector.get_selected_tables(table)
		df = pd.DataFrame(select_table.fetchall())
		df = changeDateFormat(df)
		column_name_with_dtype = connector.get_column_with_dtype(table)
		column_and_dtypes = column_name_with_dtype.fetchall()
		print("column with dtypes",column_and_dtypes)
		df = changePandasDatatypes(df,column_and_dtypes)
		parquet_name = f'{table}.parquet'
		path_directory = "assest/parquet_files"
		source_path_directory = f"assest/parquet_files/source_{source_id}"
		if not os.path.exists(path_directory):
			os.makedirs(path_directory)
		elif os.path.exists(path_directory) and not os.path.exists(source_path_directory):
			os.makedirs(source_path_directory)
			if os.path.exists(path_directory) and os.path.exists(source_path_directory):
				file_path = f'{source_path_directory}/{parquet_name}'
				df.to_parquet(file_path)
		else:
			file_path = f'{source_path_directory}/{parquet_name}'
			df.to_parquet(file_path)
	# source_id = 42
	return redirect(f"/source/{source_id}")
def sourceData(request,id):
	try:
		is_exist = sources.objects.get(source_id = id)
		if is_exist:
			return render(request,"table_visualization.html",{'source_id':id})
	except:
		return render(request,"error_page.html",{'id':id})
def getTableList(request):
	source_id = request.POST.get('source_id')
	path = f'assest/parquet_files/source_{source_id}'
	dir_list = os.listdir(path)
	table_list = {}
	for table in dir_list:
		_path = f'{path}/{table}'
		data = pd.read_parquet(_path)
		table_name = table.rsplit('.', 1)[0]
		table_list[table_name] = list(data.columns.values)
	return JsonResponse({'table_list': table_list})

def getTableData(request):
	source_id = request.POST.get('source_id')
	table_name = request.POST.get('table_name')
	limit = int(request.POST.get('limit'))
	current_page = int(request.POST.get('current_page'))
	path = f'assest/parquet_files/source_{source_id}/{table_name}.parquet'
	data = pd.read_parquet(path)
	total_records = len(data.index)
	# data = data.head(50)
	start_row = (limit*current_page)-limit + 1
	data = data.iloc[(start_row - 1):(limit * current_page)]
	table_records = data.to_json(orient='records')
	return JsonResponse({'data': json.loads(table_records),'total_record':total_records})

def getSource(request):
	source_data = sources.objects.all().values()
	return render(request,"source_db.html",{'source_data':source_data})

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
		color = ['yellow','grey','black']
		# bar_chart = plt.bar(x_values, y_values, color = color)
		# plt.title("Educational level")
		# plt.xlabel("Education Level")
		# plt.ylabel("count")
		# plt.legend((bar_chart),(x_values))
		# # plt.legend()
		# fig = plt.gcf()
		# buf =  io.BytesIO()
		# plt.savefig(buf, format = 'png')
		# buf.seek(0)
		# string = base64.b64encode(buf.read())
		# url = urllib.parse.quote(string)
		# result = {'report_type':'Bar','aggregate_function':'count','y_column':'*','x_column':'Edu.Level','level':'Edu.level'}
		# return render(request,"source_db.html", {'url':url})
		# return result,url
	# return render(request,"visual_sample.html", {'x_values':x_values,'y_values':y_values})	
	return JsonResponse({'x_axis':x_values,'y_axis':y_values})
	
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
		# overall_total_count = data.shape[0]
		# percentage = []
		# for chart_count in individual_chart_count:
		# 	individual_percentage = (chart_count *100.00)/overall_total_count
		# 	percentage += [individual_percentage]
		pie_chart = plt.pie(individual_chart_count, labels = chart_name, autopct='%1.1f%%', shadow = True)
		fig = plt.gcf()
		buf = io.BytesIO()
		fig.savefig(buf, format = 'png')
		# fig.savefig('assest/images/testsample.png')        //for save the image into specific location
		buf.seek(0)
		string = base64.b64encode(buf.read())
		url = urllib.parse.quote(string)
		# return render(request,"source_db.html", {'url':url})
		return url
	
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
		# line_chart = plt.plot(chart_name, individual_chart_count)
		# fig = plt.gcf()
		# buf = io.BytesIO()
		# fig.savefig(buf, format = 'png')
		# buf.seek(0)
		# string = base64.b64encode(buf.read())
		# url = urllib.parse.quote(string)
		# return render(request,"source_db.html", {'url':url})
		# return url
		# return render(request,"visual_sample.html", {'x_axis':chart_name,'y_axis':individual_chart_count})
	return JsonResponse({'x_axis':chart_name,'y_axis':individual_chart_count})

	
def report(request,id):
	source_id = id
	report_name = "user35"
	chart_details =[]
	url =[]
	bar_chart = barChart(request,source_id)
	pie_chart = pieChart(request,source_id)
	line_chart = lineChart(request,source_id)
	url.append(bar_chart[1])
	url.append(pie_chart)
	url.append(line_chart)
	chart_details.append(bar_chart[0])
	print("chart_value---->",chart_details)
	# reports.objects.create(report_name = report_name, source_id = source_id, chart_details = chart_details)
	return render(request,"source_db.html", {'url':url})

# def refresh(request,id):
# 	source_id = id
# 	source_file = sources.objects.get(source_id=source_id)
# 	source_tables = source_file.selected_tables.split(",")
# 	db_credential_data = source_file.db_credential
# 	db_credential_data = db_credential_data.replace("'", "\"")
# 	source_file = json.loads(db_credential_data)
# 	db_credential = decryptDbCredential(source_file)
# 	# print("source-->",db_credential.get('server_name'))
# 	connector = connectors(**db_credential)
# 	for table in source_tables:
# 		parquet_file_path = f'assest/parquet_files/source_{source_id}/{table}.parquet'
# 		target_table = pd.read_parquet(parquet_file_path)
# 		# target_table_result = target_table.to_string()
# 		loaded_df = connector.incremental_load(target_table,table)
# 		if loaded_df is not None:
# 			print("loader block exec",parquet_file_path)
# 			loaded_df.to_parquet(parquet_file_path, index=False)

def test(request,id):
	df = pd.read_parquet("assest/parquet_files/source_42/dbo.AWBuildVersion.parquet")
	print("testing---->")
	print(df)

