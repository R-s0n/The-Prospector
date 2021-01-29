from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import User, Search, Company, Job, Contact, Note, Comment
import bcrypt, datetime, requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import numpy as np
import io
import urllib, base64



def index(request):
    if 'userid' in request.session:
        logged_user = User.objects.filter(id=request.session['userid'])
        if logged_user:
            return redirect("/home")
    return render(request, "index.html")

def home(request):
    if 'userid' in request.session:
        logged_user = User.objects.filter(id=request.session['userid']).first()
        if logged_user.first_login == True:
            return redirect("/about")
        searches = []
        counter = 0
        for search in logged_user.searches.all().order_by("-created_at"):
            if counter == 10:
                break
            searches.append(search)
            counter += 1
        companies_watchlisted = []
        counter = 0
        for company in logged_user.watchlisted_companies.all().order_by("updated_at"):
            if counter == 10:
                break
            companies_watchlisted.append(company)
            counter += 1
        context ={
            "logged_user" : logged_user,
            "searches" : searches,
            "companies_watchlisted" : companies_watchlisted,
            "notes" : logged_user.notes.all().order_by("-created_at")
        }
        return render(request, "home.html", context)
    return redirect("/")

def register(request):
    if request.method != "POST":
        return redirect("/")
    errors = User.objects.basic_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect("/register/form")
    else:
        password = request.POST['passwd']
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        users = User.objects.all()
        if not users:
            new_user = User.objects.create(first_name=request.POST['fname'], last_name=request.POST['lname'], email=request.POST['email'], password=pw_hash, admin=True, last_login=timezone.now())
        else:
            new_user = User.objects.create(first_name=request.POST['fname'], last_name=request.POST['lname'], email=request.POST['email'], password=pw_hash, last_login=timezone.now())
        logged_user = User.objects.filter(email=request.POST['email']).first()
        request.session['userid'] = logged_user.id
        return redirect("/home")

def login(request):
    if request.method != "POST":
        return redirect("/")
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
        messages.error(request, "Invalid Credentials")
        return redirect("/")

def logout(request):
    if 'userid' not in request.session:
        return redirect("/")
    del request.session['userid']
    return redirect("/")

def register_form(request):
    if 'userid' in request.session:
        logged_user = User.objects.filter(id=request.session['userid'])
        if logged_user:
            return redirect("/home")
    return render(request, "index_register.html")

def users(request):
    if 'userid' not in request.session:
        return redirect("/")
    context = {
        "logged_user" : User.objects.filter(id=request.session['userid']).first(),
        "all_users" : User.objects.all()
    }
    return render(request, "users.html", context)

def user_profile(request, id):
    if 'userid' not in request.session:
        return redirect("/")
    this_user = User.objects.filter(id=int(id)).first()
    if not this_user:
        return redirect("/notfound")
    context = {
        "this_user" : this_user,
        "logged_user" : User.objects.filter(id=request.session['userid']).first()
    }
    return render(request, "user_profile.html", context)

def user_edit(request, id):
    if 'userid' not in request.session:
        return redirect("/")
    logged_user = User.objects.filter(id=request.session['userid']).first()
    this_user = User.objects.filter(id=int(id)).first()
    if not this_user:
        return redirect("/notfound")
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
    if request.method != "POST":
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
    if request.method != "POST":
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
    if request.method != "POST":
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
    if 'userid' not in request.session:
        return redirect("/")
    if request.method != "POST":
        return redirect("/")
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
        logged_user = User.objects.filter(email=request.POST['email']).first()
        request.session['userid'] = logged_user.id
        return redirect("/home")

def search(request):
    if 'userid' not in request.session:
        return redirect("/")
    context = {
        "logged_user" : User.objects.filter(id=request.session['userid']).first()
    }
    return render(request, "search.html", context)

