from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import User
import bcrypt, datetime, requests
from bs4 import BeautifulSoup

def index(request):
    if 'userid' in request.session:
        logged_user = User.objects.filter(id=request.session['userid'])
        if logged_user:
            return redirect("/home")
    return render(request, "index.html")

def home(request):
    if 'userid' in request.session:
        logged_user = User.objects.get(id=request.session['userid'])
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
        new_user = User.objects.create(first_name=request.POST['fname'], last_name=request.POST['lname'], email=request.POST['email'], password=pw_hash, last_login=timezone.now())
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
                logged_user.last_login = timezone.now()
                logged_user.save()
                return redirect('/home')
        return redirect("/")

def logout(request):
    del request.session['userid']
    return redirect("/")

def register_form(request):
    return render(request, "index_register.html")

def users(request):
    if 'userid' not in request.session:
        return redirect("/")
    context = {
        "logged_user" : User.objects.get(id=request.session['userid']),
        "all_users" : User.objects.all()
    }
    return render(request, "users.html", context)

def user_profile(request, id):
    if 'userid' not in request.session:
        return redirect("/")
    User.objects.filter(id=int(id))
    context = {
        "this_user" : User.objects.filter(id=int(id)).first(),
        "logged_user" : User.objects.get(id=request.session['userid'])
    }
    return render(request, "user_profile.html", context)

def user_edit(request, id):
    if 'userid' not in request.session:
        return redirect("/")
    logged_user = User.objects.filter(id=request.session['userid']).first()
    this_user = User.objects.filter(id=int(id)).first()
    if logged_user.admin != True and logged_user.id != this_user.id:
        return redirect("/home")
    context = {
        "logged_user" : logged_user,
        "this_user" : this_user
    }
    return render(request, "user_edit.html", context)

def edit_user_info(request):
    if 'userid' not in request.session:
        return redirect("/")
    this_user = User.objects.filter(id=request.POST['user_id']).first()
    logged_user = User.objects.filter(id=request.session['userid']).first()
    if logged_user.admin != True and logged_user.id != this_user.id:
        return redirect("/home")
    errors = User.objects.information_validator(request.POST)
    if len(errors) > 0:
        request.session['error_from'] = 1
        for key, value in errors.items():
            messages.error(request, value)
        return redirect(f"/users/{this_user.id}/edit")
    else:
        this_user.fist_name = request.POST['fname']
        this_user.last_name = request.POST['lname']
        this_user.email = request.POST['email']
        this_user.save()
        return redirect(f"/users/{request.POST['user_id']}")

def change_password(request):
    if 'userid' not in request.session:
        return redirect("/")
    this_user = User.objects.filter(id=request.POST['user_id']).first()
    logged_user = User.objects.filter(id=request.session['userid']).first()
    if logged_user.admin != True and logged_user.id != this_user.id:
        return redirect("/home")
    errors = User.objects.password_validator(request.POST)
    if len(errors) > 0:
        request.session['error_from'] = 2
        for key, value in errors.items():
            messages.error(request, value)
        return redirect(f"/users/{this_user.id}/edit")
    else:
        if bcrypt.checkpw(request.POST['current_passwd'].encode(), this_user.password.encode()):
            password = request.POST['passwd']
            pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            this_user.password = pw_hash
            this_user.save()
            return redirect("/home")
        else:
            errors['passwd_conf'] = "Current Password is incorrect!"
            for key, value in errors.items():
                messages.error(request, value)
            return redirect(f"/users/{this_user.id}/edit")

def make_admin(request):
    if 'userid' not in request.session:
        return redirect("/")
    logged_user = User.objects.filter(id=request.session['userid']).first()
    if logged_user.admin != True:
        return redirect("/")
    this_user = User.objects.filter(id=request.POST['user_id']).first()
    this_user.admin = True
    this_user.save()
    return redirect("/users")

def add_user(request):
    if 'userid' not in request.session:
        return redirect("/")
    logged_user = User.objects.filter(id=request.session['userid']).first()
    if logged_user.admin != True:
        return redirect("/")
    context = {
        "logged_user" : logged_user
    }
    return render(request, "user_add.html", context)

def add_user_post(request):
    errors = User.objects.basic_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect("/adduser")
    else:
        password = request.POST['passwd']
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        new_user = User.objects.create(first_name=request.POST['fname'], last_name=request.POST['lname'], email=request.POST['email'], password=pw_hash, last_login=timezone.now())
        new_user.save()
        logged_user = User.objects.get(email=request.POST['email'])
        request.session['userid'] = logged_user.id
        return redirect("/home")

def search(request):
    if 'userid' not in request.session:
        return redirect("/")
    context = {
        "logged_user" : User.objects.filter(id=request.session['userid']).first()
    }
    return render(request, "search.html", context)

def request(request):
    if 'userid' not in request.session:
        return redirect("/")
    page = requests.get(request.POST['url'])
    soup = BeautifulSoup(page.content, 'html.parser')
    pretty_soup = soup.prettify()
    context = {
        "soup" : soup,
        "pretty_soup" : pretty_soup
    }
    return render(request, "test.html", context)