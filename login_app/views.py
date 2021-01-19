from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User
import bcrypt

def index(request):
    if 'userid' in request.session:
        logged_user = User.objects.filter(id=request.session['userid'])
        if logged_user:
            return redirect("/home")
    return render(request, "index.html")

def home(request):
    if 'userid' in request.session:
        print(request.session['userid'])
        logged_user = User.objects.get(id=request.session['userid'])
        print(logged_user.first_name)
        context ={
            "logged_user" : logged_user
        }
        return render(request, "home.html", context)
    return redirect("/")

def register(request):
    errors = User.objects.basic_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect("/register_form")
    else:
        password = request.POST['passwd']
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        new_user = User.objects.create(first_name=request.POST['fname'], last_name=request.POST['lname'], email=request.POST['email'], password=pw_hash)
        new_user.save()
        logged_user = User.objects.get(email=request.POST['email'])
        request.session['userid'] = logged_user.id
        return redirect("/home")

def login(request):
    errors = User.objects.login_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect("/")
    else:
        user = User.objects.filter(email=request.POST['email'])
        if user:
            logged_user = user[0]
            if bcrypt.checkpw(request.POST['passwd'].encode(), logged_user.password.encode()):
                request.session['userid'] = logged_user.id
                return redirect('/home')
        return redirect("/")

def logout(request):
    del request.session['userid']
    return redirect("/")

def register_form(request):
    return render(request, "index_register.html")