import os
import requests

from flask import redirect, render_template, request, session
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("moderator") is None:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function


def isadmin(mail):
    admin_list = ["hasanberkay@sabanciuniv.edu"]
    if mail in admin_list:
        return True
    return False


def mail_check(mail):
    print(mail)
    key = "@sabanciuniv.edu"
    print(mail.find(key), mail.rfind(key), mail[0:mail.find(key)], mail[mail.find(key):])
    if not mail.find(key) or mail.find(key) != mail.rfind(key) or not mail[0:mail.find(key)] or len(mail[mail.find(key):]) != 16:
        return False

    return True
