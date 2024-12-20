from django.http import  JsonResponse
from main.connectors import connectors

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