from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.sessions.models import Session
from django.template import loader
import pandas as pd
import pypyodbc as odbc
from main.connectors import connectors

def userValidation(request):
    print(" uservalidation executed")
    if request.method == "POST":
        print("if executed")
        emailid = request.POST["emailid"]
        password = request.POST['password']
        user_mail = "user1@gmail.com"
        user_password = "user1@123"
        if user_mail == emailid and user_password == password:
            print("if block exec")
            request.session['emailid'] = emailid
            request.session.save()
            return redirect('/index/') 
        else:
            print("invalid")
            context = {
                'error':True
            }
            return HttpResponse(render(request,"login_form.html",context))
    
def indexPage(request):
    return render(request, "index.html")

def loginValid(func):
    def val(request):
        sessionMailid = request.session.get("emailid")
        if(sessionMailid):
           return redirect("/index/")  
        else:
           func(request)
        return func(request)
    return val
@loginValid 
def loginPage(request):
    return HttpResponse(loader.get_template("login_form.html").render())

def logoutUser(request):
    Session.objects.filter(session_key = request.session.session_key).delete()
    return redirect('/')

def dbConnectionForm(request):
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
     
        
        



