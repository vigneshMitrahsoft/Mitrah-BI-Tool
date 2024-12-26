import json
from rest_framework.views import APIView
from rest_framework.response import Response
from sources.models import sources
from django.http import JsonResponse
from rest_framework.decorators import api_view
import os
import pandas as pd

class Sources(APIView):
    @api_view(('GET',))
    def get(self):
        _sources = [user.selected_tables for user in sources.objects.all()]
        print("_sources", _sources)
        # _sources = [
        #     {
        #         'source1': ['table1', 'table2']
        #     },
        #     {
        #         'source2': ['table1', 'table2']
        #     }
        # ]
        return Response({'data': _sources}, status=200)
    
    @api_view(('POST',))
    def getTables(request):
        print("source blockk ecex",request.data)
        source_id = request.data['source_id']
        print("source ",source_id)
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
    
    @api_view(('POST',))
    def getData(request):
        print("insi", request.data)
        source_id = request.data['source_id']
        print(source_id)
        table_name = request.data['table_name']
        print(table_name)
        limit = int(request.data['limit'])
        current_page = int(request.data['current_page'])
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