from django.db import models
from django.utils import timezone
import re, datetime

class UserManager(models.Manager):
    def basic_validator(self, postData):
        errors = {}
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        lowerRegex = re.compile(r'[a-z]+')
        upperRegex = re.compile(r'[A-Z]+')
        digitRegex = re.compile(r'[0-9]+')
        specRegex = re.compile(r'[$&+,:;=?@#|<>.^*()%!-]+')
        if len(postData['fname']) < 2:
            errors["fname"] = "First Name must be at least 2 characters"
        if len(postData['lname']) < 2:
            errors["lname"] = "Last Name must be at least 2 characters"
        email_list = User.objects.filter(email=postData['email'])
        if len(email_list) > 0:
            errors["email_exists"] = "An account with that email already exists"
        if not EMAIL_REGEX.match(postData['email']):
            errors["email"] = "Please enter a valid email address"
        if len(postData['passwd']) < 8: 
            errors["passwd_char"] = "Password must contain atleast 8 characters"
        if not lowerRegex.findall(postData['passwd']): 
            errors["passwd_low"] = "Password must contain atleast one lowercase character"
        if not upperRegex.findall(postData['passwd']): 
            errors["passwd_up"] = "Password must contain atleast one uppercase character"
        if not digitRegex.findall(postData['passwd']): 
            errors["passwd_num"] = "Password must contain atleast one digit"
        if not specRegex.findall(postData['passwd']): 
            errors["passwd_spec"] = "Password must contain atleast one special character"
        if postData["passwd"] != postData["confirm_passwd"]:
            errors["passwd"] = "Passwords do not match!"
        return errors
    
    def password_validator(self, postData):
        errors = {}
        lowerRegex = re.compile(r'[a-z]+')
        upperRegex = re.compile(r'[A-Z]+')
        digitRegex = re.compile(r'[0-9]+')
        specRegex = re.compile(r'[$&+,:;=?@#|<>.^*()%!-]+')
        if len(postData['passwd']) < 8: 
            errors["passwd_char"] = "Password must contain atleast 8 characters"
        if not lowerRegex.findall(postData['passwd']): 
            errors["passwd_low"] = "Password must contain atleast one lowercase character"
        if not upperRegex.findall(postData['passwd']): 
            errors["passwd_up"] = "Password must contain atleast one uppercase character"
        if not digitRegex.findall(postData['passwd']): 
            errors["passwd_num"] = "Password must contain atleast one digit"
        if not specRegex.findall(postData['passwd']): 
            errors["passwd_spec"] = "Password must contain atleast one special character"
        if postData["passwd"] != postData["confirm_passwd"]:
            errors["passwd"] = "Passwords do not match!"
        return errors
    
    def information_validator(self, postData):
        errors = {}
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if len(postData['fname']) < 2:
            errors["fname"] = "First Name must be at least 2 characters"
        if len(postData['lname']) < 2:
            errors["lname"] = "Last Name must be at least 2 characters"
        if not EMAIL_REGEX.match(postData['email']):
            errors["email"] = "Please enter a valid email address"
        return errors
    
    def login_validator(self, postData):
        errors = {}
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(postData['email']):
            errors["email"] = "Please enter a valid email address"
        return errors

class SearchManager(models.Manager):
    def search_validator(self, postData):
        errors = {}
        if len(postData['service']) < 1:
            errors["service"] = "Please enter a service to search for"
        if len(postData['city']) < 1:
            errors["city"] = "Please enter a city"
        if len(postData['state']) != 2:
            errors["state"] = "Please choose a state"
        if len(postData['radius']) < 1:
            errors["radius"] = "How did you pull this off?  Burp Suite??"
        return errors

class NoteManager(models.Manager):
    def note_validator(self, postData):
        errors = {}
        if len(postData['content']) < 1:
            errors["content"] = "You cannot add a blank note."
        return errors

class CommentManager(models.Manager):
    def comment_validator(self, postData):
        errors = {}
        if len(postData['content']) < 1:
            errors["content"] = "You cannot add a blank comment."
        return errors

class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    admin = models.BooleanField(default=False)
    last_login = models.DateTimeField()
    first_login = models.BooleanField(default="True")

    objects = UserManager()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Search(models.Model):
    service = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    radius = models.IntegerField(default=50)

    user = models.ForeignKey(User, related_name="searches", on_delete=models.CASCADE)

    objects = SearchManager()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Company(models.Model):
    name = models.CharField(max_length=255)
    size = models.CharField(max_length=255, default="Unknown")
    revenue = models.CharField(max_length=255, default="Unknown")
    headquarters = models.CharField(max_length=255, default="Unknown")
    industry = models.CharField(max_length=255, default="Unknown")
    founded = models.CharField(max_length=255, default="Unknown")
    last_edited_by = models.CharField(max_length=255, default="Noone")
    last_edited_on = models.DateField(default=timezone.now())

    indeed_link = models.CharField(max_length=255, default="/")
    dnb_link = models.CharField(max_length=255, default="/")
    glassdoor_link = models.CharField(max_length=255, default="/")
    google_link = models.CharField(max_length=255, default="/")

    searches = models.ManyToManyField(Search, related_name="companies")
    users_who_watchlisted = models.ManyToManyField(User, related_name="watchlisted_companies")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Job(models.Model):
    title = models.CharField(max_length=255)
    desc_short = models.CharField(max_length=255, default="")
    desc_long = models.TextField(default="")
    date_posted = models.CharField(max_length=255, default="30+ days ago")
    link = models.CharField(max_length=255, default="")

    searches = models.ManyToManyField(Search, related_name="jobs")

    company = models.ForeignKey(Company, related_name="jobs", on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Contact(models.Model):
    first_name = models.CharField(max_length=255, default="Unknown")
    last_name = models.CharField(max_length=255, default="Unknown")
    email = models.CharField(max_length=255, default="Unknown")
    linked_in = models.CharField(max_length=255, default="Unknown")
    department = models.CharField(max_length=255, default="Unknown")
    position = models.CharField(max_length=255, default="Unknown")
    notes = models.TextField(default="None")

    company = models.ForeignKey(Company, related_name="contacts", on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Note(models.Model):
    content = models.TextField(default="")

    user = models.ForeignKey(User, related_name="notes", on_delete=models.CASCADE)
    company = models.ForeignKey(Company, related_name="notes", on_delete=models.CASCADE)

    objects = NoteManager()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Comment(models.Model):
    content = models.TextField(default="")

    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    note = models.ForeignKey(Note, related_name="comments", on_delete=models.CASCADE)

    objects = CommentManager()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