def search_process(request):
    if 'userid' not in request.session:
        return redirect("/")
    if request.method != "POST":
        return redirect("/")
    errors = Search.objects.search_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect(f"/search")
    service = request.POST['service'].replace(" ", "+")
    search_page = requests.get(f"https://indeed.com/jobs?q={service}&l={request.POST['city']},+{request.POST['state']}&radius={request.POST['radius']}&limit=50&sort=date")
    soup = BeautifulSoup(search_page.content, 'html.parser')
    this_search = Search.objects.create(service=request.POST['service'], city=request.POST['city'], state=request.POST['state'], radius=request.POST['radius'], user=User.objects.filter(id=request.session['userid']).first())
    print(f"Search ID: {this_search.id}")
    companies = soup.find_all('span', class_="company")
    company_titles = []
    company_objects_list = []
    temp_arr = []
    job_titles = []
    date_posted = []
    indeed_links = []
    for company in companies:
        temp_arr.append(company.get_text())
        if company.a:
            indeed_links.append(company.a['href'])
        else:
            indeed_links.append("#")
    for each in temp_arr:
        company_titles.append(each.replace('\n', ''))
    for company in company_titles:
        does_company_exist = Company.objects.filter(name=company).first()
        if not does_company_exist:
            this_company = Company.objects.create(name=company)
        else:
            this_company = does_company_exist
        this_search.companies.add(this_company)
        company_objects_list.append(this_company)
    jobs = soup.find_all('a', class_="jobtitle turnstileLink")
    for job in jobs:
        job_titles.append(job.attrs['title'])
    dates = soup.find_all('span', class_="date")
    for date in dates:
        date_posted.append(date.get_text())
    for i in range(len(jobs)):
        this_job = Job.objects.create(title=job_titles[i], date_posted=date_posted[i], company=company_objects_list[i])
        this_search.jobs.add(this_job)
        this_company = company_objects_list[i]
        this_company.indeed_link = indeed_links[i]
        company_name_urlencoded = this_company.name.replace(" ", "%20")
        this_company.dnb_link = f"https://www.dnb.com/business-directory/top-results.html?term={company_name_urlencoded}&page=1"
        this_company.glassdoor_link = f"https://www.glassdoor.com/Reviews/company-reviews.htm?sc.keyword={company_name_urlencoded}"
        this_company.google_link = f"https://google.com/search?q={company_name_urlencoded}"
        this_company.save()
    return redirect("/search/results")

def search_results(request):
    if 'userid' not in request.session:
        return redirect("/")
    logged_user = User.objects.filter(id=request.session['userid']).first()
    this_search = logged_user.searches.all().last()
    jobs = this_search.jobs.all()
    context = {
        "logged_user" : logged_user,
        "this_search" : this_search,
        "jobs" : jobs
    }
    return render(request, "search_results.html", context)

def company_info(request, id):
    if 'userid' not in request.session:
        return redirect("/")
    if not Company.objects.filter(id=id).first():
        return redirect("/notfound")
    this_company = Company.objects.filter(id=id).first()
    company_jobs = this_company.jobs.all()
    jobs = []
    for job in company_jobs:
        not_in = True
        for each in jobs:
            if job.title == each.title:
                not_in = False
        if not_in == True:
            jobs.append(job)
    searches = this_company.searches.all().order_by("-created_at")
    contacts = this_company.contacts.all()
    logged_user = User.objects.filter(id=request.session['userid']).first()
    watchlisted = logged_user.watchlisted_companies.all()
    if this_company in watchlisted:
        is_watchlisted = True
    else:
        is_watchlisted = False
    context = {
        "this_company" : this_company,
        "logged_user" : logged_user,
        "jobs" : jobs,
        "searches" : searches,
        "contacts" : contacts,
        "notes" : this_company.notes.all().order_by("-created_at"),
        "is_watchlisted" : is_watchlisted
    }
    return render(request, "company_info.html", context)

def not_found(request):
    if 'userid' not in request.session:
        return redirect("/")
    return render(request, "not_found.html")

def edit_company_info(request, id):
    if 'userid' not in request.session:
        return redirect("/")
    this_company = Company.objects.filter(id=id).first()
    if not this_company:
        return redirect("/notfound")
    company_jobs = this_company.jobs.all()
    jobs = []
    for job in company_jobs:
        not_in = True
        for each in jobs:
            if job.title == each.title:
                not_in = False
        if not_in == True:
            jobs.append(job)
    searches = this_company.searches.all().order_by("-created_at")
    contacts = this_company.contacts.all()
    context = {
        "this_company" : this_company,
        "logged_user" : User.objects.filter(id=request.session['userid']).first(),
        "jobs" : jobs,
        "searches" : searches,
        "contacts" : contacts,
        "notes" : this_company.notes.all().order_by("-created_at")
    }
    return render(request, "edit_company_info.html", context)

def process_edit_company(request):
    if 'userid' not in request.session:
        return redirect("/")
    if request.method != "POST":
        return redirect("/")
    logged_user = User.objects.filter(id=request.session['userid']).first()
    this_company = Company.objects.filter(id=request.POST['company_id']).first()
    if request.POST['headquarters']:
        this_company.headquarters = request.POST['headquarters']
    if request.POST['revenue']:
        this_company.revenue = request.POST['revenue']
    if request.POST['size']:
        this_company.size = request.POST['size']
    if request.POST['industry']:
        this_company.industry = request.POST['industry']
    this_company.last_edited_by = logged_user.first_name
    this_company.last_edited_on = timezone.now()
    this_company.save()
    return redirect(f"/company/{this_company.id}")

def add_contact(request, id):
    if 'userid' not in request.session:
        return redirect("/")
    if not Company.objects.filter(id=id).first():
        return redirect("/notfound")
    context = {
        "logged_user" : User.objects.filter(id=request.session['userid']).first(),
        "this_company" : Company.objects.filter(id=id).first
    }
    return render(request, "add_contact.html", context)

