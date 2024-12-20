from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.sessions.models import Session
from django.template import loader

def userValidation(request):
    if request.method == "POST":
        emailid = request.POST["emailid"]
        password = request.POST['password']
        user_mail = "user1@gmail.com"
        user_password = "user1@123"
        if user_mail == emailid and user_password == password:
            request.session['emailid'] = emailid
            request.session.save()
            return redirect('/') 
        else:
            context = {
                'error':True
            }
            return HttpResponse(render(request,"login.html",context))
    
def indexPage(request):
    request.name = "User1"
    request.pagename = "BI-Tool"
    return render(request, "index.html")

def loginValid(func):
    def val(request):
        sessionMailid = request.session.get("emailid")
        if(sessionMailid):
           return redirect("")  
        else:
           func(request)
        return func(request)
    return val
@loginValid 
def loginPage(request):
    return HttpResponse(loader.get_template("login.html").render())

def logoutUser(request):
    Session.objects.filter(session_key = request.session.session_key).delete()
    return redirect('/login')

def testing(request):
    return HttpResponse(loader.get_template("testing.html").render())


     
        
        



