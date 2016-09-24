#!/usr/bin/env python

# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START imports]
import os
import urllib
import re

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import memcache

import jinja2
import webapp2

# code for sessions module
# http://webapp2.readthedocs.io/en/latest/_modules/webapp2_extras/sessions.html
from webapp2_extras import sessions

import xlrd
import datetime
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from models import User
from models import Team

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# webapp2 session configuration
# http://stackoverflow.com/questions/13421614/missing-configuration-keys-
# for-webapp2-extras-sessions-secret-key
config = {}

config['webapp2_extras.sessions'] = {
    'secret_key': 'some-secret-key',
}

# [END imports]
# os.path.dirname(__file__)
#jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
#    autoescape = True)

#DEFAULT_GUESTBOOK_NAME = 'Team Name'

# We set a parent key on the 'Audits' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.

# add handlers for easier write calls
class Handler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = JINJA_ENVIRONMENT.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    #get a session store for this request
    #http://webapp2.readthedocs.io/en/latest/_modules/webapp2_extras/appengine/sessions_memcache.html
    #http://stackoverflow.com/questions/33921819/using-sessions-with-webapp2-python
    def dispatch(self):
        self.session_store = sessions.get_store(request=self.request)

        try:
            #Dispatch the request
            webapp2.RequestHandler.dispatch(self)
        finally:
            #save all sessions
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()


# [START user]
class User(ndb.Model):
    """Sub model for representing a user."""
    #identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(required=True)
    team = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    #TODO: link Team to User
    team_img = ndb.StringProperty(required=True)

    @classmethod
    def by_name(cls, name):
        print '#### get by name =   %s' % name
        #u = User.all().filter('name =', name).get()
        u = User.gql("WHERE name = :name", name = name)
        result = u.get()
        return u

    @classmethod
    def by_email(cls, email):
        print '#### get by email =   %s' % email
        #u = User.all().filter('email =', email).get()
        u = User.gql("WHERE email = :email", email = email)
        result = u.get()
        return u

# [START main_page]
class MainPage(Handler):
    def get(self):
        user_email = self.session.get('email')

        print '#######user email = %s' % user_email

        # guestbook_name = self.request.get('guestbook_name',
        #                                   DEFAULT_GUESTBOOK_NAME)
        # audits_query = Audit.query(
        #     ancestor=guestbook_key(guestbook_name)).order(-Audit.date)
        # audits = audits_query.fetch(10)

        # user = users.get_current_user()

        #TODO: query audit entities
        audits = ''
        if user_email:
            #url = users.create_logout_url(self.request.uri)
            url = '/logout'
            url_linktext = 'Logout'

            #retrieve the User object from database
            u = User.by_email(user_email)
        else:
            #url = users.create_login_url(self.request.uri)
            url = '/login'
            url_linktext = 'Login'
            u = None

        self.render('index.html')
        self.render('header.html', user=u, url_linktext=url_linktext, url=url)
        self.render('content.html', user=u, audits=audits, url=url)

        upload_url = blobstore.create_upload_url('/upload')

        html_string = """
         <form action="%s" method="POST" enctype="multipart/form-data">
        Upload File:
        <input type="file" name="file"> <br>
        <input type="submit" name="submit" value="Submit">
        </form>""" % upload_url

        self.response.write(html_string)

# [END main_page]

# TODO: implement create Team Entity
# def CreateTeam(self, email, team_name):
#     t = Team.by_email(email)
#     # check if user already exists.

#     if u:
#         msg = 'User already registered.'
#         self.redirect('/')
#     else:
#         new_user = User(username=session_obj['username'],
#             email=session_obj['email'], picture=session_obj['picture'],
#             provider=session_obj['provider'],
#             provider_id=session_obj['provider_id'])
#         new_user.put()
#         user = getUserInfo(self, session_obj['email'])
#         #return user


# [START spreadsheet_import]

class Login(Handler):
    def get(self):
        self.render('login.html', user='', login_out='login')
        self.render('header.html', team_name='')

    def post(self):
        email = self.request.get('email')
        pwd = self.request.get('password')
        email_error, password_error = None, None

        # if login isn't in DB, redirect to signup page
        user = User.by_email(email)
        if not user:
            self.redirect('/signup')

        if not email:
            email_error = "Please use a valid e-mail address."

        #validate password
        #http://stackoverflow.com/questions/2990654/how-to-test-a-regex-password-in-python
        if not re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
            pwd_error1 = "Password must be alphanumeric and > 8 characters."

        if user.password != pwd:
            pwd_error2 = "Incorrect password."

        if (email_error or password_error):
            self.render("login.html", email=email,
                email_error=email_error, pwd_error1=password_error,
                pwd_error2=pwd_error2)
            self.render('header.html', user='', url='', login_out='login')
        else:
            self.session['email'] = email
            self.redirect("/")

class Signup(Handler):
    def get(self):
        self.render('signup.html', user='', login_out='login')
        self.render('header.html', team_name='')

    def post(self):
        username = self.request.get('username')
        email = self.request.get('email')
        password = self.request.get('password')
        team = self.request.get("team")
        #team_img = self.request.get("team_image")
        email_error, team_error, uname_error, pwd_error = '','','',''

        # user = User.by_email(email)
        # if user:
        #     user_error = "User account already exists"

        if not email:
            email_error = "Please use a valid email."

        if not team:
            team_error = "Please put a valid team name."

        if not username:
            uname_error = "Please enter a username."

        #validate password
        #http://stackoverflow.com/questions/2990654/how-to-test-a-regex-password-in-python
        if not re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
            pwd_error = "Please enter an alphanumeric password >= 8 characters long."

        if (email_error or team_error or uname_error or pwd_error):
            self.render("signup.html", username=username, email=email, team=team,
             uname_error=uname_error, team_error=team_error,
             email_error=email_error, pwd_error=pwd_error)
            self.render('header.html', team_img='', login_out='login')
        else:
            #create a new user
            self.session['email'] = email
            create_user(username, email, password, team, self.session)
            self.redirect('/')


def create_user(name, email, password, team_name, session_obj):
    u = User.by_email(email)

    print 'email here?  %s' % u

    # check if user already exists.
    if not u:
        new_user = User(name=name, password=password, email=email, team=team_name)
        new_user.put()

class Logout(Handler):
    def get(self):
        self.session['email'] = None
        self.redirect('/')

# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
    ('/signup', Signup),
    ('/login', Login),
    ('/logout', Logout),
    ('/upload', data.UploadHandler)
], debug=True, config=config)
# [END app]