def process_add_contact(request):
    if 'userid' not in request.session:
        return redirect("/")
    if request.method != "POST":
        return redirect("/")
    Contact.objects.create(first_name=request.POST['fname'], last_name=request.POST['lname'], email=request.POST['email'], linked_in=request.POST['linked_in'], department=request.POST['department'], position=request.POST['position'], notes=request.POST['notes'], company=Company.objects.filter(id=request.POST['company_id']).first())
    return redirect(f"/company/{request.POST['company_id']}")

def search_history(request):
    if 'userid' not in request.session:
        return redirect("/")
    context = {
        "logged_user" : User.objects.filter(id=request.session['userid']).first(),
        "searches" : Search.objects.all().order_by("-created_at")
    }
    return render(request, "search_history.html", context)

def view_search(request, id):
    if 'userid' not in request.session:
        return redirect("/")
    this_search = Search.objects.filter(id=id).first()
    if not this_search:
        return redirect("/notfound")
    context = {
        "logged_user" : User.objects.filter(id=request.session['userid']).first(),
        "this_search" : this_search,
        "jobs" : this_search.jobs.all()
    }
    return render(request, "view_search.html", context)

def process_note(request):
    if 'userid' not in request.session:
        return redirect("/")
    this_company = Company.objects.filter(id=request.POST['company_id']).first()
    errors = Note.objects.note_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect(f"/company/{this_company.id}")
    logged_user = User.objects.filter(id=request.session['userid']).first()
    Note.objects.create(content=request.POST['content'], user=logged_user, company=this_company)
    return redirect(f"/company/{this_company.id}")

def admin_wall(request):
    if 'userid' not in request.session:
        return redirect("/")
    logged_user = User.objects.filter(id=request.session['userid']).first()
    if logged_user.admin != True:
        return redirect("/")
    context = {
        "notes" : Note.objects.all().order_by("-created_at"),
        "logged_user" : logged_user
    }
    return render(request, "admin_wall.html", context)

def process_comment(request):
    if 'userid' not in request.session:
        return redirect("/")
    logged_user = User.objects.filter(id=request.session['userid']).first()
    if logged_user.admin != True:
        return redirect("/")
    errors = Comment.objects.comment_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        request.session['noteid'] = int(request.POST['note_id'])
        return redirect(f"/admin/wall")
    this_note = Note.objects.filter(id=request.POST['note_id']).first()
    Comment.objects.create(content=request.POST['content'], user=logged_user, note=this_note)
    return redirect("/admin/wall")

def process_watchlist(request, id):
    if 'userid' not in request.session:
        return redirect("/")
    this_user = User.objects.filter(id=request.session['userid']).first()
    this_company = Company.objects.filter(id=id).first()
    this_company.users_who_watchlisted.add(this_user)
    return redirect(f"/company/{id}")

def watchlist(request):
    if 'userid' not in request.session:
        return redirect("/")
    logged_user = User.objects.filter(id=request.session['userid']).first()
    context = {
        "logged_user" : logged_user,
        "watchlisted_companies" : logged_user.watchlisted_companies.all()
    }
    return render(request, "watchlist.html", context)

def edit_contact(request, id):
    if 'userid' not in request.session:
        return redirect("/")
    context = {
        "this_contact" : Contact.objects.filter(id=id).first(),
        "logged_user" : User.objects.filter(id=request.session['userid']).first()
    }
    return render(request, "edit_contact.html", context)

def process_edit_contact(request):
    if 'userid' not in request.session:
        return redirect("/")
    contact = Contact.objects.filter(id=request.POST['contact_id']).first()
    contact.first_name = request.POST['fname']
    contact.last_name = request.POST['lname']
    contact.email = request.POST['email']
    contact.linked_in = request.POST['linked_in']
    contact.department = request.POST['department']
    contact.position = request.POST['position']
    contact.notes = request.POST['notes']
    contact.save()
    return redirect(f"/company/{contact.company.id}")

def delete_contact(request, id):
    if 'userid' not in request.session:
        return redirect("/")
    contact = Contact.objects.filter(id=id).first()
    contact.delete()
    return redirect(f"/company/{contact.company.id}")

def about(request):
    if 'userid' not in request.session:
        return redirect("/")
    logged_user = User.objects.filter(id=request.session['userid']).first()
    logged_user.first_login = False
    logged_user.save()
    context = {
        "logged_user" : logged_user
    }
    return render(request, "about.html", context)

def bad_request(request, path):
    if 'userid' not in request.session:
        return redirect("/")
    context = {
        "logged_user" : User.objects.filter(id=request.session['userid']).first()
    }
    return render(request, "404_not_found.html", context)

def user_delete(request, id):
    if 'userid' not in request.session:
        return redirect("/")
    logged_user = User.objects.filter(id=request.session['userid']).first()
    this_user = User.objects.filter(id=int(id)).first()
    if not this_user:
        return redirect("/notfound")
    if logged_user.admin != True and logged_user.id != this_user.id:
        return redirect("/home")
    this_user.delete()
    return redirect("/users")
